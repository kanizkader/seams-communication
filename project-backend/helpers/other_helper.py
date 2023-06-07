#from src.data_store import initial_object
from src.data_store import initial_object, data_store
import jwt
import re
from unicodedata import name
from xxlimited import new
from json import dump, load
from os import path

from src.error import AccessError

SECRET = 'H15ABADGER'
RESET_SECRET = 'RESETTIME'

def get_auth_id(person):
    '''
    retrieve user's id
    '''
    return person['auth_user_id']  

def get_email(person):
    '''
    gets users email 
    '''
    return person['email']

def email_to_auth_id(email):
    ''' 
    gets auth user id from email
    '''
    store = data_store.get()
    for user in store['users']:
        if user['email'] == email:
            return get_auth_id(user)        
    return False

def generate_new_sess_id(user):
    '''
    Generate new session ID
    '''
    if len(user['session_id']) == 0:
        return 1
    session_id = user['session_id'][-1] + 1
    return session_id

def generate_jwt(auth_user_id, session_id):
    '''
    generates token
    '''
    return jwt.encode({'auth_user_id': auth_user_id, 'session_id': session_id}, SECRET, algorithm ='HS256')

def save_data():
    store = data_store.get()
    with open("persistance/datastore.json", "w") as FILE:
        dump(store, FILE)

def load_data():
    '''
    loads saved json file information into data_store
    '''
    if path.exists("persistance/datastore.json"):    
        with open("persistance/datastore.json", "r") as FILE:
            store = load(FILE)
            data_store.set(store)
            
def get_user_handle(auth_user_id):
    '''gets handle of user'''
    store = data_store.get()
    valid_ids = store['users']
    handle = ''
    for user in valid_ids:
        if auth_user_id == user['auth_user_id']:
            handle = user['handle_str']
    return handle

def email_to_password(email):
    '''
    return the user's password given the email
    '''
    store = data_store.get()
    for user in store["users"]:
        if user["email"] == email:
            return user['password']
    return

def auth_id_to_user(auth_user_id):
    '''
    returns the user given the auth_user_id
    '''
    store = data_store.get()
    for user in store["users"]:
        if get_auth_id(user) == auth_user_id:
            return user
    raise AccessError
