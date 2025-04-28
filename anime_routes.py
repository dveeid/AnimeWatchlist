from flask import Blueprint, render_template, current_app, request, session, jsonify, redirect, url_for
from urllib.parse import unquote, quote
import mysql.connector
import random
import logging
import datetime

anime_bp = Blueprint('anime', __name__)

def get_db_connection():
    conn = mysql.connector.connect(
        host=current_app.config['MYSQL_HOST'],
        database=current_app.config['MYSQL_DB'],
        user=current_app.config['MYSQL_USER'],
        password=current_app.config['MYSQL_PASSWORD']
    )
    return conn

@anime_bp.route('/random')
def random_anime():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT name FROM anime ORDER BY RAND() LIMIT 1")
        result = cursor.fetchone()
        if result:
            anime_name = quote(result['name'])
            return redirect(url_for('anime.anime_detail_by_name', name=anime_name))
        else:
            return "No anime found", 404
    finally:
        cursor.close()
        conn.close()

@anime_bp.route('/anime/<name>', methods=['GET'])
def anime_detail_by_name(name):
    decoded_name = unquote(name)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT anime.*, studios.name AS studio_name
            FROM anime
            JOIN studios ON anime.directed = studios.name
            WHERE anime.name = %s
        """, (decoded_name,))
        anime = cursor.fetchone()
        if anime:
            return render_template('anime_detail.html', anime=anime)
        else:
            return 'Anime not found', 404
    finally:
        cursor.close()
        conn.close()
        
@anime_bp.route('/anime/detail/<name>', methods=['GET'])
def anime_detail_by_url_name(name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        decoded_name = unquote(name)
        cursor.execute("""
            SELECT * FROM anime
            JOIN studios ON anime.directed = studios.name
            WHERE anime.name = %s
        """, (decoded_name,))
        anime = cursor.fetchone()
        if anime:
            return render_template('anime_detail.html', anime=anime)
        else:
            return 'Anime not found', 404
    finally:
        cursor.close()
        conn.close()

@anime_bp.route('/animes', methods=['GET'])
def display_anime_overview():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM anime ORDER BY reviewScore DESC LIMIT 80")
        popular_animes = cursor.fetchall()
        popular_slides = [popular_animes[i:i + 8] for i in range(0, len(popular_animes), 8)]


        cursor.execute("SELECT * FROM anime ORDER BY RAND() LIMIT 10")
        random_animes = cursor.fetchall()

        return render_template('animes.html', popular_slides=popular_slides, random_animes=random_animes)

    finally:
        cursor.close()
        conn.close()

@anime_bp.route('/animes/genre/<genreName>')
def animes_by_genre(genreName):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT a.name, a.imageURL, a.reviewScore
            FROM anime a
            JOIN animeHasGenre ahg ON a.name = ahg.animeName
            WHERE ahg.genreName = %s
        """, (genreName,))
        animes = cursor.fetchall()
        if not animes:
            message = "No animes found for this genre."
            return render_template('anime_list.html', animes=[], title=f"Animes in Genre: {genreName}", message=message)
        return render_template('anime_list.html', animes=animes, title=f"Animes in Genre: {genreName}")
    finally:
        cursor.close()
        conn.close()

@anime_bp.route('/animes/studio/<studioName>')
def animes_by_studio(studioName):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT a.name, a.imageURL, a.reviewScore
            FROM anime a
            WHERE a.directed = %s
        """, (studioName,))
        animes = cursor.fetchall()
        if not animes:
            message = "No animes found for this studio."
            return render_template('anime_list.html', animes=[], title=f"Animes by Studio: {studioName}", message=message)
        return render_template('anime_list.html', animes=animes, title=f"Animes by Studio: {studioName}")
    finally:
        cursor.close()
        conn.close()

@anime_bp.route('/search', methods=['GET'])
def search():
    search_query = request.args.get('query', '')
    if not search_query:
        return render_template('anime_list.html', message="Please enter a search query.")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT * FROM anime
            WHERE name LIKE %s OR summary LIKE %s
            ORDER BY reviewScore DESC
            LIMIT 20;
        """, ('%' + search_query + '%', '%' + search_query + '%'))
        animes = cursor.fetchall()

        if not animes:
            return render_template('anime_list.html', message="No animes found matching your search.")
        
        return render_template('anime_list.html', animes=animes, title=f"Search Results for '{search_query}'")
    finally:
        cursor.close()
        conn.close()
        
