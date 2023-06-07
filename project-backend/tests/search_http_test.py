'''
pip3 packages
'''
from urllib import response
import pytest
'''
local packages
'''
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

# Tests for search_v1
###############################################################################################################################################################################################
def test_search_valid(clear, token_jack, channel_id_jack, invite_sarah, token_sarah):
    response = requests.post(
        config.url + 'message/send/v1', json = {
            "token": token_sarah['token'],
            "channel_id": channel_id_jack['channel_id'],
            "message": "testing the search function"
        }
    )
    
    response = requests.get(
        config.url + 'search/v1', params = {
            "token": token_sarah['token'],
            "query_str": "testing the search"
        }
    )
    assert response.status_code == 200

def test_search_too_long(clear, token_jack, channel_id_jack, invite_sarah, token_sarah):
    response = requests.post(
        config.url + 'message/send/v1', json = {
            "token": token_sarah['token'],
            "channel_id": channel_id_jack['channel_id'],
            "message": "testing the search function"
        }
    )
    
    response = requests.get(
        config.url + 'search/v1', params = {
            "token": token_sarah['token'],
            "query_str": "test" * 1000
        }
    )
    assert response.status_code == InputError().code

def test_search_invalid_user(clear, token_jack, channel_id_jack, token_phil):
    response = requests.post(
        config.url + 'message/send/v1', json = {
            "token": token_jack['token'],
            "channel_id": channel_id_jack['channel_id'],
            "message": "testing the search function"
        }
    )
    
    response = requests.get(
        config.url + 'search/v1', params = {
            "token": token_phil['token'],
            "query_str": "testing the search"
        }
    )
    assert response.status_code == 200
