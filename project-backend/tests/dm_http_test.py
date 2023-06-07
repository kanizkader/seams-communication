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
import time
import datetime
from datetime import timezone
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------
BASE_URL = config.url
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------
# FIXTURES
@pytest.fixture
def clear():
    return requests.delete(f"{BASE_URL}clear/v1")

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

@pytest.fixture
def token_sarah():
    response = requests.post(
        config.url + 'auth/register/v2', json = {"email": "z5363412@ad.unsw.edu.au", "password": "Parrrpp", "name_first": "Sarah", "name_last": "Cat"})
    return response.json()

@pytest.fixture
def token_phil():
    response = requests.post(
        config.url + 'auth/register/v2', json = {"email": "z5363124@ad.unsw.edu.au", "password": "notamember!", "name_first": "Phil", "name_last": "Seed"})
    return response.json()

@pytest.fixture
def dm_create_jack(token_jack, token_sarah):
    response = requests.post(f"{BASE_URL}dm/create/v1", json={'token': token_jack['token'], 'u_ids': [token_sarah['auth_user_id']]})
    return response.json()

@pytest.fixture
def senddm_jack(token_jack, dm_create_jack):
    response = requests.post(f'{BASE_URL}message/senddm/v1', json={'token': token_jack['token'], 'dm_id': dm_create_jack['dm_id'], 'message': "test message"})
    return response.json
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------
# TESTING DM/CREATE

def test_dm_create_invalid_token(clear):
    '''
    testing invalid token
    '''
    response = requests.post(f"{BASE_URL}dm/create/v1", json={'token': "-1", 'u_ids': [1]})
    assert response.status_code == AccessError().code

def test_valid_dm_create(clear, token_jack, token_sarah):
    '''
    testing valid case
    '''
    response = requests.post(f"{BASE_URL}dm/create/v1", json={'token': token_jack['token'], 'u_ids': [token_sarah['auth_user_id']]})
    assert response.status_code == 200
    assert response.json() == {'dm_id': 1}
 
def test_invalid_dm_create(clear, token_jack):
    '''
    Invalid Member = Input Error
    '''   
    response = requests.post(f"{BASE_URL}dm/create/v1", json={'token': token_jack['token'], 'u_ids': [1000]})
    assert response.status_code == InputError().code
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------
# TESTING DM/LIST
def test_valid_dm_list(clear, token_jack, token_sarah, token_phil):
    '''
    Testing valid dm list
    '''
    u_id1 = token_jack['auth_user_id']
    u_id2 = token_sarah['auth_user_id']
    u_id3 = token_phil['auth_user_id']
    
    r1 = requests.post(f"{BASE_URL}dm/create/v1",  json={'token': token_jack['token'], 'u_ids': [u_id2, u_id3]})
    new_dm = r1.json()
    assert r1.status_code == 200

    r2 = requests.post(f"{BASE_URL}dm/create/v1",  json={'token': token_sarah['token'], 'u_ids': [u_id1]})
    new_dm_2 = r2.json()
    assert r2.status_code == 200

    response = requests.get(f"{BASE_URL}dm/list/v1",  params={'token': token_jack['token']})
    assert response.json() == {
        'dms': [
        {
                'dm_id': new_dm['dm_id'], 
                'name': 'jackhill, philseed, sarahcat'
        },
        {
                'dm_id': new_dm_2['dm_id'],
                'name': 'jackhill, sarahcat'
        }
        ],
    }

def test_invalid_dm_list(clear):
    '''
    Invalid Token = Access Error
    '''  
    response = requests.get(f"{BASE_URL}dm/list/v1", json={'token': "-1"})
    assert response.status_code == AccessError().code   
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------
# TESTING DM/REMOVE
def test_dm_remove_invalid_dm_id(clear, token_jack):
    '''
    testing invalid dm_id
    '''   
    response = requests.post(f'{BASE_URL}dm/create/v1', json = {
        'token': token_jack['token'],
        'u_ids': [token_jack['auth_user_id'] ]
    })
    assert response.status_code == 200

    response = requests.delete(f'{BASE_URL}dm/remove/v1', json = {
        'token': token_jack['token'],
        'dm_id': 50
    })
    assert response.status_code == InputError().code

def test_dm_remove_successful(clear, token_jack, token_sarah):
    '''
    testing valid remove
    '''
    response = requests.post(f'{BASE_URL}dm/create/v1', json = {
        'token': token_jack['token'],
        'u_ids': [token_sarah['auth_user_id']]
    })
    assert response.status_code == 200

    response = requests.delete(f'{BASE_URL}dm/remove/v1', json = {
        'token': token_jack['token'],
        'dm_id': 1
    })
    assert response.status_code == 200
    
def test_dm_remove_invalid_token(clear, token_jack, token_sarah):
    '''
    testing invalid token
    '''
    response = requests.post(f'{BASE_URL}dm/create/v1', json = {
        'token': token_jack['token'],
        'u_ids': [token_sarah['auth_user_id']]
    })
    assert response.status_code == 200

    response = requests.delete(f'{BASE_URL}dm/remove/v1', json = {
        'token': 'wrong',
        'dm_id': 50
    })
    assert response.status_code == AccessError().code

def test_dm_remove_not_original_owner(clear, token_jack, token_sarah):
    '''
    testing when dm member who is not the owner, is trying to remove
    a member
    '''
    response = requests.post(f'{BASE_URL}dm/create/v1', json = {
        'token': token_jack['token'],
        'u_ids': [token_sarah['auth_user_id']]
    })
    assert response.status_code == 200

    response = requests.delete(f'{BASE_URL}dm/remove/v1', json = {
        'token': token_sarah['token'],
        'dm_id': 1
    })
    assert response.status_code == AccessError().code

def test_dm_valid_remove(clear, token_jack, token_sarah):
    ''' 
    testing valid case of dm remove
    '''    
    response = requests.post(f'{BASE_URL}dm/create/v1', json = {
        'token': token_jack['token'],
        'u_ids': [token_sarah['auth_user_id']]
    })
    dm = response.json()

    assert response.status_code == 200
    response = requests.delete(f'{BASE_URL}dm/remove/v1', json = {
        'token': token_jack['token'],
        'dm_id': dm['dm_id']
    })
    assert response.status_code == 200
    response = requests.get(f"{BASE_URL}dm/details/v1", params={'token': token_jack['token'], 'dm_id': dm['dm_id']})
    assert response.status_code == InputError().code   

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------
# TESTING DM/DETAILS
def test_valid_dm_details(clear, token_sarah, token_jack):
    '''
    testing valid case of dm details
    '''
    response = requests.post(f"{BASE_URL}dm/create/v1", json={'token': token_sarah['token'], 'u_ids': [token_jack['auth_user_id']]})
    dm = response.json()
    response = requests.get(f"{BASE_URL}dm/details/v1", params={'token': token_sarah['token'], 'dm_id': dm['dm_id']})
    dm_details = response.json()
    assert response.status_code == 200
    assert dm_details['name'] == "jackhill, sarahcat"
    assert dm_details['all_members'] == [{'u_id': 1, 'email': 'z5363412@ad.unsw.edu.au', 'name_first': 'Sarah', 'name_last': 'Cat', 'handle_str': 'sarahcat'},
                                        {'u_id': 2, 'email': 'z5359521@ad.unsw.edu.au', 'name_first': 'Jack', 'name_last': 'Hill', 'handle_str': 'jackhill'}]
   
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------
# TESTING DM/LEAVE
def test_valid_dm_leave(clear, token_sarah, token_jack, token_phil):
    '''
    testing valid case of dm leave
    '''
    u_id2 = token_jack['auth_user_id']
    u_id3 = token_phil['auth_user_id']
    
    response = requests.post(f"{BASE_URL}dm/create/v1",  json={'token': token_sarah['token'], 'u_ids': [u_id2, u_id3]})
    dm = response.json()  
    assert response.status_code == 200

    response = requests.post(f"{BASE_URL}dm/leave/v1",  json={'token': token_phil['token'], 'dm_id': dm['dm_id']})
    assert response.status_code == 200

    response = requests.get(f"{BASE_URL}dm/details/v1", params={'token': token_sarah['token'], 'dm_id': dm['dm_id']})
    dm_details = response.json()
    assert response.status_code == 200

    
    assert dm_details['name'] == "jackhill, philseed, sarahcat"
    assert dm_details['all_members'] == [{'u_id': 1, 'email': 'z5363412@ad.unsw.edu.au', 'name_first': 'Sarah', 'name_last': 'Cat', 'handle_str': 'sarahcat'},
                                        {'u_id': 2, 'email': 'z5359521@ad.unsw.edu.au', 'name_first': 'Jack', 'name_last': 'Hill', 'handle_str': 'jackhill'}]

def test_valid_dm_leave_owner(clear, token_phil, token_jack, token_sarah):
    u_id2 = token_sarah['auth_user_id']
    u_id3 = token_jack['auth_user_id']

    response = requests.post(f"{BASE_URL}dm/create/v1",  json={'token': token_phil['token'], 'u_ids': [u_id2, u_id3]})
    dm = response.json()  
    assert response.status_code == 200

    response = requests.post(f"{BASE_URL}dm/leave/v1",  json={'token': token_phil['token'], 'dm_id': dm['dm_id']})
    assert response.status_code == 200

    response = requests.get(f"{BASE_URL}dm/details/v1", params={'token': token_jack['token'], 'dm_id': dm['dm_id']})
    dm_details = response.json()
    assert response.status_code == 200
    
    assert dm_details['name'] == "jackhill, philseed, sarahcat"
    assert dm_details['all_members'] == [{'u_id': token_sarah['auth_user_id'], 'email': 'z5363412@ad.unsw.edu.au', 'name_first': 'Sarah', 'name_last': 'Cat', 'handle_str': 'sarahcat'},
                                        {'u_id': token_jack['auth_user_id'], 'email': 'z5359521@ad.unsw.edu.au', 'name_first': 'Jack', 'name_last': 'Hill', 'handle_str': 'jackhill'}]

def test_invalid_token_dm_leave(clear, token_jack, token_sarah):
    '''
    testing invalid token
    '''    
    response = requests.post(f"{BASE_URL}dm/create/v1",  json={'token': token_jack['token'], 'u_ids': [token_jack['auth_user_id']]})
    dm = response.json()  
    assert response.status_code == 200
    response = requests.post(f"{BASE_URL}dm/leave/v1",  json={'token': "-1", 'dm_id': dm['dm_id']})
    assert response.status_code == AccessError.code

def test_invalid_dm_id_dm_leave(clear, token_jack, token_sarah):
    '''
    Invalid DM id = Input Error
    '''    
    response = requests.post(f"{BASE_URL}dm/create/v1",  json={'token': token_jack['token'], 'u_ids': [token_sarah['auth_user_id']]})
    assert response.status_code == 200
    response = requests.post(f"{BASE_URL}dm/leave/v1",  json={'token': token_jack['token'], 'dm_id': 1000})
    assert response.status_code == InputError().code

def test_invalid_user_dm_leave(clear, token_jack, token_sarah, token_phil):
    '''
    User is not in DM = Access Error
    '''
    response = requests.post(f"{BASE_URL}dm/create/v1",  json={'token': token_jack['token'], 'u_ids': [token_sarah['auth_user_id']]})
    dm = response.json()  
    assert response.status_code == 200
    response = requests.post(f"{BASE_URL}dm/leave/v1",  json={'token': token_phil['token'], 'dm_id': dm['dm_id']})
    assert response.status_code == AccessError().code

    
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

# -------- TESTS for DM/MESSAGES/V1-----------------------------

def test_dm_messages_invalid_dm_id(clear, token_jack, token_sarah):
    '''
    test invalid dm_id
    '''
    response = requests.post(f'{BASE_URL}dm/create/v1', json = {
        'token': token_jack['token'],
        'u_ids': [token_sarah['auth_user_id']]
    })
    response = requests.get(f'{BASE_URL}dm/messages/v1', params = {
        'token': token_jack['token'],
        'dm_id': 50,
        'start': 0
    })
    assert response.status_code == InputError().code


def test_dm_messages_invalid_start(clear, token_jack, token_sarah):
    '''
    test invalid start
    '''
    response = requests.post(f'{BASE_URL}dm/create/v1', json = {
       'token': token_jack['token'],
       'u_ids': [token_sarah['auth_user_id']]
    })
    dm1 = response.json()
    response = requests.get(f'{BASE_URL}dm/messages/v1', params = {
       'token': token_jack['token'],
       'dm_id': dm1['dm_id'],
       'start': 33
    })
    assert response.status_code == InputError().code

def test_dm_messages_http_unauthorised_user(clear, token_jack, token_sarah, token_phil):
    '''
    test unauthorised auser
    '''
    response = requests.post(f'{BASE_URL}dm/create/v1', json = {
        'token': token_jack['token'],
        'u_ids': [token_sarah['auth_user_id']]
    })
    dm1 = response.json()

    response = requests.get(f'{BASE_URL}dm/messages/v1', params = {
        'token': token_phil['token'],
        'dm_id': dm1['dm_id'],
        'start': 0
    })
    assert response.status_code == AccessError().code
    
def test_dm_messages_valid(clear, token_jack, token_sarah):
    response = requests.post(f'{BASE_URL}dm/create/v1', json = {
        'token': token_jack['token'],
        'u_ids': [token_sarah['auth_user_id']]
    })
    dm1 = response.json()
    assert response.status_code == 200

    response = requests.get(f'{BASE_URL}dm/messages/v1', params = {
        'token': token_sarah['token'],
        'dm_id': dm1['dm_id'],
        'start': 0
    })
    assert response.status_code == 200

def test_dm_messages_valid_2(clear, token_jack, token_sarah, token_phil):
    """
    Test to see if dm messages works 
    """
    r = requests.post(config.url + 'dm/create/v1',  json={'token': token_jack['token'], 'u_ids': [token_sarah['auth_user_id'], token_phil['auth_user_id']]})
    dm_1 = r.json()
    r = requests.post(config.url + 'message/senddm/v1', json={'token': token_jack['token'], 'dm_id': dm_1['dm_id'], 'message' : "Hi"})
    r = requests.post(config.url + 'message/senddm/v1', json={'token': token_sarah['token'], 'dm_id': dm_1['dm_id'], 'message' : "Bye"}) 
    r = requests.get(config.url + 'dm/messages/v1',  params={'token': token_phil['token'], 'dm_id': dm_1['dm_id'], 'start' : 0})
    output = r.json()
    
    assert output['start'] == 0
    assert output['end'] == -1

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

# --------------TESTS FOR MESSAGE/SEND/DM----------------

# MESSAGE_SENDDM (Post)
def test_pass_message_senddm(clear, token_jack, token_sarah):
    response = requests.post(f"{BASE_URL}dm/create/v1", json={'token': token_jack['token'], 'u_ids': [token_sarah['auth_user_id']]})
    dm = response.json()
    assert response.status_code == 200

    res = requests.post(f'{BASE_URL}message/senddm/v1', json={'token': token_jack['token'], 'dm_id': dm['dm_id'], 'message': "test message"})
    assert res.status_code == 200
    message = res.json()
    assert message['message_id'] == 1

def test_invalid_token_message_senddm(clear, token_jack, token_sarah):
    message = requests.post(f'{BASE_URL}dm/create/v1', json={'token': token_jack['token'], 'u_ids': [token_sarah['auth_user_id']]})
    dm = message.json()

    res = requests.post(f'{BASE_URL}message/senddm/v1', json = {'token': '-1', 'dm_id': dm['dm_id'], 'message': "test message"})
    assert res.status_code == AccessError().code

def test_invalid_dm_id_message_senddm(clear, token_jack, token_sarah):
    requests.post(f'{BASE_URL}dm/create/v1', json={'token': token_jack['token'], 'u_ids': [token_sarah['auth_user_id']]})
    res = requests.post(f'{BASE_URL}message/senddm/v1', json={'token': token_jack['token'], 'dm_id': -1, 'message': "test message"})
    assert res.status_code == InputError().code

def test_invalid_message_message_senddm(clear, token_jack, token_sarah):
    message = requests.post(f'{BASE_URL}dm/create/v1', json={'token': token_jack['token'], 'u_ids': [token_sarah['auth_user_id']]})
    dm = message.json()

    res = requests.post(f'{BASE_URL}message/senddm/v1', json = {'token': token_jack['token'], 'dm_id': dm['dm_id'], 'message': ''})
    assert res.status_code == InputError().code

def test_not_member_of_DM_message_senddm(clear, token_jack, token_sarah, token_phil):
    message = requests.post(f'{BASE_URL}dm/create/v1', json={'token': token_jack['token'], 'u_ids': [token_sarah['auth_user_id']]})
    dm = message.json()

    res = requests.post(f'{BASE_URL}message/senddm/v1', json={'token': token_phil['token'], 'dm_id': dm['dm_id'], 'message': '1'})
    assert res.status_code == AccessError().code
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------
# message sendlaterdm

def test_sendlaterdm_invalid_dm_id(clear, token_jack, dm_create_jack, senddm_jack):
    '''
    invalid dm_id
    INPUT ERROR
    '''
    res = requests.post(f"{BASE_URL}message/sendlaterdm/v1", json= {'token': token_jack['token'], 'dm_id': -1, 'message': "send dm later", 'time_sent': datetime.datetime.now().timestamp() + 2})
    assert res.status_code == InputError().code

def test_sendlaterdm_invalid_message_len(clear, token_jack, dm_create_jack, senddm_jack):
    '''
    invalid message length
    INPUT ERROR
    '''
    res = requests.post(f"{BASE_URL}message/sendlaterdm/v1", json= {'token': token_jack['token'], 'dm_id': dm_create_jack['dm_id'], 'message': "", 'time_sent': datetime.datetime.now().timestamp() + 2})
    assert res.status_code == InputError().code
    
def test_sendlaterdm_time_sent_past(clear, token_jack, dm_create_jack, senddm_jack):
    '''
    time_sent is from the past
    INPUT ERROR
    '''
    res = requests.post(f"{BASE_URL}message/sendlaterdm/v1", json= {'token': token_jack['token'], 'dm_id': dm_create_jack['dm_id'], 'message': "send dm later", 'time_sent': 2})
    assert res.status_code == InputError().code

def test_sendlaterdm_user_not_mem(clear, token_jack, dm_create_jack, senddm_jack, token_phil):
    '''
    user is not a member
    ACCESS ERROR
    '''
    res = requests.post(f"{BASE_URL}message/sendlaterdm/v1", json= {'token': token_phil['token'], 'dm_id': dm_create_jack['dm_id'], 'message': "send dm later", 'time_sent': datetime.datetime.now().timestamp() + 2})
    assert res.status_code == AccessError().code
    
def test_sendlaterdm_dm_removed(clear, token_jack, dm_create_jack, senddm_jack):
    '''
    DM was removed prior sending
    INPUT ERROR
    '''
    res = requests.post(f"{BASE_URL}message/sendlaterdm/v1", json= {'token': token_jack['token'], 'dm_id': dm_create_jack['dm_id'], 'message': "sendd dm later", 'time_sent': datetime.datetime.now().timestamp() + 2})
    requests.delete(f'{BASE_URL}dm/remove/v1', json = {
        'token': token_jack['token'],
        'dm_id': dm_create_jack['dm_id']
    })
    assert res.status_code == 200
    
def test_sendlaterdm_user_sending_left(clear, token_jack, dm_create_jack, senddm_jack):
    '''
    User left DM prior sending
    ACCESS ERROR
    '''
    res = requests.post(f"{BASE_URL}message/sendlaterdm/v1", json= {'token': token_jack['token'], 'dm_id': dm_create_jack['dm_id'], 'message': "sned dm later", 'time_sent': datetime.datetime.now().timestamp() + 2})
    requests.post(f"{BASE_URL}dm/leave/v1",  json={'token': token_jack['token'], 'dm_id': dm_create_jack['dm_id']})
    assert res.status_code == 200

def test_sendlaterdm_valid(clear, token_jack, dm_create_jack, senddm_jack):
    '''
    Valid Case
    '''
    res = requests.post(f"{BASE_URL}message/sendlaterdm/v1", json= {'token': token_jack['token'], 'dm_id': dm_create_jack['dm_id'], 'message': "send dm later", 'time_sent': datetime.datetime.now().timestamp() + 2})
    assert res.status_code == 200
    
# INVALID TOKEN LOGOUT
def test_dm_create_user_logout(clear, token_jack):
    requests.post(f"{BASE_URL}/auth/logout/v1", json={'token': token_jack['token']})
    response = requests.post(f"{BASE_URL}dm/create/v1", json={'token': token_jack['token'], 'u_ids': []})
    assert response.status_code == AccessError().code

def test_invalid_token_dm_list_user_logout(clear, token_jack, token_sarah, token_phil):
    '''
    Testing valid dm list
    '''
    u_id1 = token_jack['auth_user_id']
    u_id2 = token_sarah['auth_user_id']
    u_id3 = token_phil['auth_user_id']
    
    r1 = requests.post(f"{BASE_URL}dm/create/v1",  json={'token': token_jack['token'], 'u_ids': [u_id2, u_id3]})
    assert r1.status_code == 200

    r2 = requests.post(f"{BASE_URL}dm/create/v1",  json={'token': token_sarah['token'], 'u_ids': [u_id1]})
    assert r2.status_code == 200
    requests.post(f"{BASE_URL}/auth/logout/v1", json={'token': token_jack['token']})
    response = requests.get(f"{BASE_URL}dm/list/v1",  params={'token': token_jack['token']})
    assert response.status_code == AccessError().code

def test_invalid_token_dm_details_user_logout(clear, token_sarah, token_jack):
    '''
    testing valid case of dm details
    '''
    response = requests.post(f"{BASE_URL}dm/create/v1", json={'token': token_sarah['token'], 'u_ids': [token_jack['auth_user_id']]})
    dm = response.json()
    requests.post(f"{BASE_URL}/auth/logout/v1", json={'token': token_jack['token']})
    response = requests.get(f"{BASE_URL}dm/details/v1", params={'token': token_jack['token'], 'dm_id': dm['dm_id']})
    assert response.status_code == AccessError().code

def test_dm_invalid_token_remove_user_logout(clear, token_jack, token_sarah):
    ''' 
    testing valid case of dm remove
    '''    
    response = requests.post(f'{BASE_URL}dm/create/v1', json = {
        'token': token_jack['token'],
        'u_ids': [token_sarah['auth_user_id']]
    })
    dm = response.json()
    requests.post(f"{BASE_URL}/auth/logout/v1", json={'token': token_jack['token']})

    response = requests.delete(f'{BASE_URL}dm/remove/v1', json = {
        'token': token_jack['token'],
        'dm_id': dm['dm_id']
    })
    assert response.status_code == AccessError().code

def test_invalid_token_dm_leave_user_logout(clear, token_sarah, token_jack, token_phil):
    '''
    testing valid case of dm leave
    '''
    u_id2 = token_jack['auth_user_id']
    u_id3 = token_phil['auth_user_id']
    
    response = requests.post(f"{BASE_URL}dm/create/v1",  json={'token': token_sarah['token'], 'u_ids': [u_id2, u_id3]})
    dm = response.json()  
    assert response.status_code == 200
    requests.post(f"{BASE_URL}/auth/logout/v1", json={'token': token_phil['token']})

    response = requests.post(f"{BASE_URL}dm/leave/v1",  json={'token': token_phil['token'], 'dm_id': dm['dm_id']})
    assert response.status_code == AccessError().code

def test_dm_messages_invalid_token_user_logged_out(clear, token_jack, token_sarah):
    response = requests.post(f'{BASE_URL}dm/create/v1', json = {
        'token': token_jack['token'],
        'u_ids': [token_sarah['auth_user_id']]
    })
    dm1 = response.json()
    assert response.status_code == 200
    requests.post(f"{BASE_URL}/auth/logout/v1", json={'token': token_sarah['token']})

    response = requests.get(f'{BASE_URL}dm/messages/v1', params = {
        'token': token_sarah['token'],
        'dm_id': dm1['dm_id'],
        'start': 0
    })
    assert response.status_code == AccessError().code

def test_invalid_token_message_senddm_(clear, token_jack, token_sarah):
    response = requests.post(f"{BASE_URL}dm/create/v1", json={'token': token_jack['token'], 'u_ids': [token_sarah['auth_user_id']]})
    dm = response.json()
    assert response.status_code == 200
    requests.post(f"{BASE_URL}/auth/logout/v1", json={'token': token_jack['token']})
    res = requests.post(f'{BASE_URL}message/senddm/v1', json={'token': token_jack['token'], 'dm_id': dm['dm_id'], 'message': "test message"})
    assert res.status_code == AccessError().code

# ----------------------------------------------------------------------------
#------- TESTS FOR message/sendlater/v1--------

def test_message_send_later_invalid_channel(clear, token_jack, channel_id_jack):
    response = requests.post(f'{BASE_URL}message/sendlater/v1', json = {
        'token': token_jack['token'],
        'channel_id': '1029300934',
        'message': "Hi",
        'time_sent': datetime.datetime.now().timestamp() + 2
    })
    assert response.status_code == InputError().code

def test_message_send_later_invalid_length(clear, token_jack, channel_id_jack):
    response = requests.post(f'{BASE_URL}message/sendlater/v1', json = {
        'token': token_jack['token'],
        'channel_id': channel_id_jack['channel_id'],
        'message': "",
        'time_sent': datetime.datetime.now().timestamp() + 2
    })
    assert response.status_code == InputError().code

def test_message_send_later_time_past(clear, token_jack, channel_id_jack):
    response = requests.post(f'{BASE_URL}message/sendlater/v1', json = {
        'token': token_jack['token'],
        'channel_id': channel_id_jack['channel_id'],
        'message': "Hi",
        'time_sent': 2
    })
    assert response.status_code == InputError().code

def test_message_send_later_invalid_member(clear, token_jack, channel_id_jack, token_phil):
    response = requests.post(f'{BASE_URL}message/sendlater/v1', json = {
        'token': token_phil['token'],
        'channel_id': channel_id_jack['channel_id'],
        'message': "Hi",
        'time_sent': datetime.datetime.now().timestamp() + 2
    })
    assert response.status_code == AccessError().code

def test_message_send_later_valid_case(clear, token_jack, channel_id_jack):
    response = requests.post(f'{BASE_URL}message/sendlater/v1', json = {
        'token': token_jack['token'],
        'channel_id': channel_id_jack['channel_id'],
        'message': "Hi i am jack",
        'time_sent': datetime.datetime.now().timestamp() + 2
    })
    assert response.status_code == 200


    