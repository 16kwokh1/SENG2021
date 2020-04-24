# Relevant python libraries are imported
from datetime import datetime
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from flask_mail import Mail, Message
from json import dumps
import sys
from werkzeug.exceptions import HTTPException
from datetime import datetime

# All necessary functions from other files are imported
from authentication import (auth_login, auth_logout, auth_register,
auth_passwordreset_request, auth_passwordreset_reset)


# Default error handler for the frontend
def defaultHandler(err):

    response = err.get_response()
    response.data = dumps({
        'code': err.code,
        'name': 'System Error',
        'message': err.description,
    })
    response.content_type = 'application/json'

    return response

# A custom ValueError is defined here
class ValueError(HTTPException):
    code = 400
    message = 'No message specified'

# Setup the flask server
APP = Flask(__name__, static_url_path = '/static')

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)
CORS(APP)

# Configure the flask server with a gmail account
APP.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'w15bbananapie@gmail.com',
    MAIL_PASSWORD = 'SallyBob'
)

# Simple echo function for a GET method
@APP.route('/echo/get', methods = ['GET'])
def echo1():

    return dumps({
        'echo' : request.args.get('echo'),
    })

# Simple echo function for a POST method
@APP.route('/echo/post', methods = ['POST'])
def echo2():

    return dumps({
        'echo' : request.form.get('echo'),
    })

# Server function to handle /auth/login request
@APP.route('/auth/login', methods = ['POST'])
def server_auth_login():

    # Get input from frontend
    email = request.form.get('email')
    password = request.form.get('password')

    # Execute auth_login() catching any errors that may be raised
    try:
        u_id, token = auth_login(email, password)
    except Exception as e:
        raise ValueError(description = str(e))

    # Format the return data to be read by the frontend
    data = {'u_id' : u_id, 'token' : token}

    # Return this data
    return dumps(data)

# Server function to handle /auth/logout request
@APP.route('/auth/logout', methods = ['POST'])
def server_auth_logout():

    # Get input from frontend
    token = request.form.get('token')

    # Execute auth_logout() catching any errors that may be raised
    try:
        is_success = auth_logout(token)
    except Exception as e:
        raise ValueError(description = str(e))

    # Format the return data to be read by the frontend
    data = {'is_success' : is_success}

    # Return this data
    return dumps(data)

# Server function to handle /auth/register request
@APP.route('/auth/register', methods = ['POST'])
def server_auth_register():

    # Get input from frontend
    email = request.form.get('email')
    password = request.form.get('password')
    name_first = request.form.get('name_first')
    name_last = request.form.get('name_last')

    # Execute auth_register() catching any errors that may be raised
    try:
        u_id, token = auth_register(email, password, name_first, name_last)
    except Exception as e:
        raise ValueError(description = str(e))

    # Format the return data to be read by the frontend
    data = {'u_id' : u_id, 'token' : token}

    # Return this data
    return dumps(data)

# Server function to handle /auth/passwordreset/request request
@APP.route('/auth/passwordreset/request', methods = ['POST'])
def server_auth_passwordreset_request():

    # Get input from frontend
    email = request.form.get('email')

    # Execute auth_passwordreset_request() catching any errors that may be
    # raised
    try:
        reset_code = auth_passwordreset_request(email)
    except Exception as e:
        raise ValueError(description = str(e))

    mail = Mail(APP)

    # Send an email containing the reset code to the user unless there is an
    # error
    try:
        msg = Message('Slackr Reset Password Request',
            sender = 'w15bbananapie@gmail.com',
            recipients = [email])
        msg.body = str(reset_code)
        mail.send(msg)
    except Exception as e:
        raise ValueError(description = 'Email sent failed')

    # Return empty
    return dumps({})

# Server function to handle /auth/passwordreset/reset request
@APP.route('/auth/passwordreset/reset', methods = ['POST'])
def server_auth_passwordreset_reset():

    # Get input from frontend
    reset_code = request.form.get('reset_code')
    new_password = request.form.get('new_password')

    # Execute auth_passwordreset_reset() catching any errors that may be raised
    try:
        auth_passwordreset_reset(reset_code, new_password)
    except Exception as e:
        raise ValueError(description = str(e))

    # Return empty
    return dumps({})

# Server function to handle /admin/userpermission/change request
@APP.route('/admin/userpermission/change', methods = ['POST'])
def server_admin_userpermission_change():

    # Get input from frontend
    token = request.form.get('token')
    u_id = request.form.get('u_id')
    permission_id = request.form.get('permission_id')

    # Check correct input type
    try:
        u_id = int(u_id)
    except Exception:
        raise TypeError('Input error!')

    # Check correct input type
    try:
        permission_id = int(permission_id)
    except Exception:
        raise TypeError('Input error!')

    # Execute admin_userpermission_change() catching any errors that may be
    # raised
    try:
        admin_userpermission_change(token, u_id, permission_id)
    except Exception as e:
        raise ValueError(description = str(e))

    # Return empty
    return dumps({})

# Serve the static images
@APP.route('/static/<path:path>')
def send_file(filename):

    # Return the correct image URL
    return send_from_directory(APP.static_url_path + '/' + path, path)


# Run the flask server here
if __name__ == '__main__':

    #reset_all()

    # Run the server
    APP.run(port = (sys.argv[1] if len(sys.argv) > 1 else 5000), debug = False)
