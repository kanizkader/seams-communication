'''
Module for user
'''
from helpers.valid_user_helper import check_valid_auth_user_id, find_user, decode_jwt, check_token_valid
from helpers.other_helper import get_email, auth_id_to_user
import urllib
from PIL import Image
from src.data_store import data_store
from src.error import InputError
import re
import requests
from src.config import url
from src.users import users_stats_v1
from time import time

SUCCESS = 200

def user_profile_setemail_v1(token, email):
    '''
   <Update the authorised user's email address>    
    Arguments:
        - Token :: [str] - The user's token.
        - Email :: [str] - An email address.
    Exceptions: 
        InputError - Occurs when:
            - Email entered is not a valid email.
            - Email address is already being used by another user.
        AccessError - Occurs when:
            - Token is invalid
    Return Value:
        N/A
    '''
    check_token_valid(token)
    store = data_store.get()
    data = decode_jwt(token)
    auth_user_id = data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)

    for user in store['users']:
        if (user['auth_user_id'] == data['auth_user_id']) and data['session_id'] in user['session_id']:
            # checks email address is not already being used by another user
            for user in store["users"]:
                if get_email(user) == email:
                    raise InputError(description="Email is already taken.")
            # checks email entered is a valid email
            regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
            if not (re.fullmatch(regex, email)):
                raise InputError(description = "Invalid Email, Please enter valid email address.")
            user['email'] = email
    data_store.set(store)
    return {}


def user_profile_sethandle_v1(token, handle_str):
    '''
   <Update the authorised user's handle (i.e. display name)>    
    Arguments:
        - Token :: [str] - The user's token.
        - handle_str :: [str] - A user's handle.
    Exceptions: 
        InputError - Occurs when:
            - length of handle_str is not between 3 and 20 characters inclusive.
            - handle_str contains characters that are not alphanumeric.
            - the handle is already used by another user
        AccessError - Occurs when:
            - Token is invalid
    Return Value:
        N/A
    '''
    check_token_valid(token)
    store = data_store.get()
    data = decode_jwt(token)
    auth_user_id = data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)
   
    #Checking if handle length is valid
    if not 3 <= len(handle_str) <= 20:
        raise InputError(description = "handle_str is not between 3 and 20 characters inclusive")
    #Checking if handle has duplicates
    for user in store['users']:
        if handle_str == user['handle_str']:                              
            raise InputError(description = "handle_str is already in use")
        elif handle_str.isalnum() == False:
            raise InputError(description = "handle_str is not valid")
        if (user['auth_user_id'] == data['auth_user_id']) and data['session_id'] in user['session_id']:
            user['handle_str'] = handle_str
    data_store.set(store)
    return {}

def user_profile_v1(token, u_id):
    '''
    For a valid user, returns information about their user_id, email, first name, last name, and handle
    Method = GET
    Parameters:
        { token, u_id }
    Return Type:
        { user }
    '''
    check_token_valid(token)
    store = data_store.get()
    check_token_valid(token)
    data = decode_jwt(token)
    auth_user_id = data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)
   
    for user in store['users']:
        if user['auth_user_id'] == u_id:
            userInfo = {
                'user_id': u_id,
                'email': user['email'],
                'name_first': user['name_first'] ,
                'name_last': user['name_last'],
                "handle_str": user['handle_str'],
                'profile_img_url': user['profile_img_url']
            } 
            data_store.set(store)
            return {'user': userInfo}
    raise InputError('Error: User ID provided is invalid')
    
def user_profile_setname_v1(token, name_first, name_last):
    '''
    Update the authorised user's first and last name
    Method = PUT
    Parameters:
        { token, name_first, name_last }
    Return Type:
        {}
    '''
    check_token_valid(token)
    store = data_store.get()
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)
    
    #Checking if first name is valid
    if len(name_first) < 1 or len(name_first) > 50 or str.isdigit(name_first):
        raise InputError (description="Invalid first name")
    #Checking if last name is valid
    if len(name_last) < 1 or len(name_last) > 50 or str.isdigit(name_last):
        raise InputError (description="Invalid last name")
    
    user = find_user(auth_user_id)
    user['name_first'] = name_first,
    user['name_last'] = name_last
    data_store.set(store)
    return {}

def user_profile_upload_photo(token, img_url, x_start, y_start, x_end, y_end):
    '''
    Given a URL of an image on the internet, crops the image within bounds 
    (x_start, y_start) and (x_end, y_end). Position (0,0) is the top left.
    Parameters:
        {token, img_url, x_start, y_start, x_end, y_end}
        
    Exceptions:
        AccessError:
            - invalid token
            
        InputError:       
            - img_url returns an HTTP status other than 200, 
            or any other errors occur when attempting to retrieve the image 
            - any of x_start, y_start, x_end, y_end are not within the 
            dimensions of the image at the URL
            - x_end is less than or equal to x_start or y_end is less than or equal to y_start
            - image uploaded is not a JPG
    Return Type:
        {}
    '''
    store = data_store.get()
    check_token_valid(token)
    data = decode_jwt(token)
    auth_user_id = data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)
    
    #Check if non-http
    try:
        req = requests.get(img_url)
    except requests.exceptions.ConnectionError as e:
        # had to change this to keep pylint happy
        raise InputError(description = "Connection Error") from e
    if req.status_code != SUCCESS:
        raise InputError(description = 'Invalid Url')
    
    filepath = 'src/static/' + str(auth_user_id) + '.jpg'
    #Retrieve image url
    urllib.request.urlretrieve(img_url, filepath)
    
    # Opening the file for cropping
    imgObject = Image.open(filepath)
    # crop length must be withing dimensions of the image
    width, height = imgObject.size
    if x_start > width or x_end > width or x_start < 0 or x_end < 0 or x_start >= x_end:
        raise InputError(description="x_start or x_end are not within the dimensions of the image")
    if y_start > height or y_end > height or y_start < 0 or y_end < 0 or y_start >= y_end:
        raise InputError(description="y_start or y_end are not within the dimensions of the image")
    # cropping image
    cropped = imgObject.crop((x_start, y_start, x_end, y_end))
    cropped.save(filepath)
    
    # assigning img url to specified user
    store['users'][auth_user_id - 1]['profile_img_url'] = url + f'static/{auth_user_id}'
    store = data_store.get()
    data_store.set(store)
            
    return {}

def user_stat_v1(token):
    '''
    Fetches the required statistics about this user's use of UNSW Seams.    
    
    Arguments:
        token (string)  - Users token
    Exception:
        AccessError when token is invalid.
    Return value:
        {user_stats}
    '''
    check_token_valid(token)
    data_store.get()
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)
    auth_user = auth_id_to_user(auth_user_id)
    
    workspace_stats = users_stats_v1(token)["workspace_stats"]
    result = auth_user["user_stats"]
    numerator = (result["channels_joined"][-1]["num_channels_joined"] + result["dms_joined"][-1]["num_dms_joined"] + result["messages_sent"][-1]["num_messages_sent"])
    denominator = (workspace_stats["channels_exist"][-1]["num_channels_exist"] + workspace_stats["dms_exist"][-1]["num_dms_exist"] + workspace_stats["messages_exist"][-1]["num_messages_exist"])
    if denominator == 0:
        result["involvement_rate"] = 0.0
    else:
       result["involvement_rate"] = numerator/denominator 
        
    result['channels_joined'] = result['channels_joined'][-1]
    result['dms_joined'] = result['dms_joined'][-1]
    result['messages_sent'] = result['messages_sent'][-1]
    return { "user_stats" : result }

