# Functions are imported from classes.py to store data
from iteration3.classes import List_plus, User, Channel, Message, ResetCode

# A list of active tokens
# Resets upon re-launching server
jwt_tokens = []

# List of User objects, one for each registered user
user_list = List_plus(User, 'instance_saves/userList.json')
user_list.load()

# List of reset codes, one for each code
reset_password_list = List_plus(ResetCode,
                                       'instance_saves/resetPasswordList.json')
reset_password_list.load()
