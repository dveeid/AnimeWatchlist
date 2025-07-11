import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret-key')

    # MySQL (Railway) configuration
    MYSQL_HOST = os.environ.get('MYSQLHOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQLPORT', 3306))
    MYSQL_USER = os.environ.get('MYSQLUSER')
    MYSQL_PASSWORD = os.environ.get('MYSQLPASSWORD')
    MYSQL_DB = os.environ.get('MYSQLDATABASE')
