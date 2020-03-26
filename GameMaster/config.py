import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secretkey'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEVICESERVER_UDP_PORT = 4000
    DEVICESERVER_TCP_PORT = 8000
    DEVICESERVER_USE_TCP_UPDATE = False
    DEVICESERVER_UDP_BUFFER = 256
    DEVICE_MASK = 0xDE00


class AlertConfig(object):
    ERROR_HTTP_LINK_FAILED = (0, 'Linking of device raised errors.')
    ERROR_HTTP_POLL_FAILED = (1, 'Raised errors on getting status.')