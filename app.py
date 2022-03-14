from flask import Flask, jsonify, make_response, request, session
from flask_mongoengine import MongoEngine
from flask_restful import Api
from routes import Registration, Logout, Login, ChangePass, ForgetPass
import Utils
from model import Users


app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisisasecretkey'
api = Api(app)

# connecting with database
app.config['MONGODB_SETTINGS'] = {
    'db': 'Users',
}

db = MongoEngine(app)

# -----------------------------------------------API-----------------------------------------


@app.route('/', methods=['GET'])
@Utils.token_required
def home(user_name):
    data = Users.objects(UserName=user_name).first()
    return jsonify(message=f'Hello {data.Name}',UserName=f'{data.UserName}', Email=f'{data.Email}')


@app.route('/activate', methods=['GET'])
@Utils.token_required
def activate(user_name):
    data = Users.objects(UserName=user_name).first()
    data.update(Is_active=True)

    return make_response(jsonify(message="Your Account is Active.Now you can login"), 200)


@app.route('/setpass', methods=['POST'])
@Utils.token_required
def set_pass(user_name):
    data = Users.objects(UserName=user_name).first()
    password1 = request.form.get('New Password')
    password2 = request.form.get('Re-Enter Password')
    if password1 == password2:
        data.update(Password=password1)
        return make_response(jsonify(message='Your Password is Set Now you can Login'))
    return make_response(jsonify(message='You have to Re-Enter Same Password'))


# -------------------EndPoints---------------------------------
api.add_resource(Registration, '/Register')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
# api.add_resource(Home, '/home/<username>')
api.add_resource(ChangePass, '/changepass')
api.add_resource(ForgetPass, '/forgetpass')


if __name__ == "__main__":
    app.run(debug=True, port=90)
