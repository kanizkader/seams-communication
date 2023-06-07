'''
pip3 packages
'''
import pytest
'''
local packages
'''
import requests
from src import config
from src.error import AccessError, InputError
import jwt
import json

BASE_URL = config.url

#FIXTURES
@pytest.fixture
def clear():
    clear_v1 = requests.delete(config.url + 'clear/v1')
    return clear_v1

#Owner of channel
@pytest.fixture
def token_jack():
    response = requests.post(
        config.url + 'auth/register/v2', json = {"email": "z5359521@ad.unsw.edu.au", "password": "Pass54321word", "name_first": "Jack", "name_last": "Hill"})
    return response.json()

@pytest.fixture
def channel_id_jack(token_jack):
    response = requests.post(
        config.url + 'channels/create/v2', json = {"token": token_jack['token'], "name": "jack_channel", "is_public": True})
    return response.json()

#User who is invited
@pytest.fixture
def token_sarah():
    response = requests.post(
        config.url + 'auth/register/v2', json = {"email": "z5363412@ad.unsw.edu.au", "password": "Parrrpp", "name_first": "Sarah", "name_last": "Cat"})
    return response.json()
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------
# CHANNELS_LISTALL (Get)

def test_one_user_channels_listall_v2(clear, token_jack, channel_id_jack):
    '''
    tests one user list
    '''
    res = requests.get(f'{BASE_URL}channels/listall/v2', params={'token': token_jack['token']})
    channel = res.json()
    assert res.status_code == 200
    assert len(channel['channels']) == 1

def test_incorrect_token_channels_listall(clear, token_jack, channel_id_jack):
    '''
    tests incorrect token
    '''
    res = requests.get(f'{BASE_URL}channels/listall/v2', params={'token': 'wrong'})
    assert res.status_code == 403

def test_multiple_channels_listall(clear, token_jack):
    '''
    tests multiple channels made in a list
    '''
    requests.post(f'{BASE_URL}channels/create/v2', json={'token': token_jack['token'], 'name': 'test_channel_1', 'is_public': True})
    requests.post(f'{BASE_URL}channels/create/v2', json={'token': token_jack['token'], 'name': 'test_channel_2', 'is_public': False})
    requests.post(f'{BASE_URL}channels/create/v2', json={'token': token_jack['token'], 'name': 'test_channel_3', 'is_public': True})
    res = requests.get(f'{BASE_URL}channels/listall/v2', params={'token': token_jack['token']})
    assert res.status_code == 200
    channel = res.json()
    assert len(channel['channels']) == 3

# ################################################################################################
# #TESTING FOR CHANNELS LIST

def test_single_channel_list(clear, token_jack, channel_id_jack):
    '''
    test the function works for one channel
    '''
    res = requests.get(f'{BASE_URL}channels/list/v2', params={'token': token_jack['token']})
    assert res.status_code == 200
    channel = res.json()
    assert len(channel['channels']) == 1


def test_incorrect_token_channels_list(clear, token_jack, channel_id_jack):
    '''
    incorrect user token
    '''
    res = requests.get(f'{BASE_URL}channels/list/v2', params={'token': "wrong"})
    assert res.status_code == 403

def test_multiple_channels_list(clear, token_jack, token_sarah):
    '''
    test function works for multiple channels and users
    '''
    requests.post(f'{BASE_URL}channels/create/v2', json={'token': token_jack['token'], 'name': 'test_channel_1', 'is_public': True})
    requests.post(f'{BASE_URL}channels/create/v2', json={'token': token_jack['token'], 'name': 'test_channel_2', 'is_public': False})
    requests.post(f'{BASE_URL}channels/create/v2', json={'token': token_sarah['token'], 'name': 'test_channel_3', 'is_public': True})
    requests.post(f'{BASE_URL}channels/create/v2', json={'token': token_sarah['token'], 'name': 'test_channel_4', 'is_public': False})
    res = requests.get(f'{BASE_URL}channels/list/v2', params={'token': token_jack['token']})
    assert res.status_code == 200
    channel = res.json()
    assert len(channel['channels']) == 2

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------
#TESTING FOR CHANNELS_CREATE_V2

#Unsuccessful Tests

#Input Error Expected
def test_channels_create_short_name_(clear, token_jack):
    '''
    Name length less than 1 character (Pub)
    ''' 
    
    response = requests.post(config.url + 'channels/create/v2',  json={"token": token_jack['token'], "name": '', "is_public": True})
    assert response.status_code == InputError().code

def test_channels_create_long_name(clear, token_jack):
    '''
    Name length more than 20 characters (Pub)
    '''
    response = requests.post(config.url + 'channels/create/v2',  json={"token": token_jack['token'], "name": 'namelengthmorethan20chars', "is_public": True})
    assert response.status_code == InputError().code

#Access Error Expected
def test_channels_create_invalid_token(clear):
    '''
    Name length more than 20 characters (Pub)
    '''
    response = requests.post(config.url + 'channels/create/v2',  json={"token": "-1234", "name": 'validname', "is_public": True})
    assert response.status_code == AccessError().code

def test_valid_create(clear, token_jack):
    '''
    working test
    ''' 
    response = requests.post(config.url + 'channels/create/v2',  json={"token": token_jack['token'], "name": 'validname', "is_public": True})
    assert response.status_code == 200

# INVALID TOKEN LOGOUT 
def test_invalid_token_channels_listall_logout(clear, token_jack, channel_id_jack, token_sarah):
    requests.post(config.url + 'auth/logout/v1', json={'token': token_jack['token']})
    response = requests.get(f'{BASE_URL}channels/listall/v2', params={'token': token_jack['token']})
    assert response.status_code == AccessError().code 

def test_invalid_token_channels_list_logout(clear, token_jack, channel_id_jack, token_sarah):
    requests.post(config.url + 'auth/logout/v1', json={'token': token_jack['token']})
    response = requests.get(f'{BASE_URL}channels/list/v2', params={'token': token_jack['token']})
    assert response.status_code == AccessError().code 

def test_invalid_token_channels_create_logout(clear, token_jack, channel_id_jack, token_sarah):
    requests.post(config.url + 'auth/logout/v1', json={'token': token_jack['token']})
    response = requests.post(config.url + 'channels/create/v2',  json={"token": token_jack['token'], "name": 'validname', "is_public": True})
    assert response.status_code == AccessError().code 


