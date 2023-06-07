
'''
pip3 packages
'''
import pytest
import requests
from src import config
import json
from src.error import AccessError, InputError
from helpers.other_helper import generate_jwt, auth_id_to_user
import time
import datetime

NO_ERROR = 200
BASE_URL = config.url
IMG_URL = "https://www.cse.unsw.edu.au/~richardb/index_files/RichardBuckland-200.png"
DEFAULT_IMG = 'https://en.wikipedia.org/wiki/University_of_New_South_Wales#/media/File:ARC_UNSW_logo.png'
INVALID_IMG = 'https://thisisnotanimage'
# FIXTURES
@pytest.fixture
def clear():
    return requests.delete(f"{BASE_URL}clear/v1")
@pytest.fixture
def jack():
    return requests.post(f"{BASE_URL}auth/register/v2", json={'email':'z5359521@ad.unsw.edu.au', 'password' : 'Pass54321word', 'name_first':'Jack', 'name_last':'Hill'})
@pytest.fixture
def sarah():
    return requests.post(f"{BASE_URL}auth/register/v2", json={'email':'z5363412@ad.unsw.edu.au', 'password' : 'Parrrpp', 'name_first':'Sarah', 'name_last':'Cat'})
@pytest.fixture
def hayden():
    return requests.post(f"{BASE_URL}auth/register/v2", json={'email':'haydensmith@ad.unsw.edu.au', 'password' : 'mynameis8', 'name_first':'Hayden', 'name_last':'Smith'})

##################################################################################################
# USER_PROFILE (Get)

def test_one_user_profile_v1(clear, jack):
    '''
    test for one user
    '''
    user = jack.json()
    res = requests.get(f'{BASE_URL}user/profile/v1', params={'token': user['token'], 'u_id': user['auth_user_id']})
    assert res.status_code == 200
    assert user['auth_user_id'] == 1

# incorrect token
def test_wrong_token_user_profile_v1(clear, jack):
    '''
    test wrong token
    '''
    user = jack.json()
    res = requests.get(f'{BASE_URL}user/profile/v1', params={'token': 'Wrong', 'u_id': user['auth_user_id']})
    assert res.status_code == AccessError().code

def test_wrong_id_user_profile_v1(clear, jack):
    '''
    test wrong id 
    '''
    user = jack.json()
    res = requests.get(f'{BASE_URL}user/profile/v1', params={'token': user['token'], 'u_id': 'Wrong'})
    assert res.status_code == InputError().code

def test_multiple_user_profile_v1(clear, jack, sarah):
    '''
    test function for multiple users
    '''
    user_1 = jack.json()
    res = requests.get(f'{BASE_URL}user/profile/v1', params={'token': user_1['token'], 'u_id': user_1['auth_user_id']})
    assert res.status_code == 200

def test_user_two_sessions(clear,jack):
    user1 = jack.json()
    
    res = requests.post(f'{BASE_URL}auth/login/v2', json = {
        'email':'z5359521@ad.unsw.edu.au', 
        'password' : 'Pass54321word'
    })
    session2 = res.json()
    res2 = requests.get(f'{BASE_URL}user/profile/v1', params={'token': user1['token'], 
                                                              'u_id': user1['auth_user_id']})
    res3 = requests.get(f'{BASE_URL}user/profile/v1', params={'token': session2['token'], 
                                                              'u_id': session2['auth_user_id']})
    assert res2.json() == res3.json()
    
##################################################################################################
# USER_PROFILE_SETNAME (Put)

def test_one_user_profile_setname_v1(clear, jack):
    '''
    test profile setname functionality for one user
    '''
    user = jack.json()
    res = requests.put(f'{BASE_URL}user/profile/setname/v1', json={'token': user['token'], 'name_first': 'new', 'name_last': 'name'})
    assert res.status_code == 200
    assert user['auth_user_id'] == 1

def test_wrong_token_user_profile_setname_v1(clear, jack): 
    '''
    test incorrect token
    '''  
    res = requests.put(f'{BASE_URL}user/profile/setname/v1', json={'token': 'Wrong', 'name_first': 'new', 'name_last': 'name'})
    assert res.status_code == AccessError().code

def test_multiple_user_profile_setname_v1(clear, jack, sarah):
    '''
    test multiple users
    ''' 
    user1 = jack.json()
    user2 = sarah.json()
    res = requests.put(f'{BASE_URL}user/profile/setname/v1', json={'token': user1['token'], 'name_first': 'new', 'name_last': 'name'})
    assert res.status_code == 200
    assert user1['auth_user_id'] == 1
    assert user2['auth_user_id'] == 2

def test_user_profile_setname_invalid_first_name_v1(clear, jack):
    '''
    test invalid first name
    '''
    user = jack.json()
    res = requests.put(f'{BASE_URL}user/profile/setname/v1', json={'token': user['token'], 'name_first': 0*'A', 'name_last': 'name'})
    assert res.status_code == InputError().code
    res = requests.put(f'{BASE_URL}user/profile/setname/v1', json={'token': user['token'], 'name_first': 51*'A', 'name_last': 'name'})
    assert res.status_code == InputError().code
    res = requests.put(f'{BASE_URL}user/profile/setname/v1', json={'token': user['token'], 'name_first': '123', 'name_last': 'name'})
    assert res.status_code == InputError().code
def test_user_profile_setname_invalid_last_name_v1(clear, jack):
    '''
    test invalid last name
    '''
    user = jack.json()
    res = requests.put(f'{BASE_URL}user/profile/setname/v1', json={'token': user['token'], 'name_first': 'new', 'name_last': 0*'A'})
    assert res.status_code == InputError().code
    res = requests.put(f'{BASE_URL}user/profile/setname/v1', json={'token': user['token'], 'name_first': 'new', 'name_last': 51*'A'})
    assert res.status_code == InputError().code
    res = requests.put(f'{BASE_URL}user/profile/setname/v1', json={'token': user['token'], 'name_first': 'new', 'name_last': '123'})
    assert res.status_code == InputError().code     
##############################################################################################
def test_user_profile_setemail(clear):
    '''
    Testing for user email updated
    '''
    res = requests.post(f'{BASE_URL}auth/register/v2', json = {
        'email': "old@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': "Smith"
    })
    user = res.json()
    
    response = requests.put(f'{BASE_URL}user/profile/setemail/v1', json = {
        'token': user['token'], 
        'email': 'new@gmail.com'})
    
    res = requests.get(f'{BASE_URL}user/profile/v1', params={
        'token': user['token'], 
        'u_id': user['auth_user_id']})
    
    assert res.json()['user']['email'] == 'new@gmail.com'
    assert response.status_code == 200

def test_user_profile_setemail_invalid(clear):
    '''
    Testing for user email invalid
    '''
    res = requests.post(f'{BASE_URL}auth/register/v2', json = {
        'email': "old@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': "Smith"
    })
    user = res.json()
    
    response = requests.put(f'{BASE_URL}user/profile/setemail/v1', json ={
        'token': user['token'], 
        'email': 'abc.au'})
    assert response.status_code == InputError().code

def test_user_profile_setemail_taken(clear):
    '''
    Testing for user email duplicate
    '''
    res = requests.post(f'{BASE_URL}auth/register/v2', json = {
        'email': "email@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': "Smith"
    })
    user = res.json()

    response = requests.put(f'{BASE_URL}user/profile/setemail/v1', json ={
        'token': user['token'], 
        'email': 'email@gmail.com'})
    assert response.status_code == InputError().code
    
def test_user_profile_setemail_token_invalid(clear):
    '''
    Testing for user token invalid
    '''
    res = requests.post(f'{BASE_URL}auth/register/v2', json = {
        'email': "email@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': "Smith"
    })
    user = res.json()
    token = generate_jwt(user['auth_user_id'] + 1,1)
    response = requests.put(f'{BASE_URL}user/profile/setemail/v1', json ={
        'token': token, 
        'email': 'new@gmail.com'})
    assert response.status_code == AccessError().code
    
def test_user_profile_sethandle(clear):
    '''
    Testing for user handle updated
    '''
    res = requests.post(f'{BASE_URL}auth/register/v2', json = {
        'email': "email@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': "Smith"
    })
    user = res.json()
    
    response = requests.put(f'{BASE_URL}user/profile/sethandle/v1', json = {
        'token': user['token'], 
        'handle_str': 'mynewhandleset'})
    
    res = requests.get(f'{BASE_URL}user/profile/v1', params={
        'token': user['token'], 
        'u_id': user['auth_user_id']})
    
    assert response.status_code == 200
    assert res.json()['user']['handle_str'] == 'mynewhandleset'
    
def test_user_sethandle_taken(clear):
    '''
    Testing for user handle taken
    '''
    res = requests.post(f'{BASE_URL}auth/register/v2', json = {
        'email': "email@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': "Smith"
    })
    
    res = requests.post(f'{BASE_URL}auth/register/v2', json={
        'email': "adam.smith@ad.unsw.edu.au",
        'password': "password",
        'name_first': "Adam",
        'name_last': "Smith"
    })
    user2 = res.json()
    
    response = requests.put(f'{BASE_URL}user/profile/sethandle/v1', json = {
        'token': user2['token'], 
        'handle_str': 'haydensmith'})
    
    assert response.status_code == InputError().code

def test_invalid_handle(clear):
    '''
    Testing for invalid handle
    '''
    res = requests.post(f'{BASE_URL}auth/register/v2', json = {
        'email': "email@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': "Smith"
    })
    
    user1 = res.json()
    
    res = requests.post(f'{BASE_URL}auth/register/v2', json={
        'email': "adam.smith@ad.unsw.edu.au",
        'password': "password",
        'name_first': "Adam",
        'name_last': "Smith"
    })
    user2 = res.json()
    
    response1 = requests.put(f'{BASE_URL}user/profile/sethandle/v1', json = {
        'token': user1['token'], 
        'handle_str': '!ayden*smith'})
    
    assert response1.status_code == InputError().code
    
    response2 = requests.put(f'{BASE_URL}user/profile/sethandle/v1', json = {
        'token': user2['token'], 
        'handle_str': 'good day'})
    assert response2.status_code == InputError().code
    
def test_user_sethandle_length(clear):
    '''
    Testing for user handle length
    '''
    res = requests.post(f'{BASE_URL}auth/register/v2', json = {
        'email': "email@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': "Smith"
        })
    user = res.json()
    
    response = requests.put(f'{BASE_URL}user/profile/sethandle/v1', json = {
        'token': user['token'], 
        'handle_str': 'hi'})
    
    assert response.status_code == InputError().code
    
    response = requests.put(f'{BASE_URL}user/profile/sethandle/v1', json = {
        'token': user['token'], 
        'handle_str': 21 * 'A'})
    
    assert response.status_code == InputError().code
##############################################################################################
###USER_PROFILE_UPLOAD_PHOTO#####
def test_user_profile_upload_photo_invalid_token(clear, jack):
    '''
    Testing for user invalid token
    '''
    jack.json()
    response = requests.post(f'{BASE_URL}user/profile/uploadphoto/v1', json = {
            'token': 'invalid token',
            'img_url': IMG_URL,
            'x_start': 10,
            'y_start': 10,
            'x_end': 100,
            'y_end': 100 })
                            
    assert response.status_code == AccessError().code

def test_user_profile_photo_negative_param(clear, jack):
    '''
    Testing for invalid parameters for image
    '''
    user = jack.json()
    
    response = requests.post(f'{BASE_URL}user/profile/uploadphoto/v1', json = {
            'token': user['token'],
            'img_url': IMG_URL,
            'x_start': -2,
            'y_start': 10,
            'x_end': 100,
            'y_end': 100 })
                            
    assert response.status_code == InputError().code
    
    response = requests.post(f'{BASE_URL}user/profile/uploadphoto/v1', json = {
            'token': user['token'],
            'img_url': IMG_URL,
            'x_start': 10,
            'y_start': -2,
            'x_end': 100,
            'y_end': 100 })
                            
    assert response.status_code == InputError().code
    
    response = requests.post(f'{BASE_URL}user/profile/uploadphoto/v1', json = {
            'token': user['token'],
            'img_url': IMG_URL,
            'x_start': 10,
            'y_start': 10,
            'x_end': -10,
            'y_end': 100 })
                            
    assert response.status_code == InputError().code
    
    response = requests.post(f'{BASE_URL}user/profile/uploadphoto/v1', json = {
            'token': user['token'],
            'img_url': IMG_URL,
            'x_start': 10,
            'y_start': 10,
            'x_end': 100,
            'y_end': -10 })
                            
    assert response.status_code == InputError().code

def test_user_profile_photo_outbounds(clear, jack):
    '''
    Tests whether the images parameters are cropped out of the limit
    '''
    user = jack.json()
    response = requests.post(f'{BASE_URL}user/profile/uploadphoto/v1', json={
        "token":    user['token'],
        "img_url":  IMG_URL,
        "x_start":  0,
        "y_start":  0,
        "x_end":    20000,
        "y_end":    40000
    })
    assert response.status_code == InputError().code

    response = requests.post(f'{BASE_URL}user/profile/uploadphoto/v1', json={
        "token":    user['token'],
        "img_url":  IMG_URL,
        "x_start":  0,
        "y_start":  0,
        "x_end":    40000,
        "y_end":    51061
    })
    assert response.status_code == InputError().code

    response = requests.post(f'{BASE_URL}user/profile/uploadphoto/v1', json={
        "token":    user['token'],
        "img_url":  IMG_URL,
        "x_start":  5000,
        "y_start":  5000,
        "x_end":    20000,
        "y_end":    10000
    })
    assert response.status_code == InputError().code

def test_all_params_zero(clear, jack):
    '''
    Tests whether the images parameters exist
    '''
    user = jack.json()
    response = requests.post(f'{BASE_URL}user/profile/uploadphoto/v1', json = {
            'token': user['token'],
            'img_url': IMG_URL,
            'x_start': 0,
            'y_start': 0,
            'x_end': 0,
            'y_end': 0 })
                            
    assert response.status_code == InputError().code

def test_invalid_image(clear, jack):
    '''
    Tests whether the image url is valid
    '''
    user = jack.json()
    response = requests.post(f'{BASE_URL}user/profile/uploadphoto/v1', json = {
            'token': user['token'],
            'img_url': INVALID_IMG,
            'x_start': 0,
            'y_start': 0,
            'x_end': 10,
            'y_end': 10 })
                            
    assert response.status_code == InputError().code

def test_start_end_params(clear, jack):
    '''
    Tests whether the start and end cropped params are valid
    '''
    user = jack.json()
    
    response = requests.post(f'{BASE_URL}user/profile/uploadphoto/v1', json = {
            'token': user['token'],
            'img_url': IMG_URL,
            'x_start': 100,
            'y_start': 0,
            'x_end': 0,
            'y_end': 10 })
    
    assert response.status_code == InputError().code
    
    response = requests.post(f'{BASE_URL}user/profile/uploadphoto/v1', json = {
            'token': user['token'],
            'img_url': IMG_URL,
            'x_start': 0,
            'y_start': 100,
            'x_end': 10,
            'y_end': 0})
    
    assert response.status_code == InputError().code
    
    response = requests.post(f'{BASE_URL}user/profile/uploadphoto/v1', json = {
            'token': user['token'],
            'img_url': IMG_URL,
            'x_start': 100,
            'y_start': 100,
            'x_end': 0,
            'y_end': 0})
    
    assert response.status_code == InputError().code
    
def test_default_img_url(clear, jack):
    '''
    Tests when user first registers that it is set to a default image.
    '''
    user = jack.json()
    response = requests.get(f'{BASE_URL}user/profile/v1', params = {
        'token' : user['token'],
        'u_id' : user['auth_user_id'] 
    })
    assert response.status_code == 200
    assert response.json()['user']['profile_img_url'] == DEFAULT_IMG
    
def test_user_profile_upload_photo(clear, jack):
    '''
    Tests if the user uploads profile photo successfully
    '''
    user = jack.json()
    
    response = requests.get(f'{BASE_URL}user/profile/v1', params = {
        'token' : user['token'],
        'u_id' : user['auth_user_id']
    })
    assert response.json()['user']['profile_img_url'] == DEFAULT_IMG
    
    response = requests.post(f'{BASE_URL}user/profile/uploadphoto/v1', json = {
            'token': user['token'],
            'img_url': IMG_URL,
            'x_start': 0,
            'y_start': 0,
            'x_end': 100,
            'y_end': 100})
    
    assert response.status_code == 200
    
    response = requests.get(f'{BASE_URL}user/profile/v1', params = {
        'token' : user['token'],
        'u_id' : user['auth_user_id']
    })
    auth_user_id = user['auth_user_id']
    assert response.json()['user']['profile_img_url'] == BASE_URL + f'static/{auth_user_id}'
#############################################################################################
##USER_STATS#####
def test_initial_stats(clear, jack):
    '''
    Tests initial stats for a user
    '''
    user = jack.json()
    
    response = requests.get(f'{BASE_URL}user/stats/v1', params={
        "token": user['token']
    })
    assert response.status_code == 200

    user_stats = response.json()["user_stats"]
    assert user_stats["channels_joined"]["num_channels_joined"] == 0
    assert user_stats["dms_joined"]["num_dms_joined"] == 0
    assert user_stats["messages_sent"]["num_messages_sent"] == 0
    assert user_stats["involvement_rate"] == 0

def test_channels_create_stats(clear, jack):
    '''
    Tests user stats once channel is created
    '''
    user = jack.json()
    
    response = requests.post(f'{BASE_URL}channels/create/v2', json={
        "token": user['token'],
        "name": "channel1",
        "is_public": True
    })
    
    assert response.status_code == 200

    response = requests.get(f'{BASE_URL}user/stats/v1', params={
        "token": user['token']})
    
    assert response.status_code == 200
    user_stats = response.json()["user_stats"]
    assert user_stats["channels_joined"]["num_channels_joined"] == 1
    assert user_stats["dms_joined"]["num_dms_joined"] == 0
    assert user_stats["messages_sent"]["num_messages_sent"] == 0
    assert user_stats["involvement_rate"] == 1/1
    
def test_channel_join_stats(clear,jack, sarah):
    '''
    Tests user stats once user joins a channel
    '''
    user = jack.json()
    user2 = sarah.json()
    
    requests.post(f'{BASE_URL}channels/create/v2', json={
        "token": user['token'],
        "name": "channel1",
        "is_public": True
    })
    
    requests.post(f"{BASE_URL}channel/join/v2", json={
        "token": user2['token'],
        "channel_id" : 1,})
    
    response = requests.get(f"{BASE_URL}user/stats/v1", params={
        "token": user2['token']})
    
    assert response.status_code == 200
    user_stats = response.json()["user_stats"]
    assert user_stats["channels_joined"]["num_channels_joined"] == 1
    
def test_channel_invite_stats(clear, jack, sarah):
    '''
    Tests user stats once user is invited into a channel
    '''
    user = jack.json()
    user2 = sarah.json()
    
    requests.post(f'{BASE_URL}channels/create/v2', json={
        "token": user['token'],
        "name": "channel1",
        "is_public": True
    })
    
    requests.post(f'{BASE_URL}channel/invite/v2', json = {
        'token' : user['token'],
        'channel_id' : 1,
        'u_id' : 2})
    
    response = requests.get(f"{BASE_URL}user/stats/v1", params={
        "token": user2['token']})
    
    assert response.status_code == 200
    user_stats = response.json()["user_stats"]
    assert user_stats["channels_joined"]["num_channels_joined"] == 1
    
def test_channel_leave_stats(clear, jack, sarah):
    '''
    Tests user stats once user leaves a channel
    '''
    user = jack.json()
    user2 = sarah.json()
    
    requests.post(f'{BASE_URL}channels/create/v2', json={
        "token": user['token'],
        "name": "channel1",
        "is_public": True
    })
    
    requests.post(f'{BASE_URL}channel/invite/v2', json={
        "token": user['token'],
        "channel_id": 1,
        "u_id": 2
    })

    requests.post(f"{BASE_URL}channel/leave/v1", json={
        "token": user2['token'],
        "channel_id": 1
    })
    response = requests.get(f"{BASE_URL}user/stats/v1", params={
        "token": user2['token']})
    
    assert response.status_code == 200
    user_stats = response.json()["user_stats"]
    assert user_stats["channels_joined"]["num_channels_joined"] == 0
    

def test_dm_create_user1_stats(clear, jack):
    '''
    Tests user stats once user creates a dm
    '''
    user = jack.json()
    
    requests.post(f"{BASE_URL}dm/create/v1", json={
        "token": user['token'],
        "u_ids": []
    })
    
    response = requests.get(f"{BASE_URL}user/stats/v1", params={
        "token": user['token']})
    
    assert response.status_code == 200
    user_stats = response.json()["user_stats"]
    assert user_stats["dms_joined"]["num_dms_joined"] == 1

def test_dm_create_user2_stats(clear, jack, sarah):
    '''
    Tests user stats once user creates a dm with another user
    '''
    user = jack.json()
    user2 = sarah.json()
    
    response = requests.post(f"{BASE_URL}dm/create/v1", json={
        "token": user['token'],
        "u_ids": [2]
    })
    
    assert response.status_code == 200
    
    response = requests.get(f"{BASE_URL}user/stats/v1", params={
        "token": user2['token']})
    
    assert response.status_code == 200
    user_stats = response.json()["user_stats"]
    assert user_stats["dms_joined"]["num_dms_joined"] == 1

def test_dm_remove_stats(clear, jack, sarah):
    '''
    Tests user stats once user removes dm
    '''
    user = jack.json()
    user2 = sarah.json()
    
    requests.post(f"{BASE_URL}dm/create/v1", json={
        "token": user['token'],
        "u_ids": [2]
    })
    
    requests.delete(f"{BASE_URL}dm/remove/v1", json = {
        'token' : user['token'],
        'dm_id' : 1
    })
    
    response = requests.get(f"{BASE_URL}user/stats/v1", params={
        "token": user['token']})

    assert response.status_code == 200
    user_stats = response.json()["user_stats"]
    assert user_stats["dms_joined"]["num_dms_joined"] == 0
    
    response = requests.get(f"{BASE_URL}user/stats/v1", params={
        "token": user2['token']})

    assert response.status_code == 200
    user_stats = response.json()["user_stats"]
    assert user_stats["dms_joined"]["num_dms_joined"] == 0
    
def test_dm_leave_stats(clear, jack, sarah):
    '''
    Tests user stats once user leaves a dm
    '''
    user = jack.json()
    user2 = sarah.json()
    
    requests.post(f"{BASE_URL}dm/create/v1", json={
        "token": user['token'],
        "u_ids": [2]
    })
    
    requests.post(f"{BASE_URL}dm/leave/v1", json={
        "token": user['token'],
        "dm_id": 1
    })
    
    response = requests.get(f"{BASE_URL}user/stats/v1", params={
        "token": user['token']
    })
    
    assert response.status_code == 200
    user_stats = response.json()["user_stats"]
    assert user_stats["dms_joined"]["num_dms_joined"] == 0

    response = requests.get(f"{BASE_URL}user/stats/v1", params={
        "token": user2['token']
    })
    
    assert response.status_code == 200
    user_stats = response.json()["user_stats"]
    assert user_stats["dms_joined"]["num_dms_joined"] == 1

def test_message_send_stats(clear, jack):
    '''
    Tests user stats once user sends a message
    '''
    user = jack.json()
    
    requests.post(f"{BASE_URL}channels/create/v2", json={
        "token": user['token'],
        "name": "channel1",
        "is_public": True
    })
    
    requests.post(f"{BASE_URL}message/send/v1", json = {
        "token" : user['token'],
        'channel_id' : 1,
        'message': 'testing'
    })
    
    response = requests.get(f"{BASE_URL}user/stats/v1", params={
        "token": user['token']
    })
    
    user_stats = response.json()["user_stats"]
    assert user_stats["channels_joined"]["num_channels_joined"] == 1
    assert user_stats["messages_sent"]["num_messages_sent"] == 1

def test_message_senddm_stats(clear, jack):
    '''
    Tests user stats once user sends a message dm
    '''
    user = jack.json()
    
    requests.post(f"{BASE_URL}dm/create/v1", json={
        "token": user['token'],
        'u_ids' : []
    })
    
    requests.post(f"{BASE_URL}message/senddm/v1", json = {
        "token" : user['token'],
        'dm_id' : 1,
        'message': 'testing'
    })
    
    response = requests.get(f"{BASE_URL}user/stats/v1", params={
        "token": user['token']
    })
    
    assert response.status_code == 200
    user_stats = response.json()["user_stats"]
    assert user_stats["dms_joined"]["num_dms_joined"] == 1
    assert user_stats["messages_sent"]["num_messages_sent"] == 1
    
def test_message_sendlater_stats(clear, jack, sarah):
    '''
    Tests user stats once user sends a message later
    '''
    user = jack.json()

    # create 1 channel
    requests.post(f"{BASE_URL}channels/create/v2", json={
        "token": user['token'],
        "name": "channel1",
        "is_public": True
    })

    # send later a message to channel1
    requests.post(f"{BASE_URL}message/sendlater/v1", json={
        "token": user['token'],
        "channel_id": 1,
        "message": "testing",
        "time_sent": datetime.datetime.now().timestamp() + 2
    })
    time.sleep(3)
    response = requests.get(f"{BASE_URL}user/stats/v1", params={
        "token": user['token'],
    })
    assert response.status_code == 200

    user_stats = response.json()["user_stats"]
    assert user_stats["channels_joined"]["num_channels_joined"] == 1
    assert user_stats["messages_sent"]["num_messages_sent"] == 1

def test_message_sendlaterdm_stats(clear, jack):
    '''
    Tests user stats once user sends a message later
    '''
    user = jack.json()

    requests.post(f"{BASE_URL}dm/create/v1", json={
        "token": user['token'],
        "u_ids": []
    })

    requests.post(f"{BASE_URL}message/sendlaterdm/v1", json={
        "token": user['token'],
        "dm_id": 1,
        "message": "testing",
        "time_sent": datetime.datetime.now().timestamp() + 2
    })
    time.sleep(3)
    response = requests.get(f"{BASE_URL}user/stats/v1", params={
        "token": user['token'],
    })
    assert response.status_code == 200

    user_stats = response.json()["user_stats"]
    assert user_stats["dms_joined"]["num_dms_joined"] == 1
    assert user_stats["messages_sent"]["num_messages_sent"] == 1


def test_user_remove_stats(clear ,jack, sarah):
    '''
    Tests user stats once user is removed and has no access to the Seams.  
    Access Error is raised.
    '''
    user = jack.json()
    user2 = sarah.json()
    
    requests.post(f"{BASE_URL}channels/create/v2", json={
        "token": user['token'],
        "name": "channel1",
        "is_public": True
    })
    
    requests.post(f"{BASE_URL}channel/join/v2", json={
        "token": user2['token'],
        "channel_id": 1,
    })
    
    response = requests.post(f"{BASE_URL}message/send/v1", json={
        "token": user2['token'],
        "channel_id": 1,
        "message": "testing"
    })
    
    assert response.status_code == NO_ERROR
    
    requests.delete(f"{BASE_URL}admin/user/remove/v1", json = {
        'token' : user['token'],
        'u_id' : 2
    })

    response = requests.get(f"{BASE_URL}users/stats/v1", params={
        "token": user2['token']
    })
    
    assert response.status_code == AccessError().code
