from flask import Flask, jsonify, request, make_response
from flask_mongoengine import MongoEngine
from flask_restful import Api, Resource
from routes import ForgetPass, ChangePass, Login, Registration, Logout, logger
from model import Users
from Utils import token_required


app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisisasecretkey'
api = Api(app)


# connecting with database
app.config['MONGODB_SETTINGS'] = {
    'db': 'Users',
}

db = MongoEngine(app)

# -----------------------------------------------API-----------------------------------------


class Home(Resource):
    @token_required
    def get(user_name):
        data = Users.objects(UserName=user_name).first()
        logger.info(f'User: {user_name} has accessed home page')
        return jsonify(message=f'Hello {data.Name}', UserName=f'{data.UserName}', Email=f'{data.Email}')


class Activate(Resource):
    @token_required
    def get(user_name):
        data = Users.objects(UserName=user_name).first()
        data.update(Is_active=True)
        logger.info(f'User: {user_name} activated his account')

        return make_response(jsonify(message="Your Account is Active.Now you can login"), 200)


class SetPass(Resource):
    @token_required
    def post(user_name):
        data = Users.objects(UserName=user_name).first()
        try:
            password1 = request.form.get('New Password')
            password2 = request.form.get('Re-Enter Password')
        except:
            return make_response(jsonify(message='Password1 and Password2 can not be empty'))
        if password1 == password2:
            data.update(Password=password1)
            logger.info(f'User: {user_name} has updated his password by forgot password')
            return make_response(jsonify(message='Your Password is Set Now you can Login'))
        return make_response(jsonify(message='New Password and Re-Enter Password must be same'))


# -------------------EndPoints---------------------------------

api.add_resource(Registration, '/Register')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(Home, '/')
api.add_resource(ChangePass, '/changepass')
api.add_resource(ForgetPass, '/forgetpass')
api.add_resource(Activate, '/activate')
api.add_resource(SetPass, '/setpass')


if __name__ == "__main__":
    app.run(debug=True, port=90)
