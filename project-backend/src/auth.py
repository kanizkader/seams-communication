'''
Implementation for:
    - auth_login_v2
    - auth_register_v2
    - auth_logout_v1
    - auth_passwordreset_request_v1
    - auth_passwordreset_reset_v1
'''
from src.data_store import data_store 
from helpers.valid_user_helper import decode_jwt, check_token_valid
from helpers.other_helper import email_to_auth_id, generate_new_sess_id, email_to_password
from helpers.user_stat_helper import update_total_users_num_workspace_stats
from src.error import InputError, AccessError
from time import time
import re
import jwt
import random
import string
import smtplib
import hashlib
#-----------------------------------------------------------------------------
SECRET = 'H15ABADGER'
DEFAULT_IMG = 'https://en.wikipedia.org/wiki/University_of_New_South_Wales#/media/File:ARC_UNSW_logo.png'
#-----------------------------------------------------------------------------
def auth_login_v2(email, password):
    '''
    <Given a registered user's email and password, returns their `token` value>
    Arguments:
        email :: [str] - The users email address.
        password :: [str] - The user's password.
    Exceptions: 
        InputError - Occurs when:
            - Email entered does not belong to a user
            - Password is not correct
    Return Value:
        Returns the user's auth_user_id and token in a dictionary
    '''
    store = data_store.get()
    #Assuring user ID exists
    userID = email_to_auth_id(email)
    if userID == 0:
        raise InputError(description="Invalid email")
    
    # Check if entered password matches stored password,
    hashedpw = email_to_password(email)
    if hashedpw != hashlib.sha256(password.encode()).hexdigest():
        raise InputError(description="Incorrect password")
    
    #Assuring that the user is already registered
    for user in store['users']:
        if user['auth_user_id'] == userID:
                session = generate_new_sess_id(user)
                user['session_id'].append(session)
                token = jwt.encode({'auth_user_id': userID, 'session_id': session}, SECRET, algorithm='HS256')
                data_store.set(store)
                return {'auth_user_id': userID, 'token' : token}
    raise InputError("User does not exist")

def auth_register_v2(email, password, name_first, name_last):
    '''
    < Given a user's first and last name, email address, and password, create a new account for them and return a new user ID>
    Arguments:
        email : [str] - The users email address.
        password : [str] - The user's password.
        name_first : [str] - The user's first name.
        name_last : [str] - The user's last name.
    Exceptions:
    InputError - Occurs when:
        - email entered is not a valid email (more in section 6.4)            
        - email address is already being used by another user
        - length of password is less than 6 characters
        - length of name_first is not between 1 and 50 characters inclusive
        - length of name_last is not between 1 and 50 characters inclusive
    Return Value:
        Returns user's auth_user_id and a token in the condition of a dictionary
    '''
    store = data_store.get()
    #Checking if valid email is entered.
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    if not (re.fullmatch(regex, email)):
        raise InputError("Invalid Email, Please enter valid email address.")
    #Checking if email is duplicated.
    for user in store['users']:
        if user['email'] == email:
            raise InputError(description="Email is already taken, Please enter new email address")
    #Cheking if password is valid
    if len(password) < 6:
        raise InputError(description="Invalid Password")
    #Checking if first name is valid
    if len(name_first) < 1 or len(name_first) > 50 or str.isdigit(name_first):
        raise InputError (description="Invalid first name")
    #Checking if last name is valid
    if len(name_last) < 1 or len(name_last) > 50 or str.isdigit(name_last):
        raise InputError (description="Invalid last name")
    
    #Creating user ID
    new_userID = len(store['users']) + 1
    
    #Creating new session
    session = 1
    
    #Creating a global permission_id
    if len(store["users"]) == 0:
        global_permID = 1
    else:
        global_permID = 2
        
    #Creating handle for user
    counter = -1
    intial_handle = (name_first + name_last).lower()
    origin_handle = ''.join(ch for ch in intial_handle if intial_handle.isalnum())[:20]
    handle = origin_handle
    
    #Checking if handle has duplicates
    stop = False
    while stop == False:
        stop = True
        for user in store['users']:
            if handle == user['handle_str']:                              
                counter += 1
                handle = origin_handle + str(counter)
                stop = False
                
    #encrypt password 
    hashedpw = hashlib.sha256(password.encode()).hexdigest()
    
    user = {"auth_user_id": new_userID,
            "email": email,
            "password": hashedpw,
            "name_first": name_first,
            "name_last": name_last,
            "handle_str" : handle, 
            "session_id" : [session],
            "perm_id" : global_permID,
            "profile_img_url" : DEFAULT_IMG,
            "user_stats" : {
                "channels_joined" : [
                    {
                        "num_channels_joined" : 0,
                        "time_stamp" : int(time())
                    }
                ],
                "dms_joined" : [
                    {
                        "num_dms_joined" : 0,
                        "time_stamp" : int(time())
                    }
                ],
                "messages_sent": [
                    {
                        "num_messages_sent" : 0,
                        "time_stamp" : int(time())                        
                    }
                ]},
            "reset_code": None,
            "notifications": [],
        }
    
    store['users'].append(user)
    data_store.set(store)
    update_total_users_num_workspace_stats()
    token = jwt.encode({'auth_user_id': new_userID, 'session_id': session}, SECRET, algorithm='HS256')
    
    return {'auth_user_id' : new_userID, 'token' : token}
#-----------------------------------------------------------------------------   
def auth_logout_v1(token):
    '''
    <Given an active token, invalidates the token to log the user out>
    Arguments:
        - token :: [str] - The user's token
    Exceptions:
        Access Error when:
            - Invalid token provided
    Return Value:
        {}
    '''
    # Obtain auth user id and session id from token
    check_token_valid(token)
    token_details = decode_jwt(token)
    auth_user_id = token_details['auth_user_id']
    session_id = token_details['session_id']
    # Remove session id from database to invalidate token
    store = data_store.get()
    for user in store['users']:
        if user['auth_user_id'] == auth_user_id:
            # Verify if user is already logged out 
            if session_id in user['session_id']:
                user['session_id'].remove(session_id)
            else:
                raise AccessError(description= "User has already logged out.")
    
    return {}
#-----------------------------------------------------------------------------
def auth_passwordreset_request_v1(email):
    ''' 
    <Given an email address, if the user is a registered user, sends them an email containing 
    a specific secret code, that when entered in auth/passwordreset/reset, shows that the user
    trying to reset the password is the one who got sent this email. 
    No error should be raised when passed an invalid email, as that would pose a security/privacy 
    concern. When a user requests a password reset, they should be logged out of all current 
    sessions.>
    Arguments:
        - email :: [str] - The user's token
    Exceptions:
        N/A
    Return Value:
        {}
    '''
    store = data_store.get()
    # generate unique code
    option = string.ascii_letters + string.digits
    code = (''.join(random.choices(option, k=6)))
    # check to see if user is registered
    handle = 0
    for user in store['users']:
        if user['email'] == email:
            handle = user['handle_str']
            user['reset_code'] = code
            data_store.set(store)        
    if handle == 0:
        return {}
    
    # sends them an email
    username = 'comp1531badger@gmail.com'
    password = 'PassW0rd'

    subject = 'UNSW Seams Verification Code'
    body = """
    Dear %s,
    
    We have received a request to access your UNSW Seams account assigned to this email address.
    Your unique verification code is:
        %s
    
    This is an automated email, please do not reply.
    
    Kind Regards,
    The UNSW Seams Support team.
    """ % (handle, code)

    email_content = f"From: {username}\nTo: {email}\nSubject: {subject}\n\n{body}\n"

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(username, password)
    server.sendmail(username, [email], email_content)
    server.close()
    return {}
#-----------------------------------------------------------------------------
def auth_passwordreset_reset_v1(reset_code, new_password):
    ''' 
    <Given a reset code for a user, set that user's new password to the password provided. 
    Once a reset code has been used, it is then invalidated.>
    Arguments:
        - reset_code
        - new_password    
    Exceptions:
        InputError - Occurs when:      
            - reset_code is not a valid reset code
            - password entered is less than 6 characters long
    Return Value:
        {}
    '''
    store = data_store.get()
    #Cheking if password is valid
    if len(new_password) < 6:
        raise InputError(description="Invalid Password")

    check = 0
    for user in store['users']:
        if user['reset_code'] == reset_code:
            user['password'] = hashlib.sha256(new_password.encode()).hexdigest()
            user['reset_code'] = None
            check = 1
            data_store.set(store)
    if check == 0:
        raise InputError(description="Invalid code")
    return {}
#-----------------------------------------------------------------------------       
