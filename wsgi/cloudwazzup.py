#!/usr/bin/python

'''
Permission is hereby granted, free of charge, to any person obtaining a copy of this 
software and associated documentation files (the "Software"), to deal in the Software 
without restriction, including without limitation the rights to use, copy, modify, 
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to 
permit persons to whom the Software is furnished to do so, subject to the following 
conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR 
A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

'''
######### Cloud Wazzup 0.2 by monk 29/04/14 ######### 
Adding Whatsapp registration API

######### Cloud Wazzup 0.1 by monk 15/03/14 ######### 
This is a simple REST web service to send WhatsApp messages through API

The main goal is to be able to send push notifications/messages to mobiles indipendently of the platform (Android vs iOS)

This Web Service is not ment to be used/abused for any spamming/advertising etc. For this reason limitation on max number of messages per day is implemented
You should behave exactly as you do on your mobile WhatApp application. Be reponsible for what you send :)

This work is based on the great https://github.com/tgalal/yowsup library
Kudos to tgalal for the great work done to build the library
'''



import argparse, sys, os, csv
from Yowsup.Common.utilities import Utilities
from Yowsup.Common.debugger import Debugger
from Yowsup.Common.constants import Constants
from Examples.EchoClient import WhatsappEchoClient
from Yowsup.Registration.v2.existsrequest import WAExistsRequest as WAExistsRequestV2
from Yowsup.Registration.v2.coderequest import WACodeRequest as WACodeRequestV2
from Yowsup.Registration.v2.regrequest import WARegRequest as WARegRequestV2
from Yowsup.Contacts.contacts import WAContactsSyncRequest
import threading,time, base64
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask import request, Response
from flask import Flask, jsonify
from flask import json
from flask import redirect
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import time
import uuid
import flask

app = Flask(__name__)

#local DB
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cloudwazzup.db'

#production DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['OPENSHIFT_POSTGRESQL_DB_URL']

db = SQLAlchemy(app)

################################################################################################
#DB model
################################################################################################
MAX_WU_MEX = 100
IDENTITY= "0000000000000000"
API_VERSION = "0.2.2"

class User(db.Model):
    __tablename__ = 'cwusers'
    id = db.Column(db.Integer, primary_key=True)
    u_uid = db.Column(db.String(36), unique=True)            #user uuid
    u_created_at = db.Column(db.DateTime(timezone=False))    #user creation time
    u_name = db.Column(db.String(80), unique=True)           #user name
    u_passwd = db.Column(db.String(70))                      #user password
    u_email = db.Column(db.String(120), unique=True)         #user email
    wu_cc = db.Column(db.String(4))                          #phone sender country code
    wu_phone_number = db.Column(db.String(20), unique=True)  #phone sendr number without country code
    wu_passwd = db.Column(db.String(70))                     #whatsapp account password
    wu_max_mex_day = db.Column(db.Integer)                   #max mex  sent in a day
    wu_avail_mex_day = db.Column(db.Integer)                 #avail mex to send today
    wu_last_sent_mex_day = db.Column(db.Integer)             #day of the year of last sent mex
    wu_mex_sent = db.Column(db.Integer)                      #total number of sent mex


    def __init__(self, u_name, u_passwd, u_email, wu_cc, wu_phone_number, wu_passwd):
        self.u_uid = uuid.uuid4().hex
        self.u_created_at = datetime.now()
        self.u_name = u_name
        self.u_passwd = generate_password_hash(u_passwd)
        self.u_email = u_email
        self.wu_cc = wu_cc
        self.wu_phone_number = wu_phone_number
        self.wu_passwd = wu_passwd
        self.wu_max_mex_day = MAX_WU_MEX
        self.wu_avail_mex_day = MAX_WU_MEX
        self.wu_last_sent_mex_day = current_doy()
        self.wu_mex_sent = 0

    def __repr__(self):
        return '<User %r>' % self.u_name

################################################################################################
#Basic Auth
################################################################################################
def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """ 
    db_user = User.query.filter_by(u_name = username).first()
    if db_user is None:
        return False
    u_name = db_user.u_name
    u_passwd = db_user.u_passwd

    return username == u_name and check_password_hash(u_passwd, password)

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials\n', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

################################################################################################
#helpers
################################################################################################
def current_doy(): #current day of the year
    return datetime.now().strftime("%j")


def resultToString(result):
        unistr = str if sys.version_info >= (3, 0) else unicode
        out = []
        for k, v in result.items():
                if v is None:
                        continue
                out.append("%s: %s" %(k, v.encode("utf-8") if type(v) is unistr else v))

        return "\n".join(out)


def send_cwmex(wu_cc, wu_phone_number, wu_passwd, dst_phone, body_mex):
    countryCode = wu_cc
    login = wu_cc+wu_phone_number
    identity = IDENTITY
    password = wu_passwd

    identity = Utilities.processIdentity(identity)
    password = base64.b64decode(bytes(password.encode('utf-8')))
    phoneNumber = wu_phone_number
                    
    phone = dst_phone
    message = body_mex.encode('utf-8')

    wa = WhatsappEchoClient(phone, message, False)
    wa.login(login, password)


################################################################################################
#REST API
################################################################################################
@app.route('/')
def welcome():
    #return 'Welcome to CloudWhazzup'
    return redirect("https://github.com/mancusoa74/cloudwazzup", code=302)


@app.route('/cwuser/<string:u_uid>', methods=['GET']) #get a cloud wazzup user
@requires_auth
def get_user(u_uid):
    print(u_uid)
    user = User.query.filter_by(u_uid = u_uid).first()
    print(user)
    if user is None:
        return jsonify(error="Must provide a valid user uuid param"),415
    
    return jsonify(u_uid = user.u_uid,
                    u_created_at = user.u_created_at,
                    u_name = user.u_name,
                    u_email = user.u_email,
                    wu_cc = user.wu_cc,
                    wu_phone_number = user.wu_phone_number,
                    wu_passwd = user.wu_passwd,
                    wu_max_mex_day = user.wu_max_mex_day,
                    wu_avail_mex_day = user.wu_avail_mex_day,
                    api_version = API_VERSION), 200


@app.route('/cwuser', methods=['POST']) #register a cloud wazzup user
def register_user():
    #JSON onject for POST request
    #{"u_name": "user_name", "u_passwd": "1234","u_email": "user_name@domain.com","wu_cc": "39","wu_phone_number": "12345678","wu_passwd": "khfkwhfiowefwhenckjhsdcihj="}

    if request.headers['Content-Type'] == 'application/json':
        u_name = request.json.get('u_name')
        u_passwd = request.json.get('u_passwd')
        u_email = request.json.get('u_email')
        wu_cc = request.json.get('wu_cc')
        wu_phone_number = request.json.get('wu_phone_number')
        wu_passwd = request.json.get('wu_passwd')

        if u_name is None or u_passwd is None or u_email is None or wu_cc is None or wu_phone_number is None or wu_passwd is None:
            return jsonify(error="Must provide a cwuser JSON in data param"),400    

        try:                                        
            cwu = User(u_name=u_name,u_passwd=u_passwd,u_email=u_email,wu_cc=wu_cc,wu_phone_number=wu_phone_number,wu_passwd=wu_passwd)
            db.session.add(cwu)
            db.session.commit()
        except:
            return jsonify(error="Cannot create unique cwuser"),400

        return jsonify({ 'username': cwu.u_name, 'uuid': cwu.u_uid }), 201
    else:
        return jsonify(error="Must provide a cwuser JSON in data param"),415


@app.route('/cwuser/<string:u_uid>', methods=['PUT']) #update a cloud wazzup user
@requires_auth
def update_user(u_uid):
    #JSON onject for POST request
    #{"u_passwd": "1234","u_email": "user_name@domain.com","wu_cc": "39","wu_phone_number": "12345678","wu_passwd": "khfkwhfiowefwhenckjhsdcihj="}

    if request.headers['Content-Type'] == 'application/json':
        print(u_uid)
        user = User.query.filter_by(u_uid = u_uid).first()
        print(user)
        if user is None:
            return jsonify(error="Must provide a valid user uuid param"),415

        u_passwd = request.json.get('u_passwd')
        u_email = request.json.get('u_email')
        wu_cc = request.json.get('wu_cc')
        wu_phone_number = request.json.get('wu_phone_number')
        wu_passwd = request.json.get('wu_passwd')

        if u_passwd is not None:
            user.u_passwd = generate_password_hash(u_passwd)
        if u_email is not None:
            user.u_email = u_email
        if wu_cc is not None:
            user.wu_cc = wu_cc
        if wu_phone_number is not None:
            user.wu_phone_number = wu_phone_number
        if wu_passwd is not None:
            user.wu_passwd = wu_passwd

        try:                                        
            db.session.commit()
        except:
            return jsonify(error="Cannot update cwuser"),400

        return jsonify(u_uid = user.u_uid,
                    u_created_at = user.u_created_at,
                    u_name = user.u_name,
                    u_email = user.u_email,
                    wu_cc = user.wu_cc,
                    wu_phone_number = user.wu_phone_number,
                    wu_passwd = user.wu_passwd,
                    wu_max_mex_day = user.wu_max_mex_day,
                    wu_avail_mex_day = user.wu_avail_mex_day,
                    api_version = API_VERSION), 200
    else:
        return jsonify(error="Must provide a cwuser JSON in data param"),415

@app.route('/cwuser/<string:u_uid>', methods=['DELETE']) #delete a cloud wazzup user
@requires_auth
def delete_user(u_uid):
    print(u_uid)
    user = User.query.filter_by(u_uid = u_uid).first()
    if user is None:
        return jsonify(error="Must provide a valid user uuid param"),415            
    print(user)
    try:
        db.session.delete(user)
        db.session.commit()
    except:
        return jsonify(error="Cannot delete cwuser"),400
    return jsonify({ u_uid: 'deleted' }), 200


@app.route('/cwmex', methods=['POST'])
@requires_auth
def send():
    #JSON object for POST request
    #{"u_uid": "23809182309182309", "dst_phone": "391234567890","body_mex": "this is a test message"}
    if request.headers['Content-Type'] == 'application/json':
        u_uid = request.json.get('u_uid')
        dst_phone = request.json.get('dst_phone')
        body_mex = request.json.get('body_mex')

        user = User.query.filter_by(u_uid = u_uid).first()
        if user is None:
            return jsonify(error="Must provide a valid user uuid param"),415
            
        send_mex_day = current_doy()
        avail_mex_day = user.wu_avail_mex_day
        last_sent_mex_day = user.wu_last_sent_mex_day

        try:
            if avail_mex_day > 0:
                send_cwmex(user.wu_cc, user.wu_phone_number, user.wu_passwd, dst_phone, body_mex)
                user.wu_avail_mex_day -= 1
                user.wu_last_sent_mex_day = send_mex_day
                db.session.add(user)
                db.session.commit()
                return jsonify({ 'mex_status': 'sent', 'remaining_mex_for_today': user.wu_avail_mex_day }), 201
            else:
                if send_mex_day != last_sent_mex_day:
                    send_cwmex(user.wu_cc, user.wu_phone_number, user.wu_passwd, dst_phone, body_mex)
                    user.wu_avail_mex_day = user.wu_max_mex_day - 1
                    user.wu_last_sent_mex_day = send_mex_day
                    db.session.add(user)
                    db.session.commit()
                else:
                    return jsonify(error="No more available messages for today"),415
        except:
            return jsonify(error="Error in sending message"),400  
        return jsonify({ 'mex_status': 'sent', 'remaining_mex_for_today': user.wu_avail_mex_day }), 201
    else:
        return jsonify(error="Must provide a cwmex JSON in data param"),415

@app.route('/requestcode/<string:u_uid>', methods=['GET']) #request a SMS code from whatsapp
@requires_auth
def request_code(u_uid):
    user = User.query.filter_by(u_uid = u_uid).first()
    if user is None:
        return jsonify(error="Must provide a valid user uuid param"),415

    wu_cc = user.wu_cc
    wu_phone_number = user.wu_phone_number
    wu_identity = IDENTITY
    wu_method = "sms"

    print(wu_cc)
    print(wu_phone_number)
    print(wu_identity)
    print(wu_method)

    try:
        wc = WACodeRequestV2(wu_cc, wu_phone_number, wu_identity, wu_method)
        result = wc.send()
        print(resultToString(result))
    except:
        return jsonify(error="Error in requesting the sms code"),400
    return jsonify({ 'result': resultToString(result) }), 201

@app.route('/registercode', methods=['POST']) #request a SMS code from whatsapp
@requires_auth
def register_code():
    #JSON object for POST request
    #{"u_uid": "23809182309182309", "sms_code": "123-321"}
    if request.headers['Content-Type'] == 'application/json':
        u_uid = request.json.get('u_uid')
        user = User.query.filter_by(u_uid = u_uid).first()
        if user is None:
            return jsonify(error="Must provide a valid user uuid param"),415

        sms_code = request.json.get('sms_code')
        wu_cc = user.wu_cc
        wu_phone_number = user.wu_phone_number
        #wu_phone_number = wu_phone_number[-(len(wu_phone_number)-len(wu_cc)):]
        wu_identity = IDENTITY
        wu_code = sms_code
        wu_code = "".join(wu_code.split('-'))

        try:
            wr = WARegRequestV2(wu_cc, wu_phone_number, wu_code, wu_identity)
            result = wr.send()
            print(resultToString(result))
        except:
            return jsonify(error="Error in registering the sms code"),400
        return jsonify({ 'result': resultToString(result) }), 201



if __name__ == "__main__":
    #dev
    #app.debug = True
    #db.create_all()
    #app.run(host='0.0.0.0', port=3000)

    #production
    app.run()
