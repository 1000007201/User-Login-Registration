from flask_restful import Resource
from flask import request, jsonify, session, make_response
from model import Users
from Utils import url_short, get_token, activate_mail


class Logout(Resource):
    def get(self):
        session['logged_in'] = False
        return make_response(jsonify(message='Logged Out'), 200)


class Registration(Resource):
    def post(self):
        data_ = Users.objects()
        UserName = request.form.get('UserName')
        Name = request.form.get('Name')
        Email = request.form.get('Email')
        Password1 = request.form.get('Password1')
        Password2 = request.form.get('Password2')
        session['logged_in'] = False
        if not Password2 == Password1:
            return make_response(jsonify(message='Password1 and Password2 must be same'), 409)
        data = Users(UserName=UserName, Name=Name, Email=Email, Password=Password1)
        for itr in data_:
            if itr.UserName == data.UserName:
                return make_response(jsonify(message='UserName Already Taken'), 409)
        data.save()
        token = get_token(UserName)
        short_token = url_short(token)
        token_url = r'http://127.0.0.1:90/activate?token='+f'{short_token}'
        activate_mail(Email, token_url, Name)
        return make_response(jsonify(message='User Created Check your registered Email to activate account'), 200)


# class Activate(Resource):
#     def get(self, UserName):
#


# class Home(Resource):
#     @token_required
#     def get(self, username):
#         if session['logged_in']:
#             return jsonify(message=f'Hello,{username} You Have a valid token...')
#         else:
#             return jsonify(message='You have to login')


class ForgetPass(Resource):
    def post(self):
        UserName = request.form.get('UserName')
        data_ = Users.objects(UserName=UserName).first()
        Email = data_.Email
        Name = data_.Name
        token = get_token(UserName)
        short_token = url_short(token)
        token_url = r'http://127.0.0.1:90/setpass?token='+f'{short_token}'
        activate_mail(Email, token_url, Name)
        return make_response(jsonify(message='Check your Registered Mail ID to set new Password.'))


class ChangePass(Resource):
    def post(self):
        if session['logged_in']:
            UserName = request.form.get('UserName')
            old_pass = request.form.get('Old Password')
            new_pass1 = request.form.get('New Password')
            new_pass2 = request.form.get('Re-Enter New Password')
            if new_pass1 == new_pass2:
                data_ = Users.objects(UserName=UserName).first()
                if old_pass == data_.Password:
                    data_.update(Password=new_pass1)
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
            UserName = request.form.get('UserName')
            Password = request.form.get('Password')
            data_ = Users.objects(UserName=UserName).first()
            if data_:
                if Password == data_.Password:
                    if not data_.Is_active:
                        token = get_token(data_.UserName)
                        short_token = url_short(token)
                        token_url = r'http://127.0.0.1:90/activate?token='+f'{short_token}'
                        activate_mail(data_.Email, token_url, data_.Name)
                        return make_response(jsonify(message="Your account is not active yet Check your Registered Email to activate."))
                    session['logged_in'] = True
                    session['Name'] = data_.Name
                    token = get_token(data_.UserName)
                    short_token = url_short(token)
                    return make_response(jsonify(message=f'Hello, {data_.Name}', token=short_token), 200)
                return make_response(jsonify(message='You have entered wrong Password'), 404)
        else:
            return make_response(jsonify(message=f"{session['Name']} is already logged in"), 409)

