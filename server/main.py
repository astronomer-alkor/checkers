import logging
from hashlib import sha256

from flask import Flask, request, make_response

from server import db

logging.basicConfig(
    format="[%(levelname)s] %(message)s",
    level=logging.INFO
)

app = Flask(__name__)


def encrypt_password(password):
    return sha256(password.encode()).hexdigest()


@app.route('/user', methods=['PUT'])
def sign_up():
    if (user_name := request.args.get('name')) and (password := request.args.get('password')):
        if not db.select_user_by_name(user_name):
            password = encrypt_password(password)
            db.create_user(user_name, password)
            response = 'OK', 201
        else:
            response = 'Exists', 409
    else:
        response = 'Invalid name or password', 400

    return make_response(*response)


@app.route('/user', methods=['GET'])
def get_user():
    if (user_name := request.args.get('name')) and (password := request.args.get('password')):
        password = encrypt_password(password)
        if db.select_user(user_name, password):
            response = 'OK', 200
        else:
            response = 'Not exists', 404
    else:
        response = 'Invalid name or password', 400

    return make_response(*response)


if __name__ == '__main__':
    db.startup()
    app.run()
