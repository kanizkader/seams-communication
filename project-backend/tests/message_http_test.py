import pytest
import requests
from src import config
import json
from src.error import AccessError, InputError
import time
import datetime
from datetime import timezone


BASE_URL = config.url

# --------------------------------------------------------------------
# FIXTURES

@pytest.fixture
def clear():
    return requests.delete(f'{BASE_URL}clear/v1')

# Owner of channel
@pytest.fixture
def token_jack():
    response = requests.post(
        f'{BASE_URL}auth/register/v2', json = {'email': "z5359521@ad.unsw.edu.au", 'password': "Pass54321word", 'name_first': "Jack", 'name_last': "Hill"})
    return response.json()

@pytest.fixture
def channel_id_jack(token_jack):
    response = requests.post(
        f'{BASE_URL}channels/create/v2', json = {'token': token_jack['token'], 'name': "jack_channel", 'is_public': True})
    return response.json()

@pytest.fixture
def message_jack(token_jack, channel_id_jack):
    response = requests.get(
        f'{BASE_URL}channel/messages/v2', params = {'token': token_jack['token'], 'channel_id': channel_id_jack['channel_id'], "start": 0})
    return response.json()

@pytest.fixture
def message_id_jack(channel_id_jack, token_jack):
    response = requests.post(
        f'{BASE_URL}message/send/v1', json = {'token': token_jack['token'], 'channel_id': channel_id_jack['channel_id'], 'message': "Hi I am Jack"}
    )
    return response.json()

# Second User
@pytest.fixture
def token_sarah():
    response = requests.post(
        f'{BASE_URL}auth/register/v2', json = {'email': "z5363412@ad.unsw.edu.au", 'password': "Parrrpp", 'name_first': "Sarah", 'name_last': "Cat"})
    return response.json()
# Third User
@pytest.fixture
def token_phil():
    response = requests.post(
        f'{BASE_URL}auth/register/v2', json = {'email': "z5363124@ad.unsw.edu.au", 'password': "notamember!", 'name_first': "Phil", 'name_last': "Seed"})
    return response.json()


# TESTS ---------------- Messages_send_v1 ------------------

def test_message_send_invalid_token(clear, token_jack, token_sarah):
    '''
    test invalid token
    '''
    requests.post(f"{BASE_URL}/auth/logout/v1", json={'token': token_jack['token']})
    response = requests.post(f'{BASE_URL}message/send/v1', json = {
        'token': token_jack['token'],
        'channel_id': 1,
        'message': "a"
    })
    assert response.status_code == AccessError().code

# channel_id does not refer to valid channel
# fail response assert 400 otherwise 200 for success --> Input Error
def test_message_invalid_channel_id(clear, token_jack, token_sarah):
    '''
    test invalid channel id 
    '''

    invalid_id = 10000000
    response = requests.post(f'{BASE_URL}message/send/v1', json = {
        'token': token_jack['token'],
        'channel_id': invalid_id,
        'message': "Jack is my Name"
        # 'message': message_jack['messages']
    })
    assert response.status_code == InputError().code


def test_message_send_length_invalid(clear, token_jack, channel_id_jack):
    '''
    Length of message is less than 1 or over 1000 characters --> Input Error
    '''
    message = "a"
    for i in range(1001):
        message += f" {i}"
    response = requests.post(f'{BASE_URL}message/send/v1', json = {
        'token': token_jack['token'],
        'channel_id': channel_id_jack['channel_id'],
        'message': message
    })
    assert response.status_code == InputError().code

# Channel ID is valid but auth user is not member of channel --> Access Error

def test_message_send_invalid_member_channel(clear, token_phil, channel_id_jack, message_jack):
    response = requests.post(f'{BASE_URL}message/send/v1', json = {
        'token': token_phil['token'],
        'channel_id': channel_id_jack['channel_id'],
        'message': "Jack is my Name"
    })
    assert response.status_code == AccessError().code

def test_valid_send_message(clear, token_jack, channel_id_jack, message_jack):
    response = requests.post(f'{BASE_URL}message/send/v1', json = {
        'token': token_jack['token'],
        'channel_id': channel_id_jack['channel_id'],
        'message': "Jack is my Name"
    })
    assert response.status_code == 200


# # TESTS ---------------- Message/edit/v1 ------------------


def test_message_edit_invalid_token(clear, token_jack, token_sarah):
    '''
     Invalid Token
    '''
    requests.post(f"{BASE_URL}/auth/logout/v1", json={'token': token_jack['token']})
    response = requests.put(f'{BASE_URL}message/edit/v1', json = {
        'token': token_jack['token'],
        'message_id': 1,
        'message': "a"
    })
    assert response.status_code == AccessError().code

# Length of message is over 1000 characters --> input error
def test_message_edit_invalid_length(clear, token_jack, channel_id_jack):
    # message = "a"
    edit = "a"
    for i in range(1001):
        edit += f" {i}"
    r = requests.put(f'{BASE_URL}message/edit/v1', json = {
        'token': token_jack['token'],
        'message_id' : 1, 
        'message' : edit
    })
    assert r.status_code == InputError().code


# Message ID does not refer to a valid message within a channel/DM that the auth user has joined --> Input Error

def test_message_edit_invalid_message_id(clear, token_jack, channel_id_jack, message_id_jack):
    message = "Hey this is a test for edit"
    response = requests.put(f'{BASE_URL}message/edit/v1', json = {
        'token': token_jack['token'],
        'message_id': 1232322131,
        'message': message
    })
    assert response.status_code == InputError().code

# when message ID refers to a valid message ID in a joined channel/DM and the message was not sent by the authroised user making this req --> Access Error

# def test_message_edit_not_auth_user(clear, token_jack, channel_id_jack):
#     message = "Hello this is a test for edit"
#     edit = "edit"
#     response = requests.post(f'{BASE_URL}message/send/v1', json = {
#         'token': token_jack['token'],
#         'channel_id': channel_id_jack['channel_id'],
#         'message': message
#     })
#     message_id = response.json()
#     assert response.status_code == 200

#     response = requests.post(f'{BASE_URL}auth/logout/v1', json={'token': token_jack['token']})
#     assert response.status_code == 200

#     response = requests.put(f'{BASE_URL}message/edit/v1', json = {
#         'token': token_jack['token'],
#         'message_id': message_id['message_id'],
#         'message': edit
#     })
#     assert response.status_code == AccessError().code

# authorised user does not have permissions in the channel --> Access Error
def test_message_edit_auth_user_invalid_permission(clear, token_jack, token_sarah, token_phil, channel_id_jack):
    message = "Hello this is a test for invalid permission"
    edit = "edit"
    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_sarah['token'],
        'channel_id': channel_id_jack['channel_id']
    })
    assert response.status_code == 200

    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_phil['token'],
        'channel_id': channel_id_jack['channel_id']
    })
    assert response.status_code == 200

    response = requests.post(f'{BASE_URL}message/send/v1', json = {
        'token': token_jack['token'],
        'channel_id': channel_id_jack['channel_id'],
        'message': message
    })
    message_id = response.json()
    assert response.status_code == 200

    response = requests.put(f'{BASE_URL}message/edit/v1', json = {
        'token': token_phil['token'],
        'message_id': message_id['message_id'],
        'message': edit
    })

    assert response.status_code == AccessError().code

def test_message_invite_valid_owner(clear, token_jack, token_sarah, token_phil, channel_id_jack):
    message = "Hello this is a test for valid permission"
    edit = "edit"
    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_sarah['token'],
        'channel_id': channel_id_jack['channel_id']
    })
    assert response.status_code == 200

    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_phil['token'],
        'channel_id': channel_id_jack['channel_id']
    })
    assert response.status_code == 200

    response = requests.post(f'{BASE_URL}message/send/v1', json = {
        'token': token_jack['token'],
        'channel_id': channel_id_jack['channel_id'],
        'message': message
    })
    message_id = response.json()
    assert response.status_code == 200
    response = requests.put(f'{BASE_URL}message/edit/v1', json = {
        'token': token_jack['token'],
        'message_id': message_id['message_id'],
        'message': edit
    })
    assert response.status_code == 200

def test_message_invite_valid_sender(clear, token_jack, token_sarah, token_phil, channel_id_jack):
    message = "Hello this is a test for valid permission"
    edit = "edit"
    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_sarah['token'],
        'channel_id': channel_id_jack['channel_id']
    })
    assert response.status_code == 200
    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_phil['token'],
        'channel_id': channel_id_jack['channel_id']
    })
    assert response.status_code == 200
    response = requests.post(f'{BASE_URL}message/send/v1', json = {
        'token': token_sarah['token'],
        'channel_id': channel_id_jack['channel_id'],
        'message': message
    })
    assert response.status_code == 200
    message_id = response.json()
    response = requests.put(f'{BASE_URL}message/edit/v1', json = {
        'token': token_sarah['token'],
        'message_id': message_id['message_id'],
        'message': edit
    })
    assert response.status_code == 200

# test valid case for edit being '' --> deleting the message

def test_message_edit_empty_edit(clear, token_jack, channel_id_jack):
    message = "This is the message"
    edit = ""
    response = requests.post(f'{BASE_URL}message/send/v1', json = {
        'token': token_jack['token'],
        'channel_id': channel_id_jack['channel_id'],
        'message': message
    })
    message_id = response.json()
    response == requests.put(f'{BASE_URL}message/edit/v1', json = {
        'token': token_jack['token'],
        'message_id': message_id['message_id'],
        'message': edit
    })
    assert response.status_code == 200

def test_message_edit_global_owner(clear, token_jack, token_phil, token_sarah):
    
    response = requests.post(f'{BASE_URL}channels/create/v2', json = {
        'token': token_phil['token'], 
        'name': "phil_channel", 
        'is_public': True
    })
    channel = response.json()

    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_sarah['token'],
        'channel_id': channel['channel_id']
    })

    response = requests.post(f'{BASE_URL}message/send/v1', json = {
        'token': token_sarah['token'],
        'channel_id': channel['channel_id'],
        'message': "I am Sarah"
    })
    message = response.json()

    response = requests.put(f'{BASE_URL}message/edit/v1', json = {
        'token': token_jack['token'],
        'message_id': message['message_id'],
        'message': "Hi"
    })
    assert response.status_code == 200

# TESTS ---------------- Messages/remove/v1 ------------------

# Invalid Message ID --> Input Error

def test_message_remove_invalid_message_id(clear, token_jack, channel_id_jack):
    response = requests.post(f'{BASE_URL}message/send/v1', json = {
        'token': token_jack['token'],
        'channel_id': channel_id_jack['channel_id'],
        'message': "Hi"
    })
    assert response.status_code == 200
    response = requests.delete(f'{BASE_URL}message/remove/v1', json = {
        'token': token_jack['token'],
        'message_id': -1
    })
    assert response.status_code == InputError().code

# message sent by unauthorised user --> Access Error
def test_message_remove_invalid_user(clear, token_jack, token_sarah, channel_id_jack):
    message = "Hello this is a test for remove"
    
    response = requests.post(f'{BASE_URL}message/send/v1', json = {
        'token': token_jack['token'],
        'channel_id': channel_id_jack['channel_id'],
        'message': message
    })
    assert response.status_code == 200
    message_id = response.json()
    response = requests.post(f'{BASE_URL}auth/logout/v1', json = {'token': token_jack['token']})
    assert response.status_code == 200

    response = requests.post(f'{BASE_URL}auth/login/v2', json = {'email': 'z5363412@ad.unsw.edu.au', 'password': 'Parrrpp'})
    assert response.status_code == 200

    response = requests.delete(f'{BASE_URL}message/remove/v1', json = {
        'token': token_jack['token'],
        'message_id': message_id['message_id']
    })
    assert response.status_code == AccessError().code

# authorised user does not have permissions in the channel --> Access Error
def test_message_remove_invalid_permission(clear, token_jack, token_sarah, token_phil, channel_id_jack):
    message = "Hello this is a test for invalid permission"
    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_sarah['token'],
        'channel_id': channel_id_jack['channel_id']
    })
    assert response.status_code == 200

    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_phil['token'],
        'channel_id': channel_id_jack['channel_id']
    })
    assert response.status_code == 200

    response = requests.post(f'{BASE_URL}message/send/v1', json = {
        'token': token_sarah['token'],
        'channel_id': channel_id_jack['channel_id'],
        'message': message
    })
    assert response.status_code == 200

    message_id = response.json()
    response = requests.delete(f'{BASE_URL}message/remove/v1', json = {
        'token': token_phil['token'],
        'message_id': message_id['message_id']
    })
    assert response.status_code == AccessError().code

def test_message_remove_invalid_token(clear, token_jack, token_sarah):
    requests.post(f"{BASE_URL}/auth/logout/v1", json={'token': token_jack['token']})

    response = requests.delete(f'{BASE_URL}message/remove/v1', json = {
        'token': token_jack['token'],
        'message_id': 1
    })
    assert response.status_code == AccessError().code


def test_valid_sender_messages_remove(clear, token_jack, token_sarah, token_phil, channel_id_jack):
    message = "Hello this is a test for invalid permission"
    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_sarah['token'],
        'channel_id': channel_id_jack['channel_id']
    })
    assert response.status_code == 200

    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_phil['token'],
        'channel_id': channel_id_jack['channel_id']
    })
    assert response.status_code == 200

    response = requests.post(f'{BASE_URL}message/send/v1', json = {
        'token': token_sarah['token'],
        'channel_id': channel_id_jack['channel_id'],
        'message': message
    })
    assert response.status_code == 200

    message_id = response.json()
    response = requests.delete(f'{BASE_URL}message/remove/v1', json = {
        'token': token_sarah['token'],
        'message_id': message_id['message_id']
    })
    assert response.status_code == 200


def test_valid_owner_messages_remove(clear, token_jack, token_sarah, token_phil, channel_id_jack):
    message = "Hello this is a test for invalid permission"
    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_sarah['token'],
        'channel_id': channel_id_jack['channel_id']
    })
    assert response.status_code == 200

    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_phil['token'],
        'channel_id': channel_id_jack['channel_id']
    })
    assert response.status_code == 200

    response = requests.post(f'{BASE_URL}message/send/v1', json = {
        'token': token_jack['token'],
        'channel_id': channel_id_jack['channel_id'],
        'message': message
    })
    assert response.status_code == 200

    message_id = response.json()
    response = requests.delete(f'{BASE_URL}message/remove/v1', json = {
        'token': token_jack['token'],
        'message_id': message_id['message_id']
    })
    assert response.status_code == 200

# Valid tests for message remove

def test_message_remove_valid(clear, token_jack, channel_id_jack):
    response = requests.post(f'{BASE_URL}message/send/v1', json = {
        'token': token_jack['token'],
        'channel_id': channel_id_jack['channel_id'],
        'message': "Hi"
    })
    message_id = response.json()
    response == requests.delete(f'{BASE_URL}message/remove/v1', json = {
        'token': token_jack['token'],
        'message_id': message_id['message_id']
    })

    assert response.status_code == 200

def test_message_remove_valid_dm(clear, token_jack, token_sarah, channel_id_jack):
    r = requests.post(config.url + 'dm/create/v1',  json={'token': token_jack['token'], 'u_ids': [token_sarah['auth_user_id']]})
    dm_1 = r.json()
    r = requests.post(config.url + 'message/senddm/v1', json={'token': token_sarah['token'], 'dm_id': dm_1['dm_id'], 'message' : 'test message'})
    message_id = r.json()
    response = requests.delete(f'{BASE_URL}message/remove/v1', json = {
        'token': token_jack['token'],
        'message_id': message_id['message_id']
    })
    assert response.status_code == 200

def test_message_remove_owner_can_remove(clear, token_jack, channel_id_jack, token_sarah):
    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_sarah['token'],
        'channel_id': channel_id_jack['channel_id']
    })

    response = requests.post(f'{BASE_URL}message/send/v1', json = {
        'token': token_sarah['token'],
        'channel_id': channel_id_jack['channel_id'],
        'message': "I am Sarah"
    })
    message_id_sarah = response.json()
    response == requests.delete(f'{BASE_URL}message/remove/v1', json = {
        'token': token_jack['token'],
        'message_id': message_id_sarah['message_id']
    })

    assert response.status_code == 200
    
def test_message_remove_global_owner(clear, token_jack, token_phil, token_sarah):
    
    response = requests.post(f'{BASE_URL}channels/create/v2', json = {
        'token': token_phil['token'], 
        'name': "phil_channel", 
        'is_public': True
    })
    channel = response.json()

    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_sarah['token'],
        'channel_id': channel['channel_id']
    })

    response = requests.post(f'{BASE_URL}message/send/v1', json = {
        'token': token_sarah['token'],
        'channel_id': channel['channel_id'],
        'message': "I am Sarah"
    })
    message = response.json()

    response = requests.delete(f'{BASE_URL}message/remove/v1', json = {
        'token': token_jack['token'],
        'message_id': message['message_id']
    })
    assert response.status_code == 200

# ---------------------------------------------------------------------------------------------------
# message/pin/v1

def test_invalid_message_id_dm_pin(clear, token_jack, token_sarah):
    '''
    message_id is not a valid message within a DM that the authorised user has joined
    INPUT ERROR
    '''
    r = requests.post(config.url + 'dm/create/v1',  json={'token': token_jack['token'], 'u_ids': [token_sarah['auth_user_id']]})
    dm = r.json()
    requests.post(config.url + 'message/senddm/v1', json={'token': token_jack['token'],'dm_id': dm['dm_id'], 'message': 'test message'})
    r = requests.post(config.url + 'message/pin/v1', json={'token': token_jack['token'], 'message_id' : -1})
    assert r.status_code == InputError().code

def test_invalid_message_id_channel_pin(clear, token_jack, channel_id_jack):
    '''
    message_id is not a valid message within a channel that the authorised user has joined
    INPUT ERROR
    '''  
    r = requests.post(config.url + 'message/send/v1', json={'token': token_jack['token'], 'channel_id': channel_id_jack['channel_id'], 'message': 'hello'})
    r = requests.post(config.url + 'message/pin/v1', json={'token': token_jack['token'], 'message_id' : -1})
    assert r.status_code == InputError().code

def test_message_already_pinned_dm(clear, token_jack, token_sarah):
    '''
    the message is already pinned in DM
    INPUT ERROR
    '''
    r = requests.post(config.url + 'dm/create/v1',  json={'token': token_jack['token'], 'u_ids': [token_sarah['auth_user_id']]})
    dm = r.json()
    message_id = requests.post(config.url + 'message/senddm/v1', json={'token': token_jack['token'],'dm_id': dm['dm_id'], 'message': 'test message'})
    message = message_id.json()
    r = requests.post(config.url + 'message/pin/v1', json={'token': token_jack['token'], 'message_id' : message['message_id']})
    assert r.status_code == 200
    r = requests.post(config.url + 'message/pin/v1', json={'token': token_jack['token'], 'message_id' : message['message_id']})
    assert r.status_code == InputError().code
   
def test_message_already_pinned_channel(clear, token_jack, channel_id_jack):
    '''
    the message is already pinned in channel
    INPUT ERROR
    '''
    r = requests.post(config.url + 'message/send/v1', json={'token': token_jack['token'], 'channel_id': channel_id_jack['channel_id'], 'message': 'hello'})
    message = r.json()
    r = requests.post(config.url + 'message/pin/v1', json={'token': token_jack['token'], 'message_id' : message['message_id']})
    assert r.status_code == 200

    r = requests.post(config.url + 'message/pin/v1', json={'token': token_jack['token'], 'message_id' : message['message_id']})
    assert r.status_code == InputError().code

def test_message_pin_invalid_token_channel(clear, token_jack, channel_id_jack):
    '''
    invalid token for pinned message in channel
    ACCESS ERROR
    '''
    r = requests.post(config.url + 'message/send/v1', json={'token': token_jack['token'], 'channel_id': channel_id_jack['channel_id'], 'message': 'hello'})
    message = r.json()
    assert r.status_code == 200
    requests.post(f"{BASE_URL}/auth/logout/v1", json={'token': token_jack['token']})
    r = requests.post(config.url + 'message/pin/v1', json={'token': token_jack['token'], 'message_id' : message['message_id']})
    assert r.status_code == AccessError().code
      
def test_message_pin_invalid_token_dm(clear, token_jack, token_sarah):
    '''
    invalid token for pinned message in DM
    ACCESS ERROR
    '''
    r = requests.post(config.url + 'dm/create/v1',  json={'token': token_jack['token'], 'u_ids': [token_sarah['auth_user_id']]})
    dm = r.json()
    message_id = requests.post(config.url + 'message/senddm/v1', json={'token': token_jack['token'],'dm_id': dm['dm_id'], 'message': 'test message'})
    message = message_id.json()
    requests.post(f"{BASE_URL}/auth/logout/v1", json={'token': token_jack['token']})

    r = requests.post(config.url + 'message/pin/v1', json={'token': token_jack['token'], 'message_id' : message['message_id']})
    assert r.status_code == AccessError().code
    
def test_message_pin_invalid_channel_owner(clear, token_jack, token_sarah, channel_id_jack): 
    '''
    message_id refers to a valid message in a joined channel and 
    the authorised user does not have owner permissions in the channel
    ACCESS ERROR
    '''
    r = requests.post(config.url + 'message/send/v1', json={'token': token_jack['token'], 'channel_id': channel_id_jack['channel_id'], 'message': 'hello'})
    message = r.json()

    r = requests.post(config.url + 'message/pin/v1', json={'token': token_sarah['token'], 'message_id' : message['message_id']})
    assert r.status_code == AccessError().code

def test_message_pin_invalid_dm_owner(clear, token_jack, token_sarah): 
    '''
    message_id refers to a valid message in a joined DM and 
    the authorised user does not have owner permissions in the DM
    ACCESS ERROR
    '''
    r = requests.post(config.url + 'dm/create/v1',  json={'token': token_jack['token'], 'u_ids': [token_sarah['auth_user_id']]})
    dm = r.json()
    message_id = requests.post(config.url + 'message/senddm/v1', json={'token': token_jack['token'],'dm_id': dm['dm_id'], 'message': 'test message'})
    message = message_id.json()
  
    r = requests.post(config.url + 'message/pin/v1', json={'token': token_sarah['token'], 'message_id' : message['message_id']})
    assert r.status_code == AccessError().code

def test_messsage_pin_valid_dm(clear, token_jack, token_sarah):
    r = requests.post(config.url + 'dm/create/v1',  json={'token': token_jack['token'], 'u_ids': [token_sarah['auth_user_id']]})
    dm = r.json()
    message_id = requests.post(config.url + 'message/senddm/v1', json={'token': token_jack['token'],'dm_id': dm['dm_id'], 'message': 'test message'})
    message = message_id.json()
    r = requests.post(config.url + 'message/pin/v1', json={'token': token_jack['token'], 'message_id' : message['message_id']})
    assert r.status_code == 200
    
def test_messsage_pin_valid_channel(clear, token_jack, channel_id_jack):
    r = requests.post(config.url + 'message/send/v1', json={'token': token_jack['token'], 'channel_id': channel_id_jack['channel_id'], 'message': 'hello'})
    message = r.json()
    r = requests.post(config.url + 'message/pin/v1', json={'token': token_jack['token'], 'message_id' : message['message_id']})
    assert r.status_code == 200
# ---------------------------------------------------------------------------------------------------
# message/unpin/v1

def test_invalid_message_id_unpin_dm(clear, token_jack, token_sarah):
    '''
    message_id is not a valid message within a DM that the authorised user has joined
    INPUT ERROR
    '''
    r = requests.post(config.url + 'dm/create/v1',  json={'token': token_jack['token'], 'u_ids': [token_sarah['auth_user_id']]})
    dm = r.json()
    message_id = requests.post(config.url + 'message/senddm/v1', json={'token': token_jack['token'],'dm_id': dm['dm_id'], 'message': 'test message'})
    message = message_id.json()
    r = requests.post(config.url + 'message/pin/v1', json={'token': token_jack['token'], 'message_id' : message['message_id']})
    assert r.status_code == 200
    r = requests.post(config.url + 'message/unpin/v1', json={'token': token_jack['token'], 'message_id' : -1})
    assert r.status_code == InputError().code
    

def test_invalid_message_id_unpin_channel(clear, token_jack, channel_id_jack):
    '''
    message_id is not a valid message within a channel that the authorised user has joined
    INPUT ERROR
    '''
    r = requests.post(config.url + 'message/send/v1', json={'token': token_jack['token'], 'channel_id': channel_id_jack['channel_id'], 'message': 'hello'})
    message = r.json()
    r = requests.post(config.url + 'message/pin/v1', json={'token': token_jack['token'], 'message_id' : message['message_id']})
    assert r.status_code == 200
    r = requests.post(config.url + 'message/unpin/v1', json={'token': token_jack['token'], 'message_id' : -1})
    assert r.status_code == InputError().code

def test_message_not_pinned_dm(clear, token_jack, token_sarah):
    '''
    the message is not already pinned in dm
    INPUT ERROR
    '''
    r = requests.post(config.url + 'dm/create/v1',  json={'token': token_jack['token'], 'u_ids': [token_sarah['auth_user_id']]})
    dm = r.json()
    message_id = requests.post(config.url + 'message/senddm/v1', json={'token': token_jack['token'],'dm_id': dm['dm_id'], 'message': 'test message'})
    message = message_id.json()
    r = requests.post(config.url + 'message/unpin/v1', json={'token': token_jack['token'], 'message_id' : message['message_id']})
    assert r.status_code == InputError().code

def test_message_not_pinned_channel(clear, token_jack, channel_id_jack):
    '''
    the message is not already pinned in channel
    INPUT ERROR
    '''
    r = requests.post(config.url + 'message/send/v1', json={'token': token_jack['token'], 'channel_id': channel_id_jack['channel_id'], 'message': 'hello'})
    message = r.json()
    r = requests.post(config.url + 'message/unpin/v1', json={'token': token_jack['token'], 'message_id' : message['message_id']})
    assert r.status_code == InputError().code

def test_message_unpin_invalid_token_dm(clear, token_jack, token_sarah):
    '''
    invalid token
    ACCESS ERROR
    '''
    r = requests.post(config.url + 'dm/create/v1',  json={'token': token_jack['token'], 'u_ids': [token_sarah['auth_user_id']]})
    dm = r.json()
    message_id = requests.post(config.url + 'message/senddm/v1', json={'token': token_jack['token'],'dm_id': dm['dm_id'], 'message': 'test message'})
    message = message_id.json()
    r = requests.post(config.url + 'message/pin/v1', json={'token': token_jack['token'], 'message_id' : message['message_id']})
    requests.post(f"{BASE_URL}/auth/logout/v1", json={'token': token_jack['token']})

    r = requests.post(config.url + 'message/unpin/v1', json={'token': token_jack['token'], 'message_id' : message['message_id']})    
    assert r.status_code == AccessError().code

def test_message_unpin_invalid_token_channel(clear, token_jack, channel_id_jack):
    '''
    invalid token 
    ACCESS ERROR
    '''
    r = requests.post(config.url + 'message/send/v1', json={'token': token_jack['token'], 'channel_id': channel_id_jack['channel_id'], 'message': 'hello'})
    message = r.json()
    assert r.status_code == 200
    r = requests.post(config.url + 'message/pin/v1', json={'token': token_jack['token'], 'message_id' : message['message_id']})
    requests.post(f"{BASE_URL}/auth/logout/v1", json={'token': token_jack['token']})
    r = requests.post(config.url + 'message/unpin/v1', json={'token': token_jack['token'], 'message_id' : message['message_id']})
    assert r.status_code == AccessError().code

def test_message_unpin_invalid_channel_owner(clear, token_jack, channel_id_jack, token_sarah):
    '''
    message_id refers to a valid message in a joined channel and 
    the authorised user does not have owner permissions in the channel
    ACCESS ERROR
    '''
    r = requests.post(config.url + 'message/send/v1', json={'token': token_jack['token'], 'channel_id': channel_id_jack['channel_id'], 'message': 'hello'})
    message = r.json()

    r = requests.post(config.url + 'message/pin/v1', json={'token': token_jack['token'], 'message_id' : message['message_id']})
    r = requests.post(config.url + 'message/pin/v1', json={'token': token_sarah['token'], 'message_id' : message['message_id']})

    assert r.status_code == AccessError().code

def test_message_unpin_invalid_dm_owner(clear, token_jack, token_sarah):
    '''
    message_id refers to a valid message in a joined DM and 
    the authorised user does not have owner permissions in the DM
    ACCESS ERROR
    '''
    r = requests.post(config.url + 'dm/create/v1',  json={'token': token_jack['token'], 'u_ids': [token_sarah['auth_user_id']]})
    dm = r.json()
    message_id = requests.post(config.url + 'message/senddm/v1', json={'token': token_jack['token'],'dm_id': dm['dm_id'], 'message': 'test message'})
    message = message_id.json()
  
    r = requests.post(config.url + 'message/pin/v1', json={'token': token_jack['token'], 'message_id' : message['message_id']})
    r = requests.post(config.url + 'message/unpin/v1', json={'token': token_sarah['token'], 'message_id' : message['message_id']})
    assert r.status_code == AccessError().code

def test_message_unpin_valid_dm(clear, token_jack, token_sarah):
    r = requests.post(config.url + 'dm/create/v1',  json={'token': token_jack['token'], 'u_ids': [token_sarah['auth_user_id']]})
    dm = r.json()
    message_id = requests.post(config.url + 'message/senddm/v1', json={'token': token_jack['token'],'dm_id': dm['dm_id'], 'message': 'test message'})
    message = message_id.json()
  
    requests.post(config.url + 'message/pin/v1', json={'token': token_jack['token'], 'message_id' : message['message_id']})
    r = requests.post(config.url + 'message/unpin/v1', json={'token': token_jack['token'], 'message_id' : message['message_id']})
    assert r.status_code == 200

def test_message_unpin_valid_channel(clear, token_jack, channel_id_jack):
    r = requests.post(config.url + 'message/send/v1', json={'token': token_jack['token'], 'channel_id': channel_id_jack['channel_id'], 'message': 'hello'})
    message = r.json()
    requests.post(config.url + 'message/pin/v1', json={'token': token_jack['token'], 'message_id' : message['message_id']})
    r = requests.post(config.url + 'message/unpin/v1', json={'token': token_jack['token'], 'message_id' : message['message_id']})
    assert r.status_code == 200

# ---------------------------------------------------------------------------------------------------
#------------------ TESTS FOR message/share/v1 --------------------#

# Both channel ID and dm ID are invalid --> Input Error

def test_message_share_invalid_channel_dm(clear, token_jack, channel_id_jack, token_sarah):
    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_sarah['token'],
        'channel_id': channel_id_jack['channel_id']
    })

    response = requests.post(f'{BASE_URL}dm/create/v1', json = {
        'token': token_jack['token'],
        'u_ids': [token_sarah['auth_user_id']]
    })
    assert response.status_code == 200
    created_dm = response.json()

    response = requests.post(f'{BASE_URL}message/senddm/v1', json = {
        'token': token_jack['token'],
        'dm_id': created_dm['dm_id'],
        'message': "Hi i am Jack"
    })
    assert response.status_code == 200
    message_id = response.json()

    response = requests.post(f'{BASE_URL}message/share/v1', json = {
        'token': token_jack['token'],
        'og_message_id': message_id['message_id'],
        'message': "Hi i am jack",
        'channel_id': 1232424,
        'dm_id': '12'
    })
    assert response.status_code  == InputError().code


# Error when message_id is invalid --> Input
def test_message_share_invalid_message_id(clear, token_jack, token_sarah, channel_id_jack):
    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_sarah['token'],
        'channel_id': channel_id_jack['channel_id']
    })

    response = requests.post(f'{BASE_URL}dm/create/v1', json = {
        'token': token_jack['token'],
        'u_ids': [token_sarah['auth_user_id']]
    })
    assert response.status_code == 200
    created_dm = response.json()

    response = requests.post(f'{BASE_URL}message/senddm/v1', json = {
        'token': token_jack['token'],
        'dm_id': created_dm['dm_id'],
        'message': "Hi i am Jack"
    })
    assert response.status_code == 200

    response = requests.post(f'{BASE_URL}message/share/v1', json = {
        'token': token_jack['token'],
        'og_message_id': 982372,
        'message': "Hi i am jack",
        'channel_id': channel_id_jack['channel_id'],
        'dm_id': created_dm['dm_id']
    })
    assert response.status_code  == InputError().code

# channel ID that user is sharing to or the dm_id is incorrect --> AccessError 

def test_message_share_invalid_access_channel_dm(clear, token_sarah, token_jack, channel_id_jack):
    response = requests.post(f'{BASE_URL}dm/create/v1', json = {
        'token': token_sarah['token'],
        'u_ids': [token_jack['auth_user_id']]
    })
    assert response.status_code == 200
    created_dm = response.json()

    response = requests.post(f'{BASE_URL}message/senddm/v1', json = {
        'token': token_sarah['token'],
        'dm_id': created_dm['dm_id'],
        'message': "Hi i am Sarah"
    })
    assert response.status_code == 200
    message_id = response.json()

    response = requests.post(f'{BASE_URL}message/share/v1', json = {
        'token': token_sarah['token'],
        'og_message_id': message_id['message_id'],
        'message': "Hi i am jack",
        'channel_id': channel_id_jack['channel_id'],
        'dm_id': created_dm['dm_id']
    })
    assert response.status_code  == AccessError().code

def test_message_share_valid(clear, token_sarah, token_jack, channel_id_jack):
    response = requests.post(f'{BASE_URL}dm/create/v1', json = {
        'token': token_sarah['token'],
        'u_ids': [token_jack['auth_user_id']]
    })
    assert response.status_code == 200
    created_dm = response.json()

    response = requests.post(f'{BASE_URL}message/senddm/v1', json = {
        'token': token_sarah['token'],
        'dm_id': created_dm['dm_id'],
        'message': "Hi i am Sarah"
    })
    assert response.status_code == 200
    message_id = response.json()

    response = requests.post(f'{BASE_URL}message/share/v1', json = {
        'token': token_jack['token'],
        'og_message_id': message_id['message_id'],
        'message': "Hi i am jack",
        'channel_id': channel_id_jack['channel_id'],
        'dm_id': created_dm['dm_id']
    })
    assert response.status_code  == 200

#------------------ TESTS FOR message/react/v1 --------------------#

# INVALID MESSAGE_ID

def test_message_react_invalid_message_id(clear, token_sarah, token_jack, channel_id_jack):
    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_sarah['token'],
        'channel_id': channel_id_jack['channel_id']
    })

    response = requests.post(f'{BASE_URL}dm/create/v1', json = {
        'token': token_jack['token'],
        'u_ids': [token_sarah['auth_user_id']]
    })
    assert response.status_code == 200
    created_dm = response.json()

    response = requests.post(f'{BASE_URL}message/senddm/v1', json = {
        'token': token_jack['token'],
        'dm_id': created_dm['dm_id'],
        'message': "Hi i am Jack"
    })
    assert response.status_code == 200

    response = requests.post(f'{BASE_URL}message/react/v1', json = {
        'token': token_jack['token'],
        'message_id': -1023,
        'react_id': 10
    })
    assert response.status_code  == InputError().code

# INVALID REACT ID

def test_message_react_invalid_react_id(clear, token_jack, token_sarah, channel_id_jack):
    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_sarah['token'],
        'channel_id': channel_id_jack['channel_id']
    })

    response = requests.post(f'{BASE_URL}dm/create/v1', json = {
        'token': token_jack['token'],
        'u_ids': [token_sarah['auth_user_id']]
    })
    assert response.status_code == 200
    created_dm = response.json()

    response = requests.post(f'{BASE_URL}message/senddm/v1', json = {
        'token': token_jack['token'],
        'dm_id': created_dm['dm_id'],
        'message': "Hi i am Jack"
    })
    assert response.status_code == 200
    message_id = response.json()

    response = requests.post(f'{BASE_URL}message/react/v1', json = {
        'token': token_jack['token'],
        'message_id': message_id['message_id'],
        'react_id': 10
    })
    assert response.status_code  == InputError().code

# message already contains a react with ID react_id
def test_message_react_already_reacted(clear, token_sarah, token_jack, channel_id_jack):
    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_sarah['token'],
        'channel_id': channel_id_jack['channel_id']
    })

    response = requests.post(f'{BASE_URL}dm/create/v1', json = {
        'token': token_jack['token'],
        'u_ids': [token_sarah['auth_user_id']]
    })
    assert response.status_code == 200
    created_dm = response.json()

    response = requests.post(f'{BASE_URL}message/senddm/v1', json = {
        'token': token_jack['token'],
        'dm_id': created_dm['dm_id'],
        'message': "Hi i am Jack"
    })
    assert response.status_code == 200
    message_id = response.json()

    response = requests.post(f'{BASE_URL}message/react/v1', json = {
        'token': token_jack['token'],
        'message_id': message_id['message_id'],
        'react_id': 1
    })

    response = requests.post(f'{BASE_URL}message/react/v1', json = {
        'token': token_jack['token'],
        'message_id': message_id['message_id'],
        'react_id': 1
    })
    assert response.status_code  == InputError().code

def test_message_react_valid(clear, token_sarah, token_jack, channel_id_jack):
    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_sarah['token'],
        'channel_id': channel_id_jack['channel_id']
    })

    response = requests.post(f'{BASE_URL}dm/create/v1', json = {
        'token': token_jack['token'],
        'u_ids': [token_sarah['auth_user_id']]
    })
    assert response.status_code == 200
    created_dm = response.json()

    response = requests.post(f'{BASE_URL}message/senddm/v1', json = {
        'token': token_jack['token'],
        'dm_id': created_dm['dm_id'],
        'message': "Hi i am Jack"
    })
    assert response.status_code == 200
    message_id = response.json()

    response = requests.post(f'{BASE_URL}message/react/v1', json = {
        'token': token_jack['token'],
        'message_id': message_id['message_id'],
        'react_id': 1
    })
    assert response.status_code == 200

def test_message_react_valid_channel(clear, token_jack, token_sarah, channel_id_jack):
    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_sarah['token'],
        'channel_id': channel_id_jack['channel_id']
    })
    r = requests.post(config.url + 'message/send/v1', json={'token': token_jack['token'], 'channel_id': channel_id_jack['channel_id'], 'message': 'hello'})
    assert r.status_code == 200
    message_id = r.json()
    response = requests.post(f'{BASE_URL}message/react/v1', json = {
        'token': token_jack['token'],
        'message_id': message_id['message_id'],
        'react_id': 1
    })
    assert response.status_code == 200

#------------------ TESTS FOR message/unreact/v1 --------------------#

#invalid message ID

def test_message_unreact_invalid_message_id(clear, token_jack, token_sarah, channel_id_jack):
    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_sarah['token'],
        'channel_id': channel_id_jack['channel_id']
    })

    response = requests.post(f'{BASE_URL}dm/create/v1', json = {
        'token': token_jack['token'],
        'u_ids': [token_sarah['auth_user_id']]
    })
    assert response.status_code == 200
    created_dm = response.json()

    response = requests.post(f'{BASE_URL}message/senddm/v1', json = {
        'token': token_jack['token'],
        'dm_id': created_dm['dm_id'],
        'message': "Hi i am Jack"
    })
    assert response.status_code == 200
    message_id = response.json()

    response = requests.post(f'{BASE_URL}message/react/v1', json = {
        'token': token_jack['token'],
        'message_id': message_id['message_id'],
        'react_id': 1
    })
    response = requests.post(f'{BASE_URL}message/unreact/v1', json = {
        'token': token_jack['token'],
        'message_id': '-102',
        'react_id': 1
    })
    assert response.status_code  == InputError().code

#invalid react ID

def test_message_unreact_invalid_react_id(clear, token_jack, token_sarah, channel_id_jack):
    
    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_sarah['token'],
        'channel_id': channel_id_jack['channel_id']
    })

    response = requests.post(f'{BASE_URL}dm/create/v1', json = {
        'token': token_jack['token'],
        'u_ids': [token_sarah['auth_user_id']]
    })
    assert response.status_code == 200
    created_dm = response.json()

    response = requests.post(f'{BASE_URL}message/senddm/v1', json = {
        'token': token_jack['token'],
        'dm_id': created_dm['dm_id'],
        'message': "Hi i am Jack"
    })
    assert response.status_code == 200
    message_id = response.json()

    response = requests.post(f'{BASE_URL}message/react/v1', json = {
        'token': token_jack['token'],
        'message_id': message_id['message_id'],
        'react_id': 1
    })
    response = requests.post(f'{BASE_URL}message/unreact/v1', json = {
        'token': token_jack['token'],
        'message_id': message_id['message_id'],
        'react_id': 10
    })
    assert response.status_code  == InputError().code

#there is no initial react made to be removed

def test_message_unreact_react_doesnt_exist(clear, token_jack, token_sarah, channel_id_jack):
    
    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_sarah['token'],
        'channel_id': channel_id_jack['channel_id']
    })

    response = requests.post(f'{BASE_URL}dm/create/v1', json = {
        'token': token_jack['token'],
        'u_ids': [token_sarah['auth_user_id']]
    })
    assert response.status_code == 200
    created_dm = response.json()

    response = requests.post(f'{BASE_URL}message/senddm/v1', json = {
        'token': token_jack['token'],
        'dm_id': created_dm['dm_id'],
        'message': "Hi i am Jack"
    })
    assert response.status_code == 200
    message_id = response.json()

    response = requests.post(f'{BASE_URL}message/unreact/v1', json = {
        'token': token_jack['token'],
        'message_id': message_id['message_id'],
        'react_id': 1
    })
    assert response.status_code  == InputError().code

def test_message_unreact_valid(clear, token_sarah, token_jack, channel_id_jack):
    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_sarah['token'],
        'channel_id': channel_id_jack['channel_id']
    })

    response = requests.post(f'{BASE_URL}dm/create/v1', json = {
        'token': token_jack['token'],
        'u_ids': [token_sarah['auth_user_id']]
    })
    assert response.status_code == 200
    created_dm = response.json()

    response = requests.post(f'{BASE_URL}message/senddm/v1', json = {
        'token': token_jack['token'],
        'dm_id': created_dm['dm_id'],
        'message': "Hi i am Jack"
    })
    assert response.status_code == 200
    message_id = response.json()

    response = requests.post(f'{BASE_URL}message/react/v1', json = {
        'token': token_jack['token'],
        'message_id': message_id['message_id'],
        'react_id': 1
    })
    response = requests.post(f'{BASE_URL}message/unreact/v1', json = {
        'token': token_jack['token'],
        'message_id': message_id['message_id'],
        'react_id': 1
    })
    assert response.status_code == 200

def test_message_unreact_valid_channel(clear, token_jack, token_sarah, channel_id_jack):
    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_sarah['token'],
        'channel_id': channel_id_jack['channel_id']
    })
    r = requests.post(config.url + 'message/send/v1', json={'token': token_jack['token'], 'channel_id': channel_id_jack['channel_id'], 'message': 'hello'})
    message_id = r.json()
    assert r.status_code == 200

    response = requests.post(f'{BASE_URL}message/react/v1', json = {
        'token': token_jack['token'],
        'message_id': message_id['message_id'],
        'react_id': 1
    })
    response = requests.post(f'{BASE_URL}message/unreact/v1', json = {
        'token': token_jack['token'],
        'message_id': message_id['message_id'],
        'react_id': 1
    })
    assert response.status_code == 200
