from flask import request
import datetime
from email.message import EmailMessage
import smtplib
import jwt
from functools import wraps
from flask import jsonify


token_dict = {}


def token_required(f):
    import app
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'access-token' in request.headers:
            short_token = request.headers.get('access-token')
        else:
            short_token = request.args.get('token')
        token = token_dict[int(short_token)]
        if not token:
            return jsonify(message='Token is missing!')
        try:
            data = jwt.decode(token, app.app.config['SECRET_KEY'])
        except:
            return jsonify(message='Token is invalid')

        return f(data['User'], *args, **kwargs)
    return decorated


def get_token(UserName):
    import app
    token = jwt.encode({'User': UserName, 'Exp': str(datetime.datetime.utcnow() + datetime.timedelta(seconds=600))},
                       app.app.config['SECRET_KEY'])
    return token


def activate_mail(Email, token_url, Name):
    EMAIL_ADDRESS = 'nishantsharma17121998@gmail.com'
    EMAIL_PASS = 'nishant5504'

    msg = EmailMessage()
    msg['Subject'] = 'Activate Account'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = Email
    msg.set_content(f"Hello {Name},\n Click the link to activate your account {token_url}")

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASS)
        smtp.send_message(msg)


def url_short(token):
    key = len(token_dict) + 1
    token_dict.__setitem__(key, token)
    return key



