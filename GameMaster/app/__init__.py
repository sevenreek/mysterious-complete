from flask import Flask
from config import Config, AlertConfig
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from deviceserver import DevicesCommunicationServer

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
deviceServer = DevicesCommunicationServer(Config, AlertConfig)
from app import routes, models

if __name__ == "__main__":
    deviceServer.runThreaded()
    app.run()