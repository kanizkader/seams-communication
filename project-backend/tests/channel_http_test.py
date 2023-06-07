'''
Testing for:
    - channel_invite_v2
    - channel_details_v2
    - channel_messages_v2
    - channel_join_v2
    - channel_leave_v1
    - channel_addowner_v1
    - channel_removeowner_v1
'''
import pytest
import requests
from src import config
from src.error import AccessError, InputError
import jwt
import json
#-----------------------------------------------------------------------------
BASE_URL = config.url
#----------------------------------------------------------------------------
#FIXTURES
@pytest.fixture
def clear():
    clear_v1 = requests.delete(config.url + 'clear/v1')
    return clear_v1

@pytest.fixture
def token_jack():
    response = requests.post(
        config.url + 'auth/register/v2', json = {
            "email": "z5359521@ad.unsw.edu.au", 
            "password": "Pass54321word", 
            "name_first": "Jack", 
            "name_last": "Hill"
        }
    )
    return response.json()

@pytest.fixture
def channel_id_jack(token_jack):
    response = requests.post(
        config.url + 'channels/create/v2', json = {
            "token": token_jack['token'], 
            "name": "jack_channel", 
            "is_public": True
        }
    )
    return response.json()

@pytest.fixture
def token_sarah():
    response = requests.post(
        config.url + 'auth/register/v2', json = {
            "email": "z5363412@ad.unsw.edu.au", 
            "password": "Parrrpp", 
            "name_first": "Sarah", 
            "name_last": "Cat"
        }
    )
    return response.json()

@pytest.fixture
def invite_sarah(token_jack, channel_id_jack, token_sarah):
    response = requests.post(
        config.url + 'channel/invite/v2', json = {
            "token": token_jack['token'], 
            "channel_id": channel_id_jack['channel_id'], 
            "u_id": token_sarah['auth_user_id']
        }
    )
    return response.json()

@pytest.fixture
def token_phil():
    response = requests.post(
        config.url + 'auth/register/v2', json = {
            "email": "z5363124@ad.unsw.edu.au", 
            "password": "notamember!", 
            "name_first": "Phil", 
            "name_last": "Seed"
        }
    )
    return response.json()

@pytest.fixture
def invite_phil(token_jack, channel_id_jack, token_phil):
    response = requests.post(
        config.url + 'channel/invite/v2', json = {
            "token": token_jack['token'], 
            "channel_id": channel_id_jack['channel_id'], 
            "u_id": token_phil['auth_user_id']
        }
    )
    return response.json()

def channel_message_iterator(num, token, channel_id):
    message = str(num)
    requests.post(
        f'{BASE_URL}message/send/v1', json = {
            'token': token['token'],
            'channel_id': channel_id['channel_id'],
            'message': message
        }
    )
#-----------------------------------------------------------------------------
# TEST CHANNEL/DETAILS
def test_valid_channel_details(clear, token_jack, channel_id_jack):
    '''
    Testing valid channel details
    '''
    response = requests.get(
        config.url + "channel/details/v2", params = {
            'token': token_jack['token'], 
            'channel_id': channel_id_jack['channel_id']
        }
    )
    details = response.json()    
    assert response.status_code == 200
    assert len(details['owner_members']) == 1
    assert len(details['all_members']) == 1
    
def test_invalid_ch_id_channel_details(clear, token_jack):
    '''
    Testing invalid channel id
    ''' 
    response = requests.get(
        config.url + "channel/details/v2", params = {
            'token': token_jack['token'], 
            'channel_id': -1
        }
    ) 
    assert response.status_code == InputError().code
    
def test_invalid_user_not_mem_channel_details(clear, token_jack, token_sarah, channel_id_jack):
    '''
    Testing user is not a member of channel
    '''   
    response = requests.get(
        config.url + "channel/details/v2", params = {
            'token': token_sarah['token'], 
            'channel_id': channel_id_jack['channel_id']
        }
    ) 
    assert response.status_code == AccessError().code
    
def test_invalid_user_channel_details(clear, token_jack, channel_id_jack):
    '''
    Testing user channel details incorrect
    '''    
    response = requests.get(
        config.url + "channel/details/v2", params = {
            'token': "-10000", 
            'channel_id': channel_id_jack['channel_id']
        }
    ) 
    assert response.status_code == AccessError().code       
#-----------------------------------------------------------------------------
# TESTING CHANNEL/INVITE
def test_invalid_channel_invite(clear, token_jack, token_sarah):
    '''
    Testing invalid channel given
    '''
    # invalid channel
    invalid_channel_id = requests.post(
        config.url + "channel/invite/v2", json = {
            'token': token_jack['token'], 
            'channel_id': "1000", 
            'u_id': token_sarah['auth_user_id']
        }
    ) 
    assert invalid_channel_id.status_code == InputError().code

def test_invalid_channel_invite_owner(clear, token_jack, token_sarah, channel_id_jack):
    '''
    Testing invalid owner
    '''
    # user not owner
    invalid_owner = requests.post(
        config.url + "channel/invite/v2", json = {
            'token': "-100000", 
            'channel_id': channel_id_jack['channel_id'], 
            'u_id': token_sarah['auth_user_id']
        }
    ) 
    assert invalid_owner.status_code == AccessError().code
    
def test_invalid_u_id_channel_invite(clear, token_jack, channel_id_jack):
    '''
    Testing invalid u_id
    '''
    invalid_u_id = requests.post(
        config.url + "channel/invite/v2", json = {
            'token': token_jack['token'], 
            'channel_id': channel_id_jack['channel_id'], 
            'u_id': "1000"
        }
    )
    assert invalid_u_id.status_code == InputError().code

def test_u_id_already_mem_channel_invite(clear, token_jack, token_sarah, channel_id_jack):
    '''
    Testing when u_id is already member of the channel they are being invited to
    '''
    requests.post(
        config.url + "channel/invite/v2", json = {
            'token': token_jack['token'], 
            'channel_id': channel_id_jack['channel_id'], 
            'u_id': token_sarah['auth_user_id']
        }
    ) 
    u_id_already_mem = requests.post(
        config.url + "channel/invite/v2", json = {
            'token': token_jack['token'], 
            'channel_id': channel_id_jack['channel_id'], 
            'u_id': token_sarah['auth_user_id']
        }
    ) 
    assert u_id_already_mem.status_code == InputError().code

def test_valid_sems_owner_invite(clear, token_sarah, token_jack, channel_id_jack):
    '''
    testing invite from seams owner
    '''
    response = requests.post(
        config.url + "channel/invite/v2", json = {
            'token': token_sarah['token'], 
            'channel_id': channel_id_jack['channel_id'], 
            'u_id': token_sarah['auth_user_id']
        }
    ) 
    assert response.status_code == 200

def test_valid_invite(clear, token_sarah, token_jack, token_phil, channel_id_jack):
    response = requests.post(
        config.url + "channel/invite/v2", json = {
            'token': token_jack['token'], 
            'channel_id': channel_id_jack['channel_id'], 
            'u_id': token_sarah['auth_user_id']
        }
    ) 
    assert response.status_code == 200
    response = requests.post(
        config.url + "channel/invite/v2", json = {
            'token': token_jack['token'], 
            'channel_id': channel_id_jack['channel_id'], 
            'u_id': token_phil['auth_user_id']
        }
    ) 
    assert response.status_code == 200
#-----------------------------------------------------------------------------
# TESTS for Channel/Messages/V2 
def test_channel_messages_invalid_token(clear, channel_id_jack):
    '''
    Invalid Token
    '''
    invalid_token = "-100"
    response = requests.get(
            f'{BASE_URL}channel/messages/v2', params = {
            'token': invalid_token,
            'channel_id': channel_id_jack['channel_id'],
            'start': 0
        }
    )
    assert response.status_code == AccessError().code

def test_channel_messages_invalid_member_channel(clear, channel_id_jack, token_sarah):
    '''
    User not member of channel
    '''
    response = requests.get(f'{BASE_URL}channel/messages/v2', params = {
        'token': token_sarah['token'],
        'channel_id': channel_id_jack['channel_id'],
        'start': 0
    })
    assert response.status_code == AccessError().code

def test_channel_messages_invalid_channel_id(clear, token_jack):
    '''
    Invalid Channel ID
    '''
    invalid_channel_id = -100
    response = requests.get(f'{BASE_URL}channel/messages/v2', params = {
        'token': token_jack['token'],
        'channel_id': invalid_channel_id,
        'start': 0
    })
    assert response.status_code == InputError().code

def test_channel_messages_invalid_start(clear, token_jack, channel_id_jack):
    '''
    Invalid Start
    '''
    response = requests.get(f'{BASE_URL}channel/messages/v2', params = {
        'token': token_jack['token'],
        'channel_id': channel_id_jack['channel_id'],
        'start': 50
    })
    assert response.status_code == InputError().code

def test_channel_messages_valid(clear, token_jack, channel_id_jack):
    '''
    Valid Case
    '''
    response = requests.get(f'{BASE_URL}channel/messages/v2', params = {
        'token': token_jack['token'],
        'channel_id': channel_id_jack['channel_id'],
        'start': 0
    })
    assert response.status_code == 200 

def test_channel_message_valid_start(clear, token_jack, channel_id_jack):
    '''
    Valid Start
    '''
    for i in range(51):
        channel_message_iterator(i, token_jack, channel_id_jack)

    response = requests.get(f'{BASE_URL}channel/messages/v2', params = {
        'token': token_jack['token'],
        'channel_id': channel_id_jack['channel_id'],
        'start': 51
    })
    assert response.status_code == 200 
    response = requests.get(f'{BASE_URL}channel/messages/v2', params = {
        'token': token_jack['token'],
        'channel_id': channel_id_jack['channel_id'],
        'start': 5
    })
    assert response.status_code == 200 
    
def test_valid_channel_messages(clear, token_jack, channel_id_jack):
    '''
    Valid Case 2
    '''
    response = requests.get(f'{BASE_URL}channel/messages/v2', params = {
        'token': token_jack['token'],
        'channel_id': channel_id_jack['channel_id'],
        'start': 0
    })
    assert response.status_code == 200

def test_channel_messages_owner_of_seams(clear, token_sarah, token_jack, channel_id_jack):
    '''
    test owner of seams can access all messages
    '''
    response = requests.get(f'{BASE_URL}channel/messages/v2', params = {
        'token': token_sarah['token'],
        'channel_id': channel_id_jack['channel_id'],
        'start': 0
    })
    assert response.status_code == 200
#-----------------------------------------------------------------------------
# TESTS for Channel/Join/V2

def test_channel_join_invalid_token(clear, channel_id_jack):
    '''
    Invalid Token
    '''
    invalid_token = "-100"
    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': invalid_token,
        'channel_id': channel_id_jack['channel_id']
    })
    assert response.status_code == AccessError().code

def test_channel_join_private_channel(clear, token_jack, token_sarah):
    '''
    User trying to join private channel
    '''
    response = requests.post(f'{BASE_URL}channels/create/v2', json = {
        'token': token_jack['token'],
        'name': "private_channel",
        'is_public': False
    })
    private = response.json()
    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_sarah['token'],
        'channel_id': private['channel_id']
    })
    assert response.status_code == AccessError().code

def test_channel_join_invalid_channel_id(clear, token_jack):
    '''
    Invalid Channel ID
    '''
    invalid_channel_id = -1
    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_jack['token'],
        'channel_id': invalid_channel_id
    })
    assert response.status_code == InputError().code
#-----------------------------------------------------------------------------
# TESTING FOR CHANNEL_LEAVE_1
def test_channel_leave_successful(clear, token_jack, channel_id_jack, token_sarah, invite_sarah):
    '''
    when valid member successfully leaves channel he was in
    '''
    response = requests.post(
        config.url + 'channel/leave/v1', json = {
            "token": token_sarah['token'], 
            "channel_id": channel_id_jack['channel_id']
        }
    )
    assert response.status_code == 200

def test_channel_leave_invalid_channel(clear, token_jack, channel_id_jack, token_sarah):
    '''
    when valid member tries to leave an invalid channel
    '''
    response = requests.post(
        config.url + 'channel/invite/v2', json = {
            "token": token_jack['token'], 
            "channel_id": channel_id_jack['channel_id'], 
            "u_id": token_sarah['auth_user_id']
        }
    )
    response = requests.post(
        config.url + 'channel/leave/v1', json= {
            "token": token_sarah['token'], 
            "channel_id": -1234
        }
    )
    assert response.status_code == InputError().code

def test_channel_leave_invalid_member(clear, token_phil, channel_id_jack):
    '''
    when user that is attempting to leave is not a member of the specified channel
    '''
    response = requests.post(
        config.url + 'channel/leave/v1', json = {
            "token": token_phil['token'], 
            "channel_id": channel_id_jack['channel_id']
        }
    )
    assert response.status_code == AccessError().code

def test_channel_invalid_token(clear, token_jack, channel_id_jack):
    '''
    when token invalid
    '''
    response = requests.post(
        config.url + 'channel/leave/v1', json = {
            "token": "-1234", 
            "channel_id": channel_id_jack['channel_id']
        }
    )
    assert response.status_code == 403
#-----------------------------------------------------------------------------
# TESTING FOR CHANNEL_ADDOWNER_V1
def test_addowner_successful(clear, token_jack, token_sarah, invite_sarah, channel_id_jack):
    '''
    successful add owner
    '''
    response = requests.post(
        config.url + 'channel/addowner/v1', json = {
            "token": token_jack['token'], 
            "channel_id": channel_id_jack['channel_id'], 
            "u_id": token_sarah['auth_user_id']
        }
    )
    assert response.status_code == 200  

def test_addowner_invalid_channel(clear, token_jack, token_sarah, invite_sarah):
    '''
    when channel_id is invalid
    '''
    response = requests.post(config.url + 'channel/addowner/v1', json = {
        "token": token_jack['token'], 
        "channel_id": '-1234', 
        "u_id": token_sarah['auth_user_id']
    })
    assert response.status_code == InputError().code

def test_addowner_invalid_u_id(clear, token_jack, channel_id_jack):
    '''
    when u_id is invalid
    '''
    response = requests.post(config.url + 'channel/addowner/v1', json = {
        "token": token_jack['token'], 
        "channel_id": channel_id_jack['channel_id'], 
        "u_id": -1234
    })
    assert response.status_code == InputError().code

def test_addowner_invalid_member(clear, token_jack, channel_id_jack, token_phil):
    '''
    when u_id referring to a user not that is not member of specified channel
    '''
    response = requests.post(config.url + 'channel/addowner/v1', json = {
        "token": token_jack['token'], 
        "channel_id": channel_id_jack["channel_id"], 
        "u_id": token_phil['auth_user_id']
    })
    assert response.status_code == InputError().code

def test_addowner_already_owner(clear, token_jack, channel_id_jack):
    '''
    when u_id refers to a user who is already an owner of the channel
    '''
    response = requests.post(config.url + 'channel/addowner/v1', json = {
        "token": token_jack['token'], 
        "channel_id": channel_id_jack['channel_id'], 
        "u_id": token_jack['auth_user_id']
    })
    assert response.status_code == InputError().code

def test_addowner_not_owner(clear, token_sarah, channel_id_jack, invite_phil, token_phil):
    '''
    when channel_id is valid and the authorised user 
    does not have owner permissions in the channel
    '''
    response = requests.post(config.url + 'channel/addowner/v1', json = {
        "token": token_sarah['token'], 
        "channel_id": channel_id_jack["channel_id"], 
        "u_id": token_phil['auth_user_id']
    })
    assert response.status_code == AccessError().code

def test_addowner_invalid_token(clear, token_sarah, invite_sarah, channel_id_jack, token_phil):
    '''
    when token is invalid
    '''
    response = requests.post(config.url + 'channel/addowner/v1', json = {
        "token": "-1", 
        "channel_id": channel_id_jack['channel_id'], 
        "u_id": token_sarah['auth_user_id']
    })
    assert response.status_code == AccessError().code  
#-----------------------------------------------------------------------------
# TESTING FOR CHANNEL_REMOVEOWNER_V1
def test_removeowner_successful(clear, token_jack, token_sarah, invite_sarah, channel_id_jack):
    '''
    successful remove owner
    '''
    response = requests.post(config.url + 'channel/addowner/v1', json = {
        "token": token_jack['token'], 
        "channel_id": channel_id_jack['channel_id'], 
        "u_id": token_sarah['auth_user_id']
    })
    response = requests.post(config.url + 'channel/removeowner/v1', json = {
        "token": token_jack['token'], 
        "channel_id": channel_id_jack["channel_id"], 
        "u_id": token_sarah["auth_user_id"]
    })
    assert response.status_code == 200 

def test_removeowner_invalid_channel(clear, token_jack, token_sarah, invite_sarah):
    '''
    when channel_id is invalid
    '''
    response = requests.post(config.url + 'channel/removeowner/v1', json = {
        "token": token_jack['token'], 
        "channel_id": -1234, 
        "u_id": token_sarah['auth_user_id']
    })
    assert response.status_code == InputError().code

def test_removeowner_invalid_u_id(clear, token_jack, channel_id_jack):
    '''
    when u_id is invalid
    '''
    response = requests.post(config.url + 'channel/removeowner/v1', json = {
        "token": token_jack['token'], 
        "channel_id": channel_id_jack['channel_id'], 
        "u_id": -1234
    })
    assert response.status_code == InputError().code

def test_removeowner_invalid_member(clear, token_jack, channel_id_jack, token_phil):
    '''
    when u_id referring to a user not that is not member of specified channel
    '''
    response = requests.post(config.url + 'channel/removeowner/v1', json = {
        "token": token_jack['token'], 
        "channel_id": channel_id_jack["channel_id"], 
        "u_id": token_phil["auth_user_id"]
    })
    assert response.status_code == InputError().code

def test_removeowner_only_owner(clear, token_jack, channel_id_jack):
    '''
    u_id refers to a user who is currently the only owner of the channel
    '''
    response = requests.post(config.url + 'channel/removeowner/v1', json = {
        "token": token_jack['token'], 
        "channel_id": channel_id_jack['channel_id'], 
        "u_id": token_jack['auth_user_id']
    })
    assert response.status_code == InputError().code

def test_removeowner_not_owner(clear, token_sarah, channel_id_jack, invite_phil, token_phil):
    '''
    when channel_id is valid and the authorised user does not have owner permissions in the channel
    '''
    response = requests.post(config.url + 'channel/removeowner/v1', json = {
        "token": token_sarah['token'], 
        "channel_id": channel_id_jack["channel_id"], 
        "u_id": token_phil["auth_user_id"]
    })
    assert response.status_code == InputError().code

def test_removeowner_invalid_token(clear, token_sarah, invite_sarah, channel_id_jack, token_phil):
    '''
    when token is invalid
    '''
    response = requests.post(config.url + 'channel/removeowner/v1', json = {
        "token": token_phil['token'], 
        "channel_id": channel_id_jack['channel_id'], 
        "u_id": token_sarah['auth_user_id']
    })
    assert response.status_code == AccessError().code  
#-----------------------------------------------------------------------------
# INVALID TOKEN LOGOUT FOR CHANNEL FUNCTIONS
def test_invalid_token_channel_details(clear, token_jack, channel_id_jack):
    '''
    Invalid Token when User logs out
    '''
    requests.post(config.url + 'auth/logout/v1', json={'token': token_jack['token']})
    response = requests.get(config.url + "channel/details/v2", params = {
        'token': token_jack['token'], 
        'channel_id': channel_id_jack['channel_id']
    }) 
    assert response.status_code == AccessError().code 

def test_invalid_token_channel_invite(clear, token_jack, channel_id_jack, token_sarah):
    '''
    Invalid Token when User logs out
    '''
    requests.post(config.url + 'auth/logout/v1', json={
        'token': token_jack['token']
    })
    response = requests.post(config.url + "channel/invite/v2", json = {
        'token': token_jack['token'], 
        'channel_id': channel_id_jack['channel_id'], 
        'u_id':token_sarah['auth_user_id']
    }) 
    assert response.status_code == AccessError().code 

def test_invalid_token_channel_messages(clear, token_jack, channel_id_jack, token_sarah):
    '''
    Invalid Token when User logs out
    '''
    requests.post(config.url + 'auth/logout/v1', json={
        'token': token_jack['token']
    })
    response = requests.get(f'{BASE_URL}channel/messages/v2', params = {
        'token': token_jack['token'],
        'channel_id': channel_id_jack['channel_id'],
        'start': 0
    })
    assert response.status_code == AccessError().code 

def test_invalid_token_channel_join_logout(clear, token_jack, channel_id_jack, token_sarah):
    '''
    Invalid Token when User logs out
    '''
    requests.post(config.url + 'auth/logout/v1', json={'token': token_jack['token']})
    response = requests.post(f'{BASE_URL}channel/join/v2', json = {
        'token': token_jack['token'],
        'channel_id': channel_id_jack['channel_id']
    })
    assert response.status_code == AccessError().code 

def test_invalid_token_channel_leave_logout(clear, token_jack, channel_id_jack, token_sarah):
    '''
    Invalid Token when User logs out
    '''
    requests.post(config.url + 'auth/logout/v1', json={'token': token_jack['token']})
    response = requests.post(config.url + 'channel/leave/v1', json = {
        "token": token_jack['token'], 
        "channel_id": channel_id_jack['channel_id']
    })
    assert response.status_code == AccessError().code 

def test_invalid_token_channel_addowner_logout(clear, token_jack, channel_id_jack, token_sarah):
    '''
    Invalid Token when User logs out
    '''
    requests.post(config.url + 'auth/logout/v1', json={
        'token': token_jack['token']
    })
    response = requests.post(config.url + 'channel/addowner/v1', json = {
        "token": token_jack['token'], 
        "channel_id": channel_id_jack['channel_id'], 
        "u_id": token_sarah['auth_user_id']
    })
    assert response.status_code == AccessError().code 

def test_invalid_token_channel_removeowner_logout(clear, token_jack, channel_id_jack, token_sarah):
    '''
    Invalid Token when User logs out
    '''
    requests.post(config.url + 'auth/logout/v1', json={
        'token': token_jack['token']
    })
    response = requests.post(config.url + 'channel/removeowner/v1', json = {
        "token": token_jack['token'], 
        "channel_id": channel_id_jack['channel_id'], 
        "u_id": token_sarah['auth_user_id']
    })
    assert response.status_code == AccessError().code 
#-----------------------------------------------------------------------------
