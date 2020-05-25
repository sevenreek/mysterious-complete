from app import app, deviceServer
from flask import render_template, flash, redirect, url_for, request, abort, send_from_directory
from app.forms import LoginForm
from flask_login import current_user, logout_user, login_user, login_required
from app.models import User
from werkzeug.urls import url_parse
import json
from unittest import mock
from deviceserver import Room, RoomOverviewEncoder
from run import CK_DEVICE_SERVER
@app.route('/')
@app.route('/index')
def index():
    user = {'displayname' : 'Pracownik #01'}
    devicesList = [device.getBasicStatusDictionary() for device in app.config[CK_DEVICE_SERVER].detectedDevices]
    return render_template('dashboard.html', title='Home', user=user, devices=devicesList)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/room/raw')
def list_rooms_raw():
    return json.dumps(app.config[CK_DEVICE_SERVER].detectedDevices, cls=RoomOverviewEncoder)

@app.route('/room/<int:index>/raw')
def room_details_raw(index):
    return "raw details about device " + index

@app.route('/room/<int:index>')
def room_details(index):
    return "details about device " + index

@app.route('/room/<int:index>/<path:command>')
def pass_command_to_room(index, command):
    deviceServer.sendCommand(index, command)
    return ''

@app.route('/js/<path:path>')
def send_static_js(path):
    return send_from_directory('js', path)

@app.route('/css/<path:path>')
def send_static_css(path):
    return send_from_directory('css', path)

@app.route('/vendor/<path:path>')
def send_static_vendor(path):
    return send_from_directory('vendor', path)
