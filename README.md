# Anime Watchlist

A Flask-based web application for tracking and discovering anime shows.

## Features

- Search and filter anime database
- Create and manage personal watchlists
- User profiles with login/logout functionality
- Admin privileges for content management
- Random anime recommendation feature

## Requirements

- Web server with Python support
- MySQL Server
- Python 3.x
- Flask Framework

## Installation

1. Clone the repository to your local machine or server.
   ```bash
   git clone https://github.com/AdoniasDaniel/AnimeWatchlist.git
   ```
   
2. Navigate into the project directory.
   ```bash
   cd AnimeWatchlist
   ```
   
3. Install dependencies.
   ```bash
   pip install -r requirements.txt
   ```
   
4. Set up your MySQL database and import the initial schema and data.
   ```bash
   mysql -u username -p database_name < schema.sql
   mysql -u username -p database_name < instance.sql
   ```
   
5. Configure your server settings and database connection in `config.py`.

6. Start the Flask application.
   ```bash
   flask run
   ```
   Or use `gunicorn` for production:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

## Documentation

The `AnimeDBPhase4.pdf` file contains comprehensive documentation on the database design and application architecture. 