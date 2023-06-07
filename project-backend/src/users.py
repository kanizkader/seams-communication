'''
module for users
'''
from src.error import AccessError
from helpers.valid_user_helper import check_valid_auth_user_id, decode_jwt, check_token_valid
from helpers.channel_helper import auth_user_in_channel
from helpers.dm_helper import auth_user_in_dm
from src.data_store import data_store

def users_all_v1(token):
    '''
    Returns a list of all users and their associated details.
    Method = GET
    Perameters:
        { token }
    Return Type:
        { users }
    '''
    store = data_store.get()
    check_token_valid(token)
    data = decode_jwt(token)
    auth_user_id = data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)
    
    user_list = {'users': []}
    for user in store['users']:
        user_list['users'].append({
            'u_id': user['auth_user_id'],
            'email': user['email'],
            'name_first': user['name_first'] ,
            'name_last': user['name_last'],
            "handle_str": user['handle_str'],
            }
        )
    return user_list

def users_stats_v1(token):
    '''
    Fetches the required statistics about the use of UNSW Seams.
    Method = GET
    Perameters:
        { token }
    Return Type:
        { workspace_stats }
    '''

    store = data_store.get()
    check_token_valid(token)
    data = decode_jwt(token)
    auth_user_id = data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)
    
    num_users = 0
    # Looks at all users in the users dict
    for user in store["users"]:
        found = False
        # Checks for a given user in channel
        for channel in store["channels"]:
            if user['auth_user_id'] == channel["all_members"][-1]['u_id']:
                num_users += 1
                found = True
                break
        # If user was not found in channel, checks for them in dms dict
        if not found:
            for dm in store["dms"]:
                if user['auth_user_id'] == dm["all_members"][-1]['u_id']:
                    num_users += 1
                    break
    store["workspace_stats"]["utilization_rate"] = num_users/store["total_users"]
    data_store.set(store)
    
    return {'workspace_stats' : store['workspace_stats']}

    
