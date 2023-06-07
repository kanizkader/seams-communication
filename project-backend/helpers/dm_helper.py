from src.data_store import data_store
from helpers.user_stat_helper import auth_id_to_user 
from src.error import AccessError, InputError
from helpers.notifications_helper import check_tagging
from time import time

def find_dm_id(dm_id):
    '''
    gets the dm_id
    '''
    store = data_store.get()
    for dm in store['dms']:        
        if dm['dm_id'] == dm_id:
            return dm
    raise InputError(description="Dm_id does not refer to a valid DM")
    
def find_dm_message_id(message_id):
    '''
    Find message_id and return message
    '''
    store = data_store.get()
    for dms in store['dms']:
        for message in dms['messages']:
            if message_id == message['message_id']:
                return message
    raise InputError(description='Error: Message not found')

def find_dm_member(dm, auth_user_id):
    '''
    find dm member from all_members
    '''
    store = data_store.get()
    for dms in store['dms']:
        if dm['dm_id'] == dms['dm_id']:
            for member in dm['all_members']:
                if member['u_id'] == auth_user_id:
                    return dm
    raise AccessError(description="User is not part of DM")

def find_dm_owner(dm, auth_user_id):
    '''
    find owner of dm
    '''
    store = data_store.get()
    for dms in store['dms']:
        if dm['dm_id'] == dms['dm_id']:
            for member in dm['owner_members']:
                if member['u_id'] == auth_user_id:
                    return dm
    raise AccessError(description="the authorised user is not the original DM creator")

def create_sendlaterdm(auth_user_id, dm_id, message):
    '''
    Sends dm later after sleep time
    '''
    store = data_store.get()
    # check that the dm still exists
    dm = find_dm_id(dm_id)
    store['message_num'] += 1
    message_id = store['message_num']
    
    # check that sender is still a member of dm
    find_dm_member(dm, auth_user_id)
    dm['messages'].append({
        'message_id': message_id,
        'u_id': auth_user_id,
        'message': message,
        'time_sent': int(time()),
        'reacts': [],
        'is_pinned': False,
    })           
    for dm in store['dms']:        
        if dm['dm_id'] == dm_id:
            dm_name = dm['name']
    check_tagging(auth_user_id, dm_name, message, False, dm_id) 
    data_store.set(store)   
    return message_id

def dm_id_to_dm(dm_id):
    '''
    Find dm_id and return dm
    '''
    store = data_store.get()
    for dm in store["dms"]:
        if dm["dm_id"] == dm_id:
            return dm
    raise InputError

def auth_user_in_dm(auth_user_id, dm_id):
    '''
    Returns true if user is in dm
    '''
    user = auth_id_to_user(auth_user_id)
    dm = dm_id_to_dm(dm_id)
    if user in dm["all_members"] or user in dm["owner_members"]:
        return True

    return False

def find_dm_member_bool(dm, auth_user_id):
    '''
    find dm member from all_members
    '''
    for member in dm['all_members']:
        if member['u_id'] == auth_user_id:
            return True
    return False