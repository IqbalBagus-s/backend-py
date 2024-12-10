from flask import Flask
from flask_mysqldb import MySQL
from routes.all_routes import routes
from config import Config

app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = Config.DB_HOST
app.config['MYSQL_USER'] = Config.DB_USER
app.config['MYSQL_PASSWORD'] = Config.DB_PASSWORD
app.config['MYSQL_DB'] = Config.DB_NAME

# Initialize MySQL
mysql = MySQL(app)

# Register routes
app.register_blueprint(routes, url_prefix='/api')


if __name__ == '__main__':
    app.run(port=Config.PORT)
