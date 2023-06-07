'''
Implementation for: 
    - channels_list_v2
    - channels_listall_v2
    - channels_create_v2
'''
from src.error import InputError, AccessError
from helpers.other_helper import auth_id_to_user
from helpers.user_stat_helper import update_channel_num_workspace_stats
from helpers.valid_user_helper import check_valid_auth_user_id, decode_jwt, find_user, check_token_valid
from helpers.channel_helper import get_num_channels
from src.data_store import data_store
from time import time
#-----------------------------------------------------------------------------
def channels_list_v2(token):
    '''
    Provide a list of all channels (and their associated details)
    that the authorised user is part of.
    Parameters:{token}
    Return Type:{channels}
    '''
    store = data_store.get()
    check_token_valid(token)
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)
       
    channel_list = {
        'channels': []
    }
    for channel in store['channels']:
        for member in channel['all_members']:
            if member['u_id'] == auth_user_id:
                channel_list['channels'].append({
                    'channel_id': channel['channel_id'],
                    'name': channel['name']      
                })
    return channel_list
#-----------------------------------------------------------------------------
def channels_listall_v2(token):
    '''
    Provide a list of all channels, including private channels, 
    (and their associated details)
    Parameters:{token}
    Return Type:{ channels }
    '''
    store = data_store.get()
    check_token_valid(token)
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)
    
    channel_list = {'channels': []}
    for channel in store['channels']:
        channel_list['channels'].append({
            'channel_id': channel['channel_id'],
            'name': channel['name']        
        })
    return channel_list
#-----------------------------------------------------------------------------
def channels_create_v2(token, name, is_public):
    '''
    Verifies if parameters input are valid and outputs a channel id 
    Parameters: {token, name, is_public}
    Output: {channel_id}
    '''
    store = data_store.get()
    check_token_valid(token)
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)
            
    #check if name is valid 
    if len(name) > 20 or len(name) < 1: 
        raise InputError(description="Error: Length of name must be between 1 and 20 characters.")
    
    user = find_user(auth_user_id)
    user_details = {
        'auth_user_id': user['auth_user_id'],
        'email': user['email'],
        'password': user['password'],
        'name_first': user['name_first'],
        'name_last': user['name_last'],
        'handle_str': user['handle_str']
    }
            
    #obtain channel id (number of channels)
    num_channels = get_num_channels() + 1
    #create a new channel
    new_channel = {
        "name": name,
        "channel_id": num_channels,
        "is_public": is_public,
        "owner_members": [],
        "all_members": [],
        "messages": [],
        "standup": {
            'time_finish': 0,
            'is_active': False
        }
    }    
    
    new_channel['owner_members'].append(
        {
        'u_id': user_details['auth_user_id'], 
        'name_first': user_details['name_first'], 
        'name_last': user_details['name_last']
        }
    )
    
    new_channel['all_members'].append(
        {
        'u_id': user_details['auth_user_id'], 
        'name_first': user_details['name_first'],
        'name_last': user_details['name_last']
        }
    )

    #add newly created channel to existing dictionary of channels
    store['channels'].append(new_channel)
    user = auth_id_to_user(auth_user_id)
    user["user_stats"]["channels_joined"].append({
        "num_channels_joined" : user["user_stats"]["channels_joined"][-1]["num_channels_joined"] + 1,
        "time_stamp" : int(time())
    })
    data_store.set(store)
    update_channel_num_workspace_stats()
    return {'channel_id': num_channels}
#-----------------------------------------------------------------------------
