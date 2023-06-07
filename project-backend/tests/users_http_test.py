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
from helpers.other_helper import auth_id_to_user
import jwt
import json
import time
import datetime
BASE_URL = config.url

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

# test the function works for one user
def test_one_users_all_v1(clear, jack):
    user = jack.json()
    res = requests.get(f'{BASE_URL}users/all/v1', params={'token': user['token']})
    users = res.json()
    assert res.status_code == 200
    assert len(users['users']) == 1

# incorrect user token
def test_wrong_token_users_all_v1(clear, jack):
    res = requests.get(f'{BASE_URL}users/all/v1', params={'token': 'Wrong'})
    assert res.status_code == AccessError().code

# test function works for multiple users
def test_multiple_users_all(clear, sarah, jack):
    user_1 = jack.json()
    res = requests.get(f'{BASE_URL}users/all/v1', params={'token': user_1['token']})
    assert res.status_code == 200
    users = res.json()
    assert len(users['users']) == 2


####################################################################################################################################################
##########################################USERS_STATS TESTS#################################################################################
####################################################################################################################################################

def test_initial_workspace_stats(clear, jack):
    '''
    Tests users_stats_v1 intial workspace is zero
    '''
    user = jack.json()
    
    response = requests.get(f"{BASE_URL}users/stats/v1", params = {
        'token' : user['token']
    })
    
    assert response.status_code == 200
    
    workspace_stats = response.json()["workspace_stats"]
    assert workspace_stats["channels_exist"][0]["num_channels_exist"] == 0
    assert workspace_stats["dms_exist"][0]["num_dms_exist"] == 0
    assert workspace_stats["messages_exist"][0]["num_messages_exist"] == 0
    assert workspace_stats["utilization_rate"] == 0

def test_channels_create_workspace_stats(clear, jack):
    '''
    Tests users_stats_v1 when created a channel, workspace increases in channels_exist
    '''
    user = jack.json()

    requests.post(f"{BASE_URL}channels/create/v2", json={
        "token": user['token'],
        "name": "channel",
        "is_public": True
    })

    response = requests.get(f"{BASE_URL}users/stats/v1", params={
        "token": user['token']
    })
    
    assert response.status_code == 200
    workspace_stats = response.json()["workspace_stats"]
    assert workspace_stats["channels_exist"][1]["num_channels_exist"] == 1

def test_dm_create_workspace_stats(clear, jack):
    '''
    Tests users_stats_v1 when dm is created and increases stats
    '''
    user = jack.json()

    # user1 create dm1 with 1 user
    requests.post(f"{BASE_URL}dm/create/v1", json={
        "token": user['token'],
        "u_ids": []
    })

    # check user's stats after creating dm1
    response = requests.get(f"{BASE_URL}users/stats/v1", params={
        "token": user['token']
    })
    assert response.status_code == 200
    workspace_stats = response.json()["workspace_stats"]
    assert workspace_stats["dms_exist"][1]["num_dms_exist"] == 1

def test_dm_remove_workspace_stats(clear, jack):
    '''
    Tests users_stats_v1 when a dm is removed
    '''
    user = jack.json()

    requests.post(f"{BASE_URL}dm/create/v1", json={
        "token": user['token'],
        "u_ids": [1]
    })

    requests.delete(f"{BASE_URL}dm/remove/v1", json={
        "token": user['token'],
        "dm_id": 1
    })

    response = requests.get(f"{BASE_URL}users/stats/v1", params={
        "token": user['token']
    })

    assert response.status_code == 200
    
    workspace_stats = response.json()["workspace_stats"]
    assert workspace_stats["dms_exist"][2]["num_dms_exist"] == 0

def test_message_send_workspace_stats(clear, jack):
    '''
    Tests users_stats_v1 when message_exist increases & channels
    '''
    user = jack.json()

    requests.post(f"{BASE_URL}channels/create/v2", json={
        "token": user['token'],
        "name": "channel1",
        "is_public": True
    })

    requests.post(f"{BASE_URL}message/send/v1", json={
        "token": user['token'],
        "channel_id": 1,
        "message": "okay"
    })

    response = requests.get(f"{BASE_URL}users/stats/v1", params={
        "token": user['token']
    })
    assert response.status_code == 200

    workspace_stats = response.json()["workspace_stats"]
    assert workspace_stats["channels_exist"][1]["num_channels_exist"] == 1
    assert workspace_stats["messages_exist"][1]["num_messages_exist"] == 1
    
def test_message_senddm_workspace_stats(clear, jack):
    '''
    Tests users_stats_v1 when dm & message_exist increases
    '''
    user = jack.json()

    requests.post(f"{BASE_URL}dm/create/v1", json={
        "token": user['token'],
        "u_ids": []
    })

    requests.post(f"{BASE_URL}message/senddm/v1", json={
        "token": user['token'],
        "dm_id": 1,
        "message": "hello"
    })

    response = requests.get(f"{BASE_URL}users/stats/v1", params={
        "token": user['token']
    })
    assert response.status_code == 200

    workspace_stats = response.json()["workspace_stats"]
    assert workspace_stats["dms_exist"][1]["num_dms_exist"] == 1
    assert workspace_stats["messages_exist"][1]["num_messages_exist"] == 1

def test_message_sendlater_workspace_stats(clear, jack):
    '''
    Tests users stats once user sends a message later
    '''
    user = jack.json()

    requests.post(f"{BASE_URL}channels/create/v2", json={
        "token": user['token'],
        "name": "channel1",
        "is_public": True
    })

    requests.post(f"{BASE_URL}message/sendlater/v1", json={
        "token": user['token'],
        "channel_id": 1,
        "message": "testing",
        "time_sent": datetime.datetime.now().timestamp() + 2
    })
    time.sleep(3)
    response = requests.get(f"{BASE_URL}users/stats/v1", params={
        "token": user['token'],
    })
    assert response.status_code == 200
    
    workspace_stats = response.json()["workspace_stats"]
    assert workspace_stats["channels_exist"][1]["num_channels_exist"] == 1
    assert workspace_stats["messages_exist"][1]["num_messages_exist"] == 1

def test_message_sendlaterdm_workspace_stats(clear, jack):
    '''
    Tests users_stats_v1 when dm & message_exist increases
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

    response = requests.get(f"{BASE_URL}users/stats/v1", params={
        "token": user['token']
    })
    assert response.status_code == 200

    workspace_stats = response.json()["workspace_stats"]
    assert workspace_stats["dms_exist"][1]["num_dms_exist"] == 1
    assert workspace_stats["messages_exist"][1]["num_messages_exist"] == 1

def test_user_remove_stats(clear, jack, sarah):
    '''
    Test that once user is removed, user does not have 
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

    requests.delete(f"{BASE_URL}admin/user/remove/v1", json={
        "token": user['token'],
        "u_id": 2
    })

    response = requests.get(f"{BASE_URL}users/stats/v1", params={
        "token": user2['token']
    })
    
    assert response.status_code == AccessError().code

def test_invalid_token_once_logged_out_users_stats(clear, jack):
    '''
    Invalid token when user tries to check stats after logging out
    '''
    user1 = jack.json()

    requests.post(f'{BASE_URL}auth/logout/v1', json={
        'token': user1['token']})

    response = requests.get(f"{BASE_URL}users/stats/v1", params={
        "token": user1['token']
    })
    
    assert response.status_code == AccessError().code

def test_valid_users_stats(clear, jack, sarah):
    '''
    Testsing a successful workspace_stat
    '''

    user = jack.json()
    user = sarah.json()

    requests.post(f"{BASE_URL}channels/create/v2", json={
        "token": user['token'],
        "name": "channel1",
        "is_public": True
    })
   
    requests.post(f"{BASE_URL}dm/create/v1", json={
        "token": user['token'],
        "u_ids": [2]
    })
    
    requests.post(f"{BASE_URL}message/senddm/v1", json={
        "token": user['token'],
        "dm_id": 1,
        "message": "hi"
    })

    response = requests.get(f"{BASE_URL}users/stats/v1", params={
        "token": user['token']
    })
    assert response.status_code == 200

    workspace_stats = response.json()["workspace_stats"]
    assert workspace_stats['channels_exist'][-1]['num_channels_exist'] == 1
    assert workspace_stats["dms_exist"][-1]["num_dms_exist"] == 2
    assert workspace_stats["messages_exist"][-1]["num_messages_exist"] == 1
    assert workspace_stats['utilization_rate'] == 0.5
    assert response.status_code == 200
    


