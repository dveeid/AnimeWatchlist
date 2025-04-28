from flask import Flask, request, render_template, redirect, url_for, session, jsonify
import mysql.connector
import hashlib
from profile_routes import profile_bp
from anime_routes import anime_bp
import config


app = Flask(__name__, static_folder='static')
app.config.from_object(config.Config)
app.secret_key = 'your_secret_key'

def get_db_connection():
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        database=app.config['MYSQL_DB'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD']
    )

def getUserLists():
    if 'username' not in session:
        return None, None 

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT GetListIDs(%s) AS list_ids;", (username,))
        result = cursor.fetchone()
        if result:
            list_ids = result[0]
            parts = list_ids.split(',')
            watchID = parts[0].split(': ')[1]
            prevID = parts[1].split(': ')[1]
            return prevID, watchID
        else:
            return None, None  # No IDs found
    except mysql.connector.Error as err:
        print(f"Error retrieving list IDs: {err}")
        return None, None
    finally:
        cursor.close()
        conn.close()
    
@app.route('/')
def index():
    if 'username' in session:
        return render_template('animes.html')
    else:
        notification = request.args.get('notification', None)
        return render_template('login.html', notification=notification)
    
@app.route('/login', methods=['POST'])
def login():
    user_input = request.form['username']
    password = request.form['password']
    hashed_password = hashlib.md5(password.encode()).hexdigest()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM user WHERE username = %s OR email = %s", (user_input, user_input))
    result = cursor.fetchone()
    if result and result[1] == hashed_password:
        session['username'] = result[0]
        return render_template('profile.html')
    else:
        return redirect(url_for('index', notification='login_error'))

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    hashed_password = hashlib.md5(password.encode()).hexdigest()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO user (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
        conn.commit()
        
        cursor.callproc('CreateAndAssignLists', [username])
        conn.commit()
        
        return redirect(url_for('index', notification='signup_success'))
    except mysql.connector.Error as err:
        return 'Signup Failed: ' + str(err)

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/animes')
def animes():
    if 'username' not in session:
        return redirect(url_for('index', notification='Please log in to view this page'))
    return render_template('animes')

@app.route('/filters')
def filters():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch genre data with anime counts
    cursor.execute("""
        SELECT g.genreName, COUNT(ahg.animeName) AS animeCount
        FROM genre g
        LEFT JOIN animeHasGenre ahg ON g.genreName = ahg.genreName
        GROUP BY g.genreName
        ORDER BY g.genreName
        LIMIT 100;
    """)
    genres = cursor.fetchall()

    # Fetch studio data with anime counts
    cursor.execute("""
        SELECT s.name, COUNT(a.name) AS animeCount
        FROM studios s
        LEFT JOIN anime a ON s.name = a.directed
        GROUP BY s.name
        ORDER BY s.name
        LIMIT 100;
    """)
    studios = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('filters.html', genres=genres, studios=studios)

@app.route('/categories')
def categories():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch genre data
    cursor.execute("""
        SELECT g.genreName, COUNT(ahg.animeName) AS animeCount
        FROM genre g
        LEFT JOIN animeHasGenre ahg ON g.genreName = ahg.genreName
        GROUP BY g.genreName;
    """)
    genres = cursor.fetchall()
    
    # Fetch studio data
    cursor.execute("""
        SELECT s.name, COUNT(a.name) AS animeCount
        FROM studios s
        LEFT JOIN anime a ON s.name = a.directed
        GROUP BY s.name;
    """)
    studios = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('categories.html', genres=genres, studios=studios)

@app.route('/add_anime_to_list', methods=['POST'])
def add_anime_to_list():
    conn = get_db_connection()
    cursor = conn.cursor()
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 403

    data = request.get_json()
    anime_name = data.get('animeName')
    list_type = data.get('listType')  # Expects 'watchList' or 'previouslyWatched'

    if not anime_name or not list_type:
        return jsonify({'success': False, 'message': 'Missing anime name or list type'}), 400

    

    try:
        # Get the list ID from the user's watchList or previouslyWatched
        cursor.execute("SELECT watchList, previouslyWatched FROM user WHERE username = %s", (session['username'],))
        result = cursor.fetchone()
        if result is None:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        list_id = result[0] if list_type == 'watchList' else result[1]

        # Check if the anime exists
        cursor.execute("SELECT name FROM anime WHERE name = %s", (anime_name,))
        if cursor.fetchone() is None:
            return jsonify({'success': False, 'message': 'Anime not found'}), 404

        # Insert into animeListItem
        cursor.execute("INSERT INTO animeListItem (listIndex, listID, animeName) VALUES (%s, %s, %s)", (0, list_id, anime_name))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({'success': False, 'message': f"Database error: {err}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({'success': True, 'message': f"Anime '{anime_name}' added to {list_type} successfully"})


@app.route('/users')
def users():
    if session.get('username') != 'admin':
        return redirect(url_for('index', notification='Unauthorized access'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user LIMIT 10")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('users.html', users=users)

@app.route('/profile/<username>')
def profile(username):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        return render_template('user_profile.html', user=user)
    else:
        return 'User not found', 404
    
@app.route('/lists')
def lists():
    if 'username' not in session:
        return redirect(url_for('index', notification='Please log in to view this page'))
    
    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Fetch Watchlist
        cursor.execute("""
            SELECT a.* FROM anime a
            JOIN animeListItem ali ON a.name = ali.animeName
            JOIN animeList al ON ali.listID = al.id
            JOIN user u ON al.id = u.watchList
            WHERE u.username = %s;
        """, (username,))
        watchlist_animes = cursor.fetchall()
        
        # Fetch Previously Watched
        cursor.execute("""
            SELECT a.* FROM anime a
            JOIN animeListItem ali ON a.name = ali.animeName
            JOIN animeList al ON ali.listID = al.id
            JOIN user u ON al.id = u.previouslyWatched
            WHERE u.username = %s;
        """, (username,))
        prev_watched_animes = cursor.fetchall()
        
    finally:
        cursor.close()
        conn.close()
    
    return render_template('lists.html', watchlist_animes=watchlist_animes, prev_watched_animes=prev_watched_animes, title='My Lists')


app.register_blueprint(profile_bp, url_prefix='/profile')
app.register_blueprint(anime_bp, url_prefix='/anime')

@app.errorhandler(404)
def not_found(error):
    if 'username' not in session:
        return redirect(url_for('index', notification='Please log in to view this page'))

if __name__ == '__main__':
    app.run(debug=True, port=5008)