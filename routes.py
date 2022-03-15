from flask_restful import Resource
from flask import request, jsonify, session, make_response
from model import Users
from Utils import url_short, get_token, activate_mail
import logging

# Creating custom logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('app.log')

# create formatters and aad it to handlers
file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_format)
file_handler.setLevel(logging.INFO)

# Add handlers to logger
logger.addHandler(file_handler)


class Logout(Resource):
    def get(self):
        user = session['Name']
        session['logged_in'] = False
        logger.info(f'{user} is logged out')
        return make_response(jsonify(message='Logged Out'), 200)


class Registration(Resource):
    def post(self):
        data_ = Users.objects()
        username = request.form.get('UserName')
        name = request.form.get('Name')
        email = request.form.get('Email')
        password1 = request.form.get('Password1')
        password2 = request.form.get('Password2')
        session['logged_in'] = False
        if not password2 == password1:
            return make_response(jsonify(message='Password1 and Password2 must be same'), 409)
        data = Users(UserName=username, Name=name, Email=email, Password=password1)
        for itr in data_:
            if itr.UserName == data.UserName:
                return make_response(jsonify(message='UserName Already Taken'), 409)
        data.save()
        logger.info(f'New user is registered by {username} username')
        token = get_token(username)
        short_token = url_short(token)
        token_url = r'http://127.0.0.1:90/activate?token='+f'{short_token}'
        activate_mail(email, token_url, name)
        return make_response(jsonify(message='User Created Check your registered Email to activate account'), 200)


class ForgetPass(Resource):
    def post(self):
        user_name = request.form.get('UserName')
        data_ = Users.objects(UserName=user_name).first()
        if not data_:
            return make_response(jsonify(message='User name not found!!'))
        email = data_.Email
        name = data_.Name
        logger.info(f'{user_name} has been forgotten his password')
        token = get_token(user_name)
        short_token = url_short(token)
        token_url = r'http://127.0.0.1:90/setpass?token='+f'{short_token}'
        activate_mail(email, token_url, name)
        logger.info(f'Mail is sent to registered mail id of user : {user_name} to set new password')
        return make_response(jsonify(message='Check your Registered Mail ID to set new Password.'))


class ChangePass(Resource):
    def post(self):
        if session['logged_in']:
            user_name = request.form.get('UserName')
            old_pass = request.form.get('Old Password')
            new_pass1 = request.form.get('New Password')
            new_pass2 = request.form.get('Re-Enter New Password')
            if new_pass1 == new_pass2:
                data_ = Users.objects(UserName=user_name).first()
                if old_pass == data_.Password:
                    data_.update(Password=new_pass1)
                    logger.info(f'{user_name} changed his password')
                    return make_response(jsonify(message='Your Password is Updated.'), 200)
                else:
                    return make_response(jsonify(message='Check Your old Password'), 409)
            else:
                return make_response(jsonify(message='Re-Entered Password must be equal to New_Password'), 409)
        else:
            return make_response(jsonify(message='You have to Login First'))


class Login(Resource):
    def post(self):
        if not session['logged_in']:
            user_name = request.form.get('UserName')
            password = request.form.get('Password')
            data_ = Users.objects(UserName=user_name).first()
            if data_:
                if password == data_.Password:
                    if not data_.Is_active:
                        logger.info(f'User: {user_name} tried to log in without activation of account')
                        token = get_token(data_.UserName)
                        short_token = url_short(token)
                        token_url = r'http://127.0.0.1:90/activate?token='+f'{short_token}'
                        activate_mail(data_.Email, token_url, data_.Name)
                        logger.info(f'Mail has been sent to registered mail id of user: {user_name} for activation of account')
                        return make_response(jsonify(message="Your account is not active yet Check your Registered Email to activate."))
                    session['logged_in'] = True
                    session['Name'] = data_.Name
                    logger.info(f'User: {user_name} logged in')
                    token = get_token(data_.UserName)
                    short_token = url_short(token)
                    return make_response(jsonify(message=f'Hello, {data_.Name}', token=short_token), 200)
                return make_response(jsonify(message='You have entered wrong Password'), 404)
            else:
                return make_response(jsonify(message='Entered User name not exist'))
        else:
            return make_response(jsonify(message=f"{session['Name']} is already logged in"), 409)


