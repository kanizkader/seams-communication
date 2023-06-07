from src.data_store import initial_object, data_store
import jwt

from src.error import AccessError, InputError

SECRET = 'H15ABADGER'
RESET_SECRET = 'RESETTIME'

def decode_jwt(token):  
    '''
    decodes token
    '''  
    try:
        decode = jwt.decode(token, SECRET, algorithms=['HS256'])
    except jwt.exceptions.DecodeError:
        raise AccessError(description= "Unable to decode token") from None
    return decode

def check_token_valid(token):
    '''
    check token works
    '''
    data = decode_jwt(token)
    if check_valid_auth_user_id(data['auth_user_id']):
        user = find_user(data["auth_user_id"])
        for session in user["session_id"]:
            if session == data["session_id"]:
                return 
        raise AccessError(description= "Invalid Token")

def check_valid_u_id(u_id):
    '''
    returns input error if u_id is incorrect
    '''
    store = data_store.get()
    valid_ids = store['users']
    for user in valid_ids:
        if user['auth_user_id'] == u_id:
            return True
    raise InputError(description='Error: u_id provided is invalid')


def check_valid_auth_user_id(auth_user_id):
    '''
    checks whether user is a valid user id
    '''
    store = data_store.get()
    valid_ids = store['users']
    for user in valid_ids:
        if user['auth_user_id'] == auth_user_id:
            return True
    raise AccessError(description='Error: auth_user_id provided is invalid')

def find_user(auth_user_id):
    '''
    find the user we are looking for
    '''
    store = data_store.get()
    valid_ids = store['users']
    for user in valid_ids:
        if user['auth_user_id'] == auth_user_id:
            return user
    return
