'''
Tests for:
    - admin_user_remove_v1
    - admin_userpermission_change_v1
'''
from urllib import response
import pytest
import json
from src.config import url
import requests
from src.error import AccessError, InputError
from helpers.other_helper import generate_jwt
#-----------------------------------------------------------------------------
SECRET = 'H15ABADGER'
#-----------------------------------------------------------------------------
# FIXTURES
@pytest.fixture
def clear():
    requests.delete(f'{url}clear/v1')
#-----------------------------------------------------------------------------
# admin_user_remove_v1 
def test_admin_user_remove_invalid_token(clear):
    '''
    Testing for invalid token from admin
    '''
    res = requests.post(f'{url}auth/register/v2', json = {
        'email': "hello@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': "Smith"
    })
    user = res.json()
    invalid_token = generate_jwt(user['auth_user_id'] + 1,1)
    response = requests.delete(f'{url}admin/user/remove/v1', json = {
        'token' : invalid_token,
        'u_id' : user['auth_user_id']
    })
    assert response.status_code == AccessError().code

def test_admin_user_remove_invalid_id(clear):
    '''
    Testing for invalid id from admin
    '''
    res = requests.post(f'{url}auth/register/v2', json = {
        'email': "hello@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': "Smith"
    })
    user = res.json()
    
    response = requests.delete(f'{url}admin/user/remove/v1', json = {
        'token' : user['token'],
        'u_id' : user['auth_user_id'] + 100
    })
    assert response.status_code == InputError().code

def test_admin_remove_global_owner(clear):
    '''
    Testing if a user is global owner and being removed
    '''
    res = requests.post(f'{url}auth/register/v2', json = {
        'email': "hello@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': "Smith"
    })
    user = res.json()

    response = requests.delete(f'{url}admin/user/remove/v1', json = {
        'token' : user['token'],
        'u_id' : user['auth_user_id']
    })
    assert response.status_code == InputError().code
    
def test_admin_not_global_owner(clear):
    '''
    Testing if a user is calling the remove function but is not an owner
    '''
    res = requests.post(f'{url}auth/register/v2', json = {
        'email': "owner@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': "Smith"
    })
    user1 = res.json() 
    
    res = requests.post(f'{url}auth/register/v2', json = {
        'email': "second@gmail.com",
        'password': "mynameis8",
        'name_first': "John",
        'name_last': "Smith"
    })
    user2 = res.json()
    
    response = requests.delete(f'{url}admin/user/remove/v1', json = {
        'token' : user2['token'],
        'u_id' : user1['auth_user_id']
    })
    assert response.status_code == AccessError().code
    
def test_admin_remove(clear):
    '''
    Testing if admin function works 
    '''
    r = requests.post(f'{url}auth/register/v2', json={
        'email':'hello@gmail.com',
        'password':'password', 
        'name_first':'Hayden', 
        'name_last':'Smith'})
    user1 = r.json()
    
    r = requests.post(f'{url}auth/register/v2', json={
        'email':'goodbye@gmail.com',
        'password':'mynameis8!', 
        'name_first':'John', 
        'name_last':'Smith'})
    user2 = r.json()
    
    response = requests.delete(f'{url}admin/user/remove/v1', json={
        'token': user1['token'], 
        'u_id': user2['auth_user_id']})
    
    assert response.status_code == 200

def test_admin_remove_owner(clear):
    '''
    Testing if admin function works 
    '''
    r = requests.post(f'{url}auth/register/v2', json={
        'email':'hello@gmail.com',
        'password':'password', 
        'name_first':'Hayden', 
        'name_last':'Smith'})
    user1 = r.json()
    
    r = requests.post(f'{url}auth/register/v2', json={
        'email':'goodbye@gmail.com',
        'password':'mynameis8!', 
        'name_first':'John', 
        'name_last':'Smith'})
    user2 = r.json()
    
    r = requests.post(f'{url}channels/create/v2', json = {
        "token": user1['token'], 
        "name": 'hi', 
        "is_public": True
    })
    
    r = requests.post(f'{url}channel/join/v2', json = {
        'token': user2['token'],
        'channel_id': 1
    })
    
    r = requests.delete(f'{url}admin/user/remove/v1', json={
        'token': user2['token'], 
        'u_id': user1['auth_user_id']})
    
    assert r.status_code == AccessError().code
    
def test_admin_remove_dm(clear):
    '''
    Testing when valid case when user is removed and has sent a DM
    '''
    r = requests.post(f'{url}auth/register/v2', json={
        'email':'hello@gmail.com',
        'password':'password', 
        'name_first':'Hayden', 
        'name_last':'Smith'})
    user1 = r.json()
    
    r = requests.post(f'{url}auth/register/v2', json={
        'email':'goodbye@gmail.com',
        'password':'mynameis8!', 
        'name_first':'John', 
        'name_last':'Smith'})
    user2 = r.json()
    
    r = requests.post(f'{url}channels/create/v2', json = {
        "token": user1['token'], 
        "name": 'hi', 
        "is_public": True
    })
    
    r = requests.post(f'{url}channel/join/v2', json = {
        'token': user2['token'],
        'channel_id': 1
    })

    r = requests.post(f'{url}dm/create/v1',  json={'token': user1['token'], 'u_ids': [user2['auth_user_id']]})
    dm_1 = r.json()
    message_1 = "Hello"
    message_2 = "Bye"

    r = requests.post(f'{url}message/senddm/v1', json={'token': user1['token'], 'dm_id': dm_1['dm_id'], 'message' : message_1})
    r = requests.post(f'{url}message/senddm/v1', json={'token': user2['token'], 'dm_id': dm_1['dm_id'], 'message' : message_2}) 
     
    r = requests.delete(f'{url}admin/user/remove/v1', json={
        'token': user1['token'], 
        'u_id': user2['auth_user_id']})
    
    assert r.status_code == 200
    
def test_reusable_handle(clear):
    '''
    Testing if handle can be reused once user is removed
    '''
    r = requests.post(f'{url}auth/register/v2', json={
        'email':'hello@gmail.com',
        'password':'password', 
        'name_first':'Hayden', 
        'name_last':'Smith'})
    user1 = r.json()
    
    r = requests.post(f'{url}auth/register/v2', json={
        'email':'goodbye@gmail.com',
        'password':'mynameis8!', 
        'name_first':'John', 
        'name_last':'Smith'})
    user2 = r.json()
    
    r = requests.delete(f'{url}admin/user/remove/v1', json={
        'token': user1['token'], 
        'u_id': user2['auth_user_id']})
    
    r = requests.post(f'{url}auth/register/v2', json={
        'email':'goodbye@gmail.com',
        'password':'mynameis8!', 
        'name_first':'John', 
        'name_last':'Smith'})
    newuser2 = r.json()
    
    res = requests.get(f'{url}user/profile/v1', params={
        'token': newuser2['token'], 
        'u_id': newuser2['auth_user_id']})
    
    assert res.json()['user']['handle_str'] == 'johnsmith'

def test_removal_from_channel(clear):
    '''
    Test when user is removed and channel was created
    '''
    r = requests.post(f'{url}auth/register/v2', json={
        'email':'hello@gmail.com',
        'password':'password', 
        'name_first':'Hayden', 
        'name_last':'Smith'})
    user1 = r.json()
    
    r = requests.post(f'{url}auth/register/v2', json={
        'email':'goodbye@gmail.com',
        'password':'mynameis8!', 
        'name_first':'John', 
        'name_last':'Smith'})
    user2 = r.json()
    
    r = requests.post(f'{url}channels/create/v2', json = {
        "token": user1['token'], 
        "name": 'hi', 
        "is_public": True
    })
    
    r = requests.post(f'{url}channel/join/v2', json = {
        'token': user2['token'],
        'channel_id': 1
    })
    
    r = requests.delete(f'{url}admin/user/remove/v1', json={
        'token': user1['token'], 
        'u_id': user2['auth_user_id']})
    
#-----------------------------------------------------------------------------
# admin_userpermission_change_v1
def test_admin_userpermission_change_invalid_token(clear):
    '''
    Testing for invalid token
    '''
    res = requests.post(f'{url}auth/register/v2', json = {
        'email': "hello@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': "Smith"
    })
    user = res.json()
    invalid_token = generate_jwt(user['auth_user_id'] + 1,1)
    
    response = requests.post(f'{url}admin/userpermission/change/v1', json = {
    'token': invalid_token, 
    'u_id':user['auth_user_id'], 
    'permission_id': 1})
    assert response.status_code == AccessError().code

def test_admin_userpermission_change_invalid_id(clear):
    '''
    Testing for invalid id
    '''
    res = requests.post(f'{url}auth/register/v2', json = {
        'email': "hello@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': "Smith"
    })
    user1 = res.json()
    
    res = requests.post(f'{url}auth/register/v2', json = {
        'email': "goodbye@gmail.com",
        'password': "mynameis8",
        'name_first': "John",
        'name_last': "Smith"
    })
    user2 = res.json()
    
    response = requests.post(f'{url}admin/userpermission/change/v1', json={
    'token': user1['token'], 
    'u_id':user2['auth_user_id'] + 10, 
    'permission_id': 1
    })
    assert response.status_code == InputError().code

def test_admin_userpermission_invalid_permID(clear):
    '''
    Testing for invalid permission ID
    '''
    res = requests.post(f'{url}auth/register/v2', json = {
        'email': "hello@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': "Smith"
    })
    user1 = res.json()
    
    res = requests.post(f'{url}auth/register/v2', json = {
        'email': "goodbye@gmail.com",
        'password': "mynameis8",
        'name_first': "John",
        'name_last': "Smith"
    })
    user2 = res.json()
    
    response = requests.post(f'{url}admin/userpermission/change/v1', json={
    'token': user1['token'], 
    'u_id':user2['auth_user_id'], 
    'permission_id': -1
    })
    assert response.status_code == InputError().code
    
def test_already_permission_level(clear):
    '''
    Testing if user already has the same permission level
    '''
    res = requests.post(f'{url}auth/register/v2', json = {
        'email': "hello@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': "Smith"
    })
    user1 = res.json()
    
    res = requests.post(f'{url}auth/register/v2', json = {
        'email': "goodbye@gmail.com",
        'password': "mynameis8",
        'name_first': "John",
        'name_last': "Smith"
    })
    user2 = res.json()
    
    response = requests.post(f'{url}admin/userpermission/change/v1', json = {
    'token': user1['token'], 
    'u_id':user2['auth_user_id'], 
    'permission_id': 2})
    
    assert response.status_code == InputError().code
    
def test_demoted_global_user(clear):
    '''
    Testing if a global user is demoted
    '''
    res = requests.post(f'{url}auth/register/v2', json = {
        'email': "hello@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': "Smith"
    })
    user = res.json()
    
    response = requests.post(f'{url}admin/userpermission/change/v1', json = {
    'token': user['token'], 
    'u_id':user['auth_user_id'], 
    'permission_id': 2})
    
    assert response.status_code == InputError().code

def test_valid_userpermission_change(clear):
    '''
    Testing for a valid success using user permission function
    '''
    res = requests.post(f'{url}auth/register/v2', json = {
        'email': "hello@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': "Smith"
    })
    user1 = res.json()
    
    res = requests.post(f'{url}auth/register/v2', json = {
        'email': "goodbye@gmail.com",
        'password': "mynameis8",
        'name_first': "John",
        'name_last': "Smith"
    })
    user2 = res.json()
    
    requests.post(f'{url}admin/userpermission/change/v1', json={
    'token': user1['token'], 
    'u_id':user2['auth_user_id'], 
    'permission_id': 1})
    
    requests.post(f'{url}channels/create/v2', json = {
        "token": user1['token'], 
        "name": 'hi', 
        "is_public": False
    })
    
    response3 = requests.post(f'{url}channel/join/v2', json = {
        'token': user2['token'],
        'channel_id': 1
    })
    
    assert response3.status_code == 200

def test_successful_change(clear):
    '''
    Testing for a valid success using user permission function
    '''
    res = requests.post(f'{url}auth/register/v2', json = {
        'email': "hello@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': "Smith"
    })
    user1 = res.json()
    
    res = requests.post(f'{url}auth/register/v2', json = {
        'email': "goodbye@gmail.com",
        'password': "mynameis8",
        'name_first': "John",
        'name_last': "Smith"
    })
    user2 = res.json()
    
    response = requests.post(f'{url}admin/userpermission/change/v1', json={
    'token': user1['token'], 
    'u_id':user2['auth_user_id'], 
    'permission_id': 1})
    
    response = requests.post(f'{url}admin/userpermission/change/v1', json={
    'token': user2['token'], 
    'u_id':user1['auth_user_id'], 
    'permission_id': 2})
    
    assert response.status_code == 200
#-----------------------------------------------------------------------------
# INVALID LOGOUT TOKEN FOR admin_user_remove_v1 and admin_userpermission_change_v1
def test_invalid_token_admin_user_remove(clear):
    '''
    Invalid token when user logs out before removing user
    '''
    r = requests.post(f'{url}auth/register/v2', json={
        'email':'hello@gmail.com',
        'password':'password', 
        'name_first':'Hayden', 
        'name_last':'Smith'})
    user1 = r.json()
    
    r = requests.post(f'{url}auth/register/v2', json={
        'email':'goodbye@gmail.com',
        'password':'mynameis8!', 
        'name_first':'John', 
        'name_last':'Smith'})
    user2 = r.json()
    
    r = requests.post(f'{url}channels/create/v2', json = {
        "token": user1['token'], 
        "name": 'hi', 
        "is_public": True
    })
    
    r = requests.post(f'{url}channel/join/v2', json = {
        'token': user2['token'],
        'channel_id': 1
    })
    
    requests.post(f'{url}auth/logout/v1', json={'token': user1['token']})
    r = requests.delete(f'{url}admin/user/remove/v1', json={
        'token': user2['token'], 
        'u_id': user1['auth_user_id']})
    
    assert r.status_code == AccessError().code

def test_invalid_token_userperm_change(clear):
    '''
    Invalid token when user tries to change permissions after logging out
    '''
    res = requests.post(f'{url}auth/register/v2', json = {
        'email': "hello@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': "Smith"
    })
    user1 = res.json()
    
    res = requests.post(f'{url}auth/register/v2', json = {
        'email': "goodbye@gmail.com",
        'password': "mynameis8",
        'name_first': "John",
        'name_last': "Smith"
    })
    user2 = res.json()
    requests.post(f'{url}auth/logout/v1', json={'token': user1['token']})
    response = requests.post(f'{url}admin/userpermission/change/v1', json={
    'token': user1['token'], 
    'u_id':user2['auth_user_id'], 
    'permission_id': 1})
    
    assert response.status_code == AccessError().code
#-----------------------------------------------------------------------------
