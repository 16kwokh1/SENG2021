from datetime import datetime, timedelta
import hashlib
import jwt
import random
import re
import requests
from urllib.parse import urlparse


# Functions from other files are imported for writing errors and saving data
from errors import AccessError
from instance import (user_list, jwt_tokens, channel_list,
message_list)

class auth_helper:

    # Define a hashing secret
    secret = 'BananaPie'

    # Generate alphanumeric string according to length
    def random(string_length):

        # Define an aplhabet
        ALPHABET = ('0123456789abcdefghijklmnopqrstuvwxyz'
                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ')

        # Create a random list of characters
        chars=[]
        for i in range(string_length):
            chars.append(random.choice(ALPHABET))

        # Return the list as a string
        return ''.join(chars)

    # Encrypt a string with sha256
    def sha_256(password):

        # Encrypt and return
        return hashlib.sha256(password.encode()).hexdigest()

    # Check that an email is valid
    def email_check(check_email):

        # Given email check structure
        regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'

        # Check if an email is already in use
        if re.search(regex,check_email):
            for user in user_list:
                if user.get_email() == check_email:
                    # Return email already used error
                    return -1
            # Return success
            return 1
        else:
            # Invalid email error
            return 0

    # Check that a password is valid
    def password_check(check_password):

        # Check that the password has a valid length
        if len(check_password) < 6:
            # Return length error
            return 0

        # Check that the password contains valid ASCII characters
        if (all(ord(c) < 127 for c in check_password) and
            all(ord(c) > 31 for c in check_password)):
            # Return success
            return 1
        else:
            # Return invalid password error
            return -1

    # Check that a first or last name is valid
    def name_check(check_name):

        # Check that the length is valid
        if len(check_name) > 50 or len(check_name) < 1:
            # Return invalid length error
            return 0
        else:

            return 1

    # Check that a handle is valid
    def handle_check(check_handle):

        # Check that the length is valid
        if 3 <= len(check_handle) <= 20:
            # Return success
            return 1
        else:
            # Return invalid length error
            return 0

    # Check that a handle is not taken
    def is_handle_taken(handle_str):

        # Loop through each user and check their handle against the given one
        for user in user_list:
            if user.get_handle() == handle_str:
                # Return handle is taken error
                return 0

        # Return success
        return 1

    # Generate a valid handle
    def generate_handle(firstname, lastname):

        # First, generate a handle based on the first and last name
        first_handle = (firstname.strip() + lastname.strip()).lower()
        first_handle = first_handle[:20]
        handle = first_handle

        # If handle is taken, add integers to the end of the handle until it
        # is unique
        counter = 0
        while auth_helper.is_handle_taken(handle) == 0:
            if len(first_handle) + len(str(counter)) > 20:
                replace = len(first_handle) - len(str(counter))
                handle = first_handle[:replace] + str(counter)
            else:
                handle = first_handle + str(counter)
            counter += 1

        # Return valid handle
        return handle

    # Create a token for the user and add to jwt_tokens list
    def activate_user(u_id):

        # Create payload
        payload = {
            'u_id' : u_id,
            # Tokens have a 24 hour expiry
            'exp' : datetime.utcnow() + timedelta(hours = 24)
        }

        # Encode a token
        new_token = jwt.encode(payload, auth_helper.secret,
                               algorithm = 'HS256')

        # Revoke the current instance of user if present
        for token in jwt_tokens:
            try:
                check_payload = auth_helper.decode_jwt(token)
                if check_payload['u_id'] == u_id:
                    jwt_tokens.remove(token)
                    break
            except ValueError:
                pass

        # Add the token to  the list as a string
        new_token_str = new_token.decode('utf-8')
        jwt_tokens.append(new_token_str)

        # Return the token
        return new_token_str

    # Decode the token
    def decode_jwt(token):

        # Return the payload unless there is an error
        try:
            payload = (jwt.decode(bytes(token, 'utf-8'), auth_helper.secret,
                       algorithms = ['HS256']))
            return payload

        except Exception:
            raise ValueError('Token is invalid')

    # Find all expired tokens and remove them
    def check_all_tokens():

        # Check each token in the list
        for token in jwt_tokens:
            try:
                payload = auth_helper.decode_jwt(token)
            except Exception:
                jwt_tokens.remove(token)

    # Checks if the given token is in the jwt_tokens list
    def is_token_valid(token):

        # Remove expired tokens
        auth_helper.check_all_tokens()

        # Check each token in the list
        try:
            payload = auth_helper.decode_jwt(token)
            for user in jwt_tokens:
                if user == token:
                    # Token found
                    return True
            # Could not find valid token
            return False
        except Exception:
            # Token invalid
            return False

    # Get a u_id given a token
    def active_token_to_uid(token):

        # Decode the token
        payload = auth_helper.decode_jwt(token)

        # Return the u_id
        return payload['u_id']

    # Check if a u_id is valid
    def is_uid_valid(u_id):

        # If u_id is less than 0, it is automatically invalid
        if u_id < 0:
            return False

        # Get the associated user unless u_id is out of range
        try:
            user = user_list[u_id]
        except IndexError:
            return False

        # Check that the user's id is the given u_id
        if user.get_u_id() == u_id:
            return True
        else:
            return False

    # Check if the user is a Slackr admin
    def is_uid_slackr_admin(u_id):

        # If u_id is less than 0, it is automatically invalid
        if u_id < 0:
            raise ValueError('u_id is invalid')

        # Get the associated user unless u_id is out of range
        try:
            user = user_list[u_id]
        except IndexError:
            raise ValueError('u_id is invalid')

        # Check permissions unless the u_id is invalid
        if user.get_u_id() == u_id:
            if user.get_user_perms() == 1 or user.get_user_perms() == 2:
                return True
            else:
                return False
        else:
            raise ValueError('u_id is invalid')

    # Get the user's name given a u_id
    def uid_to_name(u_id):

        # If u_id is less than 0, it is automatically invalid
        if u_id < 0:
            raise ValueError('u_id is invalid')

        # Get the associated user unless u_id is out of range
        try:
            user = user_list[u_id]
        except IndexError:
            raise ValueError('u_id is invalid')

        # Return full name unless the u_id is invalid
        if user.get_u_id() == u_id:
            name = user.get_name_first() + ' ' + user.get_name_last()
            return name
        else:
            raise ValueError('u_id is invalid')

    # Get the user's first name given a u_id
    def uid_to_first_name(u_id):

        # If u_id is less than 0, it is automatically invalid
        if u_id < 0:
            raise ValueError('u_id is invalid')

        # Get the associated user unless u_id is out of range
        try:
            user = user_list[u_id]
        except IndexError:
            raise ValueError('u_id is invalid')

        # Return first name unless the u_id is invalid
        if user.get_u_id() == u_id:
            return user.get_name_first()
        else:
            raise ValueError('u_id is invalid')

    # Get the user's last name given a u_id
    def uid_to_last_name(u_id):

        # If u_id is less than 0, it is automatically invalid
        if u_id < 0:
            raise ValueError('u_id is invalid')

        # Get the associated user unless u_id is out of range
        try:
            user = user_list[u_id]
        except IndexError:
            raise ValueError('u_id is invalid')

        # Return last name unless the u_id is invalid
        if user.get_u_id() == u_id:
            return user.get_name_last()
        else:
            raise ValueError('u_id is invalid')

# A class of functions for helping with errors
class error_helper:

    # Correctly format an error
    def error_to_dictionary(e):

        # Format as required
        error = {
            'code' : 400,
            'name' : str(type(e).__name__),
            'message' : str(e)
        }

        # Return correctly formatted  error
        return error