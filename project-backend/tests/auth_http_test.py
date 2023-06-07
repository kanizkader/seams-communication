'''
Testing for:
    - auth_login_v2
    - auth_register_v2
    - auth_logout_v1
    - auth_passwordreset_request_v1
    - auth_passwordreset_reset_v1
'''
import re
from urllib import response
import pytest
import json
from src.config import url
import requests
from src.error import AccessError, InputError
#-----------------------------------------------------------------------------
# FIXTURES
@pytest.fixture
def clear():
    requests.delete(f'{url}/clear/v1')

@pytest.fixture
def jack():
    return requests.post(f"{url}auth/register/v2", json={'email':'z5359521@ad.unsw.edu.au', 'password' : 'Pass54321word', 'name_first':'Jack', 'name_last':'Hill'})
#-----------------------------------------------------------------------------
#TESTING AUTH REGISTER AND AUTH LOGIN    
def test_register_invalid_email(clear):
    '''
    Testing for invalid email
    '''
    res = requests.post(f'{url}/auth/register/v2', json={
        'email': "abc",
        'password': "password",
        'name_first': "Hayden",
        'name_last': "Smith"
    })
    assert res.status_code == InputError().code
        
def test_register_invalid_password(clear):
    '''
    Testing for invalid password
    '''
    res = requests.post(f'{url}/auth/register/v2', json={
        'email': "hello@gmail.com",
        'password': "abc",
        'name_first': "Hayden",
        'name_last': "Smith"
    })
    assert res.status_code == InputError().code

def test_register_invalid_first_name_min(clear):
    '''
    Testing for minimum first name
    '''
    res = requests.post(f'{url}/auth/register/v2', json={
        'email': "hello@gmail.com",
        'password': "password",
        'name_first': 0 * "A",
        'name_last': "Smith"
    })
    assert res.status_code == InputError().code

def test_register_invalid_first_name_max(clear):
    '''
    Testing for maximum first name
    '''
    res = requests.post(f'{url}/auth/register/v2', json={
        'email': "hello@gmail.com",
        'password': "password",
        'name_first': 51 * "A",
        'name_last': "Smith"
    })
    assert res.status_code == InputError().code
    
def test_register_invalid_last_name_max(clear):
    '''
    Testing for maximum last name
    '''
    res = requests.post(f'{url}/auth/register/v2', json={
        'email': "hello@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': 51 * "A"
    })
    assert res.status_code == InputError().code 
    
def test_register_invalid_last_name_min(clear):
    '''
    Testing for minimum last name
    '''
    res = requests.post(f'{url}/auth/register/v2', json={
        'email': "hello@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': 0 * "A"
    })
    assert res.status_code == InputError().code     
        
def test_user_duplicate(clear):
    '''
    Testing for user duplicate
    '''
    requests.post(f'{url}/auth/register/v2', json={
        'email': "hello@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': "Smith"
    })
    
    res = requests.post(f'{url}/auth/register/v2', json={
        'email': "hello@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': "Smith"
    })
    assert res.status_code == InputError().code

def test_valid_register(clear):
    '''
    Testing for a valid regsiter
    '''
    res = requests.post(f'{url}/auth/register/v2', json={
        'email': "bye@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': "Smith"})
    user1 = res.json()
    
    res = requests.post(f'{url}/auth/register/v2', json={
        'email': "john@gmail.com", 
        'password': "password",
        'name_first': "John",
        'name_last': "Smith"})
    user2 = res.json()
    
    assert res.status_code == 200
    assert user1['auth_user_id'] == 1 and user2['auth_user_id'] == 2
    
def test_invalid_email_login(clear):
    '''
    Testing for invalid email login
    '''
    res = requests.post(f'{url}/auth/register/v2', json={
        'email': "bye@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': "Smith"})
    res.json()
    
    response = requests.post(f'{url}/auth/login/v2', json={
        'email' : 'wrongemail@gmail.com',
        'password' : 'password'
    })
    response.json()
    assert response.status_code == InputError().code

def test_user_does_not_exist(clear):
    '''
    Testing for invalid email login
    '''
    response = requests.post(f'{url}/auth/login/v2', json={
        'email' : 'hi@gmail.com',
        'password' : 'Password123'
    })
    
    assert response.status_code == InputError().code
    
def test_incorrect_password(clear):
    '''
    Testing for incorrect password
    '''
    res = requests.post(f'{url}/auth/register/v2', json={
        'email': "bye@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': "Smith"})
    res.json()
    
    response = requests.post(f'{url}/auth/login/v2', json = {
        'email' : 'bye@gmail.com',
        'password' : 'mynameis8'
    })
    assert response.status_code == InputError().code

def test_auth_login(clear):
    '''
    Testing for user log in
    '''
    res = requests.post(f'{url}/auth/register/v2', json={
        'email': "hello@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': "Smith"})
    rego_response = res.json()
    
    res = requests.post(f'{url}/auth/login/v2', json = {
        'email' : 'hello@gmail.com',
        'password' : 'password'
    })
    login_response = res.json()
    
    assert res.status_code == 200
    assert rego_response['auth_user_id'] == login_response['auth_user_id']

def test_auth_login2(clear):
    '''
    Testing for user log in
    '''
    res = requests.post(f'{url}/auth/register/v2', json={
        'email': "hello@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': "Smith"})
    res.json()
    
    res = requests.post(f'{url}/auth/register/v2', json={
        'email': "bye@gmail.com",
        'password': "Password123",
        'name_first': "John",
        'name_last': "Smith"})
    res.json()
    
    res = requests.post(f'{url}/auth/login/v2', json = {
        'email' : 'bye@gmail.com',
        'password' : 'Password123'
    })
    
    assert res.status_code == 200

def test_valid_handles(clear):
    '''
    Testing for duplicating handles generated
    '''
    res = requests.post(f'{url}/auth/register/v2', json={
        'email': "hello@gmail.com",
        'password': "password",
        'name_first': "Hayden",
        'name_last': "Smith"})
    user1 = res.json()
    
    res = requests.post(f'{url}/auth/register/v2', json={
        'email': "hi@gmail.com",
        'password': "password123",
        'name_first': "Hayden",
        'name_last': "Smith"})
    user2 = res.json()
    
    res = requests.post(f'{url}/auth/register/v2', json={
        'email': "bye@gmail.com",
        'password': "password321",
        'name_first': "Hayden",
        'name_last': "Smith"})
    user3 = res.json()
    
    res = requests.get(f'{url}user/profile/v1', params={
        'token': user1['token'], 
        'u_id': user1['auth_user_id']})
    
    assert res.json()['user']['handle_str'] == 'haydensmith'
    
    res = requests.get(f'{url}user/profile/v1', params={
        'token': user2['token'], 
        'u_id': user2['auth_user_id']})
    
    assert res.json()['user']['handle_str'] == 'haydensmith0'
    
    res = requests.get(f'{url}user/profile/v1', params={
        'token': user3['token'], 
        'u_id': user3['auth_user_id']})
    
    assert res.json()['user']['handle_str'] == 'haydensmith1'
    
#-----------------------------------------------------------------------------
#TESTING AUTH LOGOUT
def test_logout_invalid_token(clear):
    '''
    Invalid token used to logout 
    '''
    res = requests.post(f'{url}auth/register/v2', json={
        'email': "z0010230@gmail.com",
        'password': "pass123word",
        'name_first': "Hay",
        'name_last': "Smi"
    })

    res = requests.post(f'{url}auth/logout/v1', json={
        "token": "-1234"
    })
    assert res.status_code == AccessError().code

def test_logout_successful(clear):
    '''
    Successful logout
    '''
    res = requests.post(f'{url}auth/register/v2', json={
        'email': "z0923501@gmail.com",
        'password': "wordpass123",
        'name_first': "Jackson",
        'name_last': "Steph"
    })
    test_user = res.json()

    res = requests.post(f'{url}auth/logout/v1', json={
        "token": test_user['token']
    })
    assert res.status_code == 200

def test_logout_already_logged_out(clear):
    '''
    Already logged out 
    '''
    res = requests.post(f'{url}auth/register/v2', json={
        'email': "z0923501@gmail.com",
        'password': "wordpass123",
        'name_first': "Jackson",
        'name_last': "Steph"
    })
    test_user = res.json()

    res = requests.post(f'{url}auth/logout/v1', json={
        "token": test_user['token']
    })

    res = requests.post(f'{url}auth/logout/v1', json={
        "token": test_user['token']
    })
    assert res.status_code == 403

#-----------------------------------------------------------------------------
#   testing for auth_passwordreset_request_v1
def test_successful_auth_passwordreset_request(clear, jack):
    '''
    Testing Function works
    '''
    res = requests.post(f'{url}auth/passwordreset/request/v1', json={'email': 'z5359521@ad.unsw.edu.au'})
    assert res.status_code == 200
    
def test_invalid_email_auth_passwordreset_request(clear, jack):
    '''
    Testing invalid email
    '''
    res = requests.post(f'{url}auth/passwordreset/request/v1', json={'email': 'zwrong12@ad.unsw.edu.au'})
    assert res.status_code == 200
#-----------------------------------------------------------------------------
#   testing for auth_passwordreset_reset_v1
def test_invalid_password_password_reset(clear, jack):
    '''
    Testing invalid reset code
    '''
    res = requests.post(f'{url}auth/passwordreset/reset/v1', json={'reset_code': 'x', 'new_password': 'abc123'})
    assert res.status_code == InputError().code
    
def test_code_invalid_password_rest(clear, jack):
    '''
    testing invalid password
    '''
    res = requests.post(f'{url}auth/passwordreset/reset/v1', json={'reset_code': 'x', 'new_password': 'abc'})
    assert res.status_code == InputError().code
#-----------------------------------------------------------------------------
