from datetime import datetime, timedelta
import random
import re
from flask import request
from urllib.parse import urlparse

from errors import AccessError
from classes import User, ResetCode
from helper import auth_helper
from instance import user_list, jwt_tokens, reset_password_list

def auth_login(email, password):

    # Regex string to ensure that the entered email is valid
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'

    # Removes expired tokens
    auth_helper.check_all_tokens()

    # Check that the email is valid
    if(re.search(regex,email)):
        # Check that the email belongs to a user in user_list
        for user in user_list:
            if user.get_email() == email:
                # Activate the user and return a u_id and token if the given
                # password matches the user's account
                if (user.get_hashed_password() ==
                    auth_helper.sha_256(user.get_salt() + password)):
                    token = auth_helper.activate_user(user.get_u_id())
                    return user.get_u_id(), token

                else:
                    raise ValueError('Password is incorrect')

        # If the program reaches this line, the email has not been found
        raise ValueError('Email entered does not belong to a user')

    # Raise an error if the email is not valid
    else:
        raise ValueError('Email entered is not a valid email')

def auth_logout(token):

    # Check that the given token is valid
    if not auth_helper.is_token_valid(token):
        return False

    # Search for the associated user in the list of jwt_tokens
    if token in jwt_tokens:
        # Remove this token once found and clean up the list
        jwt_tokens.remove(token)
        auth_helper.check_all_tokens()
        return True

    # If the program reaches this line, the user has not been found
    # Clean up remaining tokens in the list and return false
    auth_helper.check_all_tokens()
    return False

def auth_register (email, password, name_first, name_last):

    # Check that the given email address is valid and does not already belong
    # to another user
    if auth_helper.email_check(email) == 0:
        raise ValueError('Invalid email')
    elif auth_helper.email_check(email) == -1:
        raise ValueError('Email already used by another user')

    # Check that the given password is an appropriate length and only
    # contains standard ASCII-standard characters
    if auth_helper.password_check(password) == 0:
        raise ValueError('Password cannot be less than 6 characters')
    elif auth_helper.password_check(password) == -1:
        raise ValueError('Password must be ASCII-standard characters only')

    # Check that the given first and last names are an appropriate length
    if auth_helper.name_check(name_first) == 0:
        raise ValueError('First name has invalid length')
    if auth_helper.name_check(name_last) == 0:
        raise ValueError('Last name has invalid length')

    # Generate u_id and salt
    new_user_id = len(user_list)
    salt = auth_helper.random(16)

    # Generate a new user_profile dictionary based on the given data
    # During this process, the handle is generated and password is hashed

    new_user_profile = User (
        u_id = new_user_id,
        email = email,
        name_first = name_first.strip(),
        name_last = name_last.strip(),
        handle = auth_helper.generate_handle(name_first, name_last),
        salt = salt,
        hashed_password = auth_helper.sha_256(salt+password),
        user_perms = 3
    )

    if new_user_id == 0:
        new_user_profile.set_user_perms(2)
    elif new_user_id == 1:
        new_user_profile.set_user_perms(1)

    # Remove any expired tokens
    auth_helper.check_all_tokens()

    # Add the newly registerd user to the user_list and log them in by
    # generating and activating a new token
    user_list.append_json(new_user_profile.get_json())
    token = auth_helper.activate_user(new_user_id)

    # Save all data and return the u_id and token
    user_list.save()
    return new_user_id, token

def auth_passwordreset_request(email):

    # Check that the email belongs to a user in user_list
    for user in user_list:
        if user.get_email() == email:
            # If the user has requested 5 or more resets today, prevent request
            if user.get_reset_attempts() >= 5:
                if (datetime.now() >
                    user.get_reset_time() + timedelta(hours=24)):
                    user.set_reset_attempts(0)
                else:
                    raise ValueError('There have been too many requests to'
                                     'reset password, please try again'
                                     'tomorrow')

            # Generate an 8 digit alpha-numeric reset code
            new_reset_code = auth_helper.random(8)

            # Ensure that this new code is unique
            while True:
                reset_code_matched = False
                for reset_user in reset_password_list:
                    # Keep randomising the reset code until it is unique
                    if reset_user.get_reset_code() == new_reset_code:
                        new_reset_code = auth_helper.random(8)
                        reset_code_matched = True
                        break
                if not reset_code_matched:
                    break

            # Replace the existing reset code if this is not the first request
            reset_user_matched = False
            for reset_user in reset_password_list:
                if reset_user.get_reset_u_id() == user.get_u_id():
                    reset_user_matched = True
                    reset_user.set_reset_code(new_reset_code)

            # Add the user and reset code to the reset_password_list
            if not reset_user_matched:
                new_reset = ResetCode(reset_u_id = user.get_u_id(),
                                      reset_code = new_reset_code)
                reset_password_list.append_json(new_reset.get_json())

            # Populate this record entry with the relevant data
            user.set_reset_attempts(user.get_reset_attempts() + 1)
            user.set_reset_code(new_reset_code)
            user.set_reset_time(datetime.now())

            # Save all data and return the reset code to be sent via email to
            # the user in server.py
            user_list.save()
            reset_password_list.save()
            return new_reset_code

    # If the program reaches this line, the given email has not been found
    raise ValueError('Email entered does not belong to a user')

# Given a reset code for a user, set that user's new password to the password
# provided
def auth_passwordreset_reset(reset_code, new_password):

    # Check that the newly given password is an appropriate length and only
    # contains standard ASCII-standard characters
    if auth_helper.password_check(new_password) == 0:
        raise ValueError('Password cannot be less than 6 characters')
    elif auth_helper.password_check(new_password) == -1:
        raise ValueError('Password must be ASCII-standard characters only')

    # Check that the given reset code is valid and matches a stored code in the
    # reset_password_list
    reset_code_valid = False
    for reset_user in reset_password_list:
        if reset_user.get_reset_code() == reset_code:
            # Get the u_id of the user requesting the rest
            reset_user_id = reset_user.get_reset_u_id()
            reset_password_list.remove(reset_user)
            reset_code_valid = True
            break

    # Raise an error if the code is invalid
    if not reset_code_valid:
        raise ValueError('Invalid reset code')

    # If the program reaches this line, the reset code and password are valid
    # Update the user's password iin the user_list
    user = user_list[reset_user_id]
    user.set_hashed_password(auth_helper.sha_256(user.get_salt() +
                                                 new_password))
    user.set_reset_code(None)
    user.set_reset_attempts(0)
    user.set_reset_time(datetime.now() - timedelta(hours = 24))

    # Logout user if user is currently active
    for user in jwt_tokens:
        if auth_helper.active_token_to_uid(user) == reset_user_id:
            auth_logout(user)

    # Save all data and return
    reset_password_list.save()
    user_list.save()
    return
