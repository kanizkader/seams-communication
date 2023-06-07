'''
Implementation for:
    - admin_user_remove_v1
    - admin_userpermission_change_v1
'''
from src.data_store import data_store
import requests
import json 
import jwt
from helpers.valid_user_helper import check_valid_u_id, decode_jwt, check_valid_auth_user_id, check_token_valid
from helpers.other_helper import generate_jwt
from src.error import InputError, AccessError
#-----------------------------------------------------------------------------
def admin_user_remove_v1(token, u_id):
    '''
    <Given a user by their u_id, remove them from the Seams. This means they should be removed from all channels/DMs, 
    and will not be included in the list of users returned by users/all. Seams owners can remove other Seams owners 
    (including the original first owner). Once users are removed, the contents of the messages they sent will be replaced 
    by 'Removed user'. Their profile must still be retrievable with user/profile, however name_first should be 'Removed' 
    and name_last should be 'user'. The user's email and handle should be reusable.>    
    Arguments:
        - token :: [str] - The user's token.
        - u_id :: [int] - List of user ids.
    Exceptions: 
        InputError - Occurs when:
            - u_id does not refer to a valid user
            - u_id refers to a user who is the only global owner
        AccessError - Occurs when:
            - invalid token
            - the authorised user is not a global owner
    Return Value:
        {}
    '''
    store = data_store.get()
    check_token_valid(token)
    data = decode_jwt(token)
    auth_user_id = data['auth_user_id']
    check_valid_auth_user_id(auth_user_id) 
    check_valid_u_id(u_id)

    #Check if user calling function is an owner
    for user in store['users']:
        if user['auth_user_id'] == data['auth_user_id']:
            if user['perm_id'] == 2:
                raise AccessError(description="User calling function is not an owner")
            
    #Check if user is the only owner
    owner_counter = 0
    for user in store["users"]:
        if user["auth_user_id"] == u_id:
            for check_others in store["users"]:
                if check_others["perm_id"] == 1:
                    owner_counter += 1
            if user["perm_id"] == 1 and owner_counter == 1:
                raise InputError(description="User being removed is currently the only global owner")

    #Remove User from Channel
    for channel in store["channels"]:
        for owner in channel["owner_members"]:
            if owner["u_id"] == u_id:
                channel['owner_members'].remove(owner)              
        for member in channel["all_members"]:
            if member["u_id"] == u_id:
                channel['all_members'].remove(member)
        for channel_message in channel["messages"]:
            if channel_message["u_id"] == u_id:
                channel_message["u_id"] = 'Removed User'
                
    #Remove User's Dms
    for dm in store["dms"]:
        for dm_owner in dm["owner_members"]:
            if dm_owner["u_id"] == u_id:
                dm['owner_members'].remove(dm_owner)
        for dm_member in dm["all_members"]:
            if dm_member["u_id"] == u_id:
                dm['all_members'].remove(dm_member)
        for dm_message in dm["messages"]:
            if dm_message["u_id"] == u_id:
                dm_message['u_id'] = 'Removed User'
                
    #Remove User's Details
    for user in store["users"]:
        if user["auth_user_id"] == u_id:
            user["name_first"] = "Removed"
            user["name_last"] = "user"
            store["removed_users"].append(user)
            store["users"].pop(store["users"].index(user))
            
    data_store.set(store)
    return {}
#----------------------------------------------------------------------------
def admin_userpermission_change_v1(token, u_id, permission_id):
    '''
    Given a user by their user ID, set their permissions to new permissions described by permission_id.
    Arguments:
        token :: [str] - The user's token.
        u_id :: [int] - List of user ids.
        permission_id :: [int] - User's permission ID
    Exceptions: 
        InputError - Occurs when:
            - u_id does not refer to a valid user
            - u_id refers to a user who is the only global owner and they are being demoted to a user
            - permission_id is invalid
        AccessError - Occurs when:
        - the authorised user is not a global owner
    Return Value:
        {}
    '''
    store = data_store.get()
    check_token_valid(token)
    data = decode_jwt(token)
    auth_user_id = data['auth_user_id']
    check_valid_auth_user_id(auth_user_id) 
    check_valid_u_id(u_id)
    
    #Check if valid perm_ID
    valid_perm_IDs = [1,2]
    if permission_id not in valid_perm_IDs:
        raise InputError(description = "Invalid permission ID")
    
    #Check if user calling function is an owner
    for user in store['users']:
        if user['auth_user_id'] == data['auth_user_id'] and user['perm_id'] == 2:
            raise AccessError(description="User calling function is not an owner")
    
    #Check if user is the only owner
    owner_counter = 0
    for user in store["users"]:
        if user["auth_user_id"] == u_id:
            for check_others in store["users"]:
                if check_others["perm_id"] == 1:
                    owner_counter += 1
            if user["perm_id"] == 1 and owner_counter == 1:
                raise InputError(description="User being removed is currently the only global owner")
            elif user['perm_id'] == permission_id:
                raise InputError(description = 'User already has permission ID')  
            else:
                user['perm_id'] = permission_id
    data_store.set(store)
    return{}
#-----------------------------------------------------------------------------
    