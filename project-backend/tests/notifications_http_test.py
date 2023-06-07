'''
pip3 packages
'''
import pytest
import requests
from src import config
import json
from src.error import AccessError, InputError
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
@pytest.fixture
def phill():
    return requests.post(f"{BASE_URL}auth/register/v2", json={'email':'z1563412@ad.unsw.edu.au', 'password' : 'tesing456', 'name_first':'Phill', 'name_last':'Green'})

#----------------------------------------------------------------------------------
def test_notifcations_simple(clear, jack, sarah):
    user1 = jack.json()
    user2 = sarah.json()
    response = requests.post(config.url + "channels/create/v2", json = {'token': user1['token'], 'name': 'jackchannel', 'is_public': True})
    new_channel = response.json()
    requests.post(config.url + "channel/invite/v2", json = {'token': user1['token'], 'channel_id': new_channel['channel_id'], 'u_id': user2['auth_user_id']})
    res = requests.get(f'{BASE_URL}notifications/get/v1', params={'token': user2['token']})
    assert res.status_code == 200
    notifiy = res.json()
    assert len(notifiy['notifications']) == 1

def test_notfications_over_20(clear, jack, sarah):
    user_1 = jack.json()
    user_2 = sarah.json()
    r = requests.post(config.url + 'dm/create/v1',  json={'token': user_1['token'], 'u_ids': [user_2['auth_user_id']]})
    dm_1 = r.json()
    message_1 =  "Spam @sarahcat"
    for r in range(25):
        r = requests.post(config.url + 'message/senddm/v1', json={'token': user_1['token'], 'dm_id': dm_1['dm_id'], 'message' : message_1})
    message_id = r.json()
    requests.post(f'{BASE_URL}message/react/v1', json = {'token': user_2['token'], 'message_id': message_id['message_id'], 'react_id': 1 })
    res = requests.get(f'{BASE_URL}notifications/get/v1', params={'token': user_2['token']})
    assert res.status_code == 200
    notifiy = res.json()
    assert len(notifiy['notifications']) == 20
    res = requests.get(f'{BASE_URL}notifications/get/v1', params={'token': user_1['token']})
    assert res.status_code == 200
    notifiy = res.json()
    assert len(notifiy['notifications']) == 1

def test_no_notifications(clear, jack, sarah):
    user = jack.json()
    res = requests.get(f'{BASE_URL}notifications/get/v1', params={'token': user['token']})
    assert res.status_code == 200
    notifiy = res.json()
    assert len(notifiy['notifications']) == 0

def test_multiple_users(clear, jack, sarah):
    user_1 = jack.json()
    user_2 = sarah.json()
    r = requests.post(config.url + 'dm/create/v1',  json={'token': user_1['token'], 'u_ids': [user_2['auth_user_id']]})
    dm_1 = r.json()
    message_1 = "Spam @sarahcat"
    message_2 = "Spam @jackhill"
    for r in range(12):
        r = requests.post(config.url + 'message/senddm/v1', json={'token': user_1['token'], 'dm_id': dm_1['dm_id'], 'message' : message_1})
    for r in range(4):
        r = requests.post(config.url + 'message/senddm/v1', json={'token': user_2['token'], 'dm_id': dm_1['dm_id'], 'message' : message_2})
    res = requests.get(f'{BASE_URL}notifications/get/v1', params={'token': user_2['token']})
    assert res.status_code == 200
    notifiy = res.json()
    assert len(notifiy['notifications']) == 13

def test_notifcations_channel_react(clear, jack, sarah):
    user1 = jack.json()
    user2 = sarah.json()
    response = requests.post(config.url + "channels/create/v2", json = {'token': user1['token'], 'name': 'jackchannel', 'is_public': True})
    new_channel = response.json()
    requests.post(config.url + "channel/invite/v2", json = {'token': user1['token'], 'channel_id': new_channel['channel_id'], 'u_id': user2['auth_user_id']})
    res = requests.post(f'{BASE_URL}message/send/v1', json = {'token': user1['token'],'channel_id': new_channel['channel_id'], 'message': "Spam @sarahcat"})
    message_id = res.json()
    requests.post(f'{BASE_URL}message/react/v1', json = {'token': user2['token'], 'message_id': message_id['message_id'], 'react_id': 1 })
    res = requests.get(f'{BASE_URL}notifications/get/v1', params={'token': user2['token']})
    assert res.status_code == 200
    notifiy = res.json()
    assert len(notifiy['notifications']) == 2
    res = requests.get(f'{BASE_URL}notifications/get/v1', params={'token': user1['token']})
    assert res.status_code == 200
    notifiy = res.json()
    assert len(notifiy['notifications']) == 1

def test_notifications_sendlater(clear, jack, sarah):
    user1 = jack.json()
    user2 = sarah.json()
    response = requests.post(config.url + "channels/create/v2", json = {'token': user1['token'], 'name': 'jackchannel', 'is_public': True})
    new_channel = response.json()
    requests.post(config.url + "channel/invite/v2", json = {'token': user1['token'], 'channel_id': new_channel['channel_id'], 'u_id': user2['auth_user_id']})
    r = requests.post(config.url + 'dm/create/v1',  json={'token': user1['token'], 'u_ids': [user2['auth_user_id']]})
    new_dm = r.json()
    r = requests.post(config.url + "message/sendlaterdm/v1", json= {'token': user1['token'], 'dm_id': new_dm['dm_id'], 'message': "sp @sarahcat am", 'time_sent': datetime.datetime.now().timestamp() + 2})
    res = requests.post(f'{BASE_URL}message/sendlater/v1', json = {'token': user1['token'], 'channel_id': new_channel['channel_id'], 'message': "@sarahcat spam", 'time_sent': datetime.datetime.now().timestamp() + 2})
    time.sleep(3)  
    res = requests.get(f'{BASE_URL}notifications/get/v1', params={'token': user2['token']})
    assert res.status_code == 200
    notifiy = res.json()
    print(notifiy['notifications'])
    assert len(notifiy['notifications']) == 4
    res = requests.get(f'{BASE_URL}notifications/get/v1', params={'token': user1['token']})
    assert res.status_code == 200
    notifiy = res.json()
    assert len(notifiy['notifications']) == 0

def test_react_leave_group(clear, jack, sarah):
    user1 = jack.json()
    user2 = sarah.json()
    response = requests.post(config.url + "channels/create/v2", json = {'token': user1['token'], 'name': 'jackchannel', 'is_public': True})
    requests.post(config.url + "channels/create/v2", json = {'token': user2['token'], 'name': 'sarahchannel', 'is_public': False})
    new_channel = response.json()
    requests.post(config.url + "channel/invite/v2", json = {'token': user1['token'], 'channel_id': new_channel['channel_id'], 'u_id': user2['auth_user_id']})
    res = requests.post(f'{BASE_URL}message/send/v1', json = {'token': user2['token'],'channel_id': new_channel['channel_id'], 'message': "Spam @jackhill"})
    message_id = res.json()
    requests.post(config.url + 'channel/leave/v1', json = {"token": user2['token'], "channel_id": new_channel['channel_id']})
    requests.post(f'{BASE_URL}message/react/v1', json = {'token': user1['token'], 'message_id': message_id['message_id'], 'react_id': 1 })
    res = requests.get(f'{BASE_URL}notifications/get/v1', params={'token': user2['token']})
    assert res.status_code == 200
    notifiy = res.json()
    assert len(notifiy['notifications']) == 1
    res = requests.get(f'{BASE_URL}notifications/get/v1', params={'token': user1['token']})
    assert res.status_code == 200
    notifiy = res.json()
    assert len(notifiy['notifications']) == 1

def test_notifications_messege_edit(clear, jack, sarah, phill): 
    user1 = jack.json()
    user2 = sarah.json()
    user3 = phill.json()
    r = requests.post(config.url + 'dm/create/v1',  json={'token': user1['token'], 'u_ids': [user2['auth_user_id'], user3['auth_user_id']]})
    dm_1 = r.json()
    r = requests.post(config.url + 'message/senddm/v1', json={'token': user1['token'], 'dm_id': dm_1['dm_id'], 'message' : "spaming @sarahcat"})
    message_id = r.json()
    requests.put(f'{BASE_URL}message/edit/v1', json = {
        'token': user1['token'],
        'message_id': message_id['message_id'],
        'message': "new message @phillgreen and @sarahcat"
    })
    res = requests.get(f'{BASE_URL}notifications/get/v1', params={'token': user1['token']})
    assert res.status_code == 200
    notifiy = res.json()
    assert len(notifiy['notifications']) == 0
    res = requests.get(f'{BASE_URL}notifications/get/v1', params={'token': user2['token']})
    assert res.status_code == 200
    notifiy = res.json()
    assert len(notifiy['notifications']) == 2
    res = requests.get(f'{BASE_URL}notifications/get/v1', params={'token': user3['token']})
    assert res.status_code == 200
    notifiy = res.json()
    assert len(notifiy['notifications']) == 2

def test_invalid_token(clear):
    res = requests.get(f'{BASE_URL}notifications/get/v1', params={'token': 'wrong'})
    assert res.status_code == AccessError().code