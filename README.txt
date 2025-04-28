Anime Watchlist
======================
USAGE:
- Search
- Filter
- List
- Users & Admin Privledges
- Random Anime Selection
- View User Profile (login/logout)


REQUIREMENTS:
------------
- Web server with PHP support (e.g., Apache, Nginx)
- MySQL Server
- PHP 7.4 or higher
- Flask Framework for Python

INSTALLATION: 
------------
1. Clone the repository to your local machine or server.
   `git clone https://example.com/your-anime-website.git`
2. Navigate into the project directory.
   `cd your-anime-website`
3. Install dependencies.
   `pip install -r requirements.txt`
4. Set up your MySQL database and import the initial schema and data.
   `mysql -u username -p database_name < setup.sql`
5. Configure your server settings and database connection in `config.py`.
6. Start the Flask application.
   `flask run` or use `gunicorn` for production: `gunicorn -w 4 -b 0.0.0.0:8774 app:app`

