from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    displayname = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    def __repr__(self):
        return '<User {}>'.format(self.username)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class PlayedGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    startstamp = db.Column(db.DateTime, index=True)
    endstamp = db.Column(db.DateTime, index=True)
    gametheme_id = db.Column(db.Integer, db.ForeignKey('gametheme.id'))
    gameresult_id = db.Column(db.Integer, db.ForeignKey('gameresult.id'))

class GameEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    gameeventtype_id = db.Column(db.Integer, db.ForeignKey('gameeventtype.id'))
    playedgame_id = db.Column(db.Integer, db.ForeignKey('playedgame.id'))

class GameResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)

class GameEventType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)

class GameTheme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)

class SystemConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
@login.user_loader
def load_user(idn):
    return User.query.get(int(idn))