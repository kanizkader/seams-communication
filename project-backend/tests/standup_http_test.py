'''
pip3 packages
'''
import datetime
import pytest
'''
local packages
'''
from src.data_store import data_store
import requests
from src import config
from src.error import AccessError, InputError
import jwt
import json

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

@pytest.fixture
def invite_sarah(token_jack, channel_id_jack, token_sarah):
    response = requests.post(
        config.url + 'channel/invite/v2', json = {"token": token_jack['token'], "channel_id": channel_id_jack['channel_id'], "u_id": token_sarah['auth_user_id']})
    return response.json()

#Not a member of channel
@pytest.fixture
def token_phil():
    response = requests.post(
        config.url + 'auth/register/v2', json = {"email": "z5363124@ad.unsw.edu.au", "password": "notamember!", "name_first": "Phil", "name_last": "Seed"})
    return response.json()

#Only one instance where Phil is considered a member 
@pytest.fixture
def invite_phil(token_jack, channel_id_jack, token_phil):
    response = requests.post(
        config.url + 'channel/invite/v2', json = {"token": token_jack['token'], "channel_id": channel_id_jack['channel_id'], "u_id": token_phil['auth_user_id']})
    return response.json()

# TESTS FOR STANDUP START V1
###################################################################################################################################################################################################
def test_standup_start_successful(clear, token_jack, channel_id_jack):
    '''
    standup successfully starts
    '''
    response = requests.post(
        config.url + 'standup/start/v1', json = {
            "token": token_jack['token'],
            "channel_id": channel_id_jack['channel_id'],
            "length": 10
        }
    )
    assert response.status_code == 200

def test_standup_start_invalid_channel(clear, token_jack, channel_id_jack):
    '''
    invalid channel_id input
    '''
    response = requests.post(
        config.url + 'standup/start/v1', json = {
            "token": token_jack['token'],
            "channel_id": "-1234",
            "length": 1
        }
    )
    assert response.status_code == InputError().code

def test_standup_start_neg_length(clear, token_jack, channel_id_jack):
    '''
    negative integer input for length of time standup is active for
    '''
    response = requests.post(
        config.url + 'standup/start/v1', json = {
            "token": token_jack['token'],
            "channel_id": channel_id_jack['channel_id'],
            "length": -100
        }
    )
    assert response.status_code == InputError().code

def test_standup_start_already_active(clear, token_jack, channel_id_jack):
    '''
    when an active standup is already running
    '''
    response = requests.post(
        config.url + 'standup/start/v1', json = {
            "token": token_jack['token'],
            "channel_id": channel_id_jack['channel_id'],
            "length": 10
        }
    )

    response = requests.post(
        config.url + 'standup/start/v1', json = {
            "token": token_jack['token'],
            "channel_id": channel_id_jack['channel_id'],
            "length": 13
        }
    )
    assert response.status_code == InputError().code

def test_standup_start_not_member(clear, channel_id_jack, token_sarah):
    '''
    when user is not a valid member of the channel
    ''' 
    response = requests.post(
        config.url + 'standup/start/v1', json = {
            "token": token_sarah['token'],
            "channel_id": channel_id_jack['channel_id'],
            "length": 10
        }
    )
    assert response.status_code == AccessError().code

# TESTS FOR STANDUP ACTIVE V1
###################################################################################################################################################################################################

def test_standup_active_invalid_channel(clear, token_jack, channel_id_jack):
    '''
    invalid channel_id input
    '''
    response = requests.post(
        config.url + 'standup/start/v1', json = {
            "token": token_jack['token'],
            "channel_id": channel_id_jack['channel_id'],
            "length": 10
        }
    )
    response = requests.get(
        config.url + 'standup/active/v1', params = {
            "token": token_jack['token'],
            "channel_id": "-1234",
        }
    )
    assert response.status_code == InputError().code

def test_standup_active_not_member(clear, token_jack, channel_id_jack, token_sarah):
    '''
    when user is not a valid member of the channel
    ''' 
    response = requests.post(
        config.url + 'standup/start/v1', json = {
            "token": token_jack['token'],
            "channel_id": channel_id_jack['channel_id'],
            "length": 10
        }
    )
    response = requests.get(
        config.url + 'standup/active/v1', params = {
            "token": token_sarah['token'],
            "channel_id": channel_id_jack['channel_id'],
        }
    )
    assert response.status_code == AccessError().code

def test_standup_active_not_active(clear, token_jack, channel_id_jack):
    '''
    when standup is not active
    '''
    response = requests.get(
        config.url + 'standup/active/v1', params = {
            "token": token_jack['token'],
            "channel_id": channel_id_jack['channel_id'],
        }
    )
    assert response.json() == {'is_active': False, 'time_finish': None}

def test_standup_active_active(clear, token_jack, channel_id_jack):
    '''
    when standup is active
    '''
    response = requests.post(
        config.url + 'standup/start/v1', json = {
            "token": token_jack['token'],
            "channel_id": channel_id_jack['channel_id'],
            "length": 10
        }
    )
    standup = response.json()
    response = requests.get(
        config.url + 'standup/active/v1', params = {
            "token": token_jack['token'],
            "channel_id": channel_id_jack['channel_id'],
        }
    )
    assert response.json() == {'is_active': True, 'time_finish': standup['time_finish']}

# TESTS FOR STANDUP SEND V1
###################################################################################################################################################################################################

def test_standup_send_successful(clear, token_jack, channel_id_jack):
    '''
    when standup sends messages in queue successfully
    '''
    response = requests.post(
        config.url + 'standup/start/v1', json = {
            "token": token_jack['token'],
            "channel_id": channel_id_jack['channel_id'],
            "length": 10
        }
    )
    response = requests.post(
        config.url + 'standup/send/v1', json = {
            "token": token_jack['token'],
            "channel_id": channel_id_jack['channel_id'],
            "message": "message successfully sent"
        }
    )
    assert response.json() == {}

def test_standup_send_invalid_channel(clear, token_jack, channel_id_jack):
    '''
    when invalid channel_id is input
    '''
    response = requests.post(
        config.url + 'standup/start/v1', json = {
            "token": token_jack['token'],
            "channel_id": channel_id_jack['channel_id'],
            "length": 10
        }
    )
    response = requests.post(
        config.url + 'standup/send/v1', json = {
            "token": token_jack['token'],
            "channel_id": "-1234",
            "message": "invalid channel test"
        }
    )
    assert response.status_code == InputError().code

def test_standup_send_long_message(clear, token_jack, channel_id_jack):
    '''
    when length of message is greater than 1000 characters
    '''
    response = requests.post(
        config.url + 'standup/start/v1', json = {
            "token": token_jack['token'],
            "channel_id": channel_id_jack['channel_id'],
            "length": 10
        }
    )
    response = requests.post(
        config.url + 'standup/send/v1', json = {
            "token": token_jack['token'],
            "channel_id": channel_id_jack['channel_id'],
            "message": "message" * 1000
        }
    )
    assert response.status_code == InputError().code

def test_standup_send_not_active(clear, token_jack, channel_id_jack):
    '''
    when standup is not active
    '''
    response = requests.post(
        config.url + 'standup/send/v1', json = {
            "token": token_jack['token'],
            "channel_id": channel_id_jack['channel_id'],
            "message": "message"
        }
    )
    assert response.status_code == InputError().code

def test_standup_active_not_member_send(clear, token_jack, channel_id_jack, token_sarah):
    '''
    when user trying to use the function is not a member of the channel
    '''
    response = requests.post(
        config.url + 'standup/start/v1', json = {
            "token": token_jack['token'],
            "channel_id": channel_id_jack['channel_id'],
            "length": 10
        }
    )
    response = requests.post(
        config.url + 'standup/send/v1', json = {
            "token": token_sarah['token'],
            "channel_id": channel_id_jack['channel_id'],
            "message": "not member of channel"
        }
    )
    assert response.status_code == AccessError().code
    
