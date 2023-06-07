from src.data_store import initial_object, data_store
import jwt
import re
from unicodedata import name
from xxlimited import new
from json import dump, load
from os import path
from helpers.membership_helper import check_global_owner
from helpers.channel_helper import find_channel_id, find_channel_member
from helpers.valid_user_helper import decode_jwt
from src.error import AccessError, InputError
from time import time
from helpers.notifications_helper import check_tagging

def check_message_len(message):
    '''
    check message length is between 1 and 1000
    '''
    if len(message) > 1000 or len(message) < 1:
        raise InputError(description="Must be 1000 characters or less")

def check_message_owner_or_sender_channel(channel, message, auth_user_id):
    '''
    check whether the user is a sender of the message
    or owner of the channel
    '''
    store = data_store.get()
    for channels in store['channels']:
        if channels['channel_id'] == channel['channel_id']:
            for owner in channels['owner_members']:
                # if owner
                if owner['u_id'] == auth_user_id:
                    return True
                # if sender
                elif message['u_id'] == auth_user_id:
                    return True 
    if check_global_owner(auth_user_id) == True:
        return True
    raise AccessError(description='User is unauthorised to do this action')

def check_message_owner_or_sender_dm(dm, message, auth_user_id):
    '''
    checks whether user is owner of dm or sender of dm message
    '''
    store = data_store.get()
    for dms in store['dms']:
        if dms['dm_id'] == dm['dm_id']:
            for owner in dms['owner_members']:
                # if owner
                if owner['u_id'] == auth_user_id:
                    return True
                # if sender
                elif message['u_id'] == auth_user_id:
                    return True 
    if check_global_owner(auth_user_id) == True:
        return True
    raise AccessError(description='User is unauthorised to do this action')

def find_message_id(message_id):
    '''
    find message id
    '''
    store = data_store.get()
    for channel in store['channels']:
        for message in channel['messages']:
            if message['message_id'] == message_id:
                return message
    raise InputError(description='Error: Message not found')

def dm_or_channel(message_id, auth_user_id):
    '''
    find the message exists
    '''
    store = data_store.get()
    # no_message = True
    for channel in store['channels']:
        if found_message_in_channel(channel, message_id):
            return channel
    
    for dms in store['dms']:
        if found_message_in_dm(dms, message_id):
            return dms

def found_message_in_dm_or_channel_for_mem(message_id, auth_user_id):
    '''
    find the message exists
    '''
    store = data_store.get()
    no_message = True
    for channel in store['channels']:
        if found_message_in_channel(channel, message_id):
            no_message = False
            if found_channel_mem_or_global_owner(channel, auth_user_id):
                return found_message_in_channel(channel, message_id)
    
    for dms in store['dms']:
        if found_message_in_dm(dms, message_id):
            no_message = False
            if found_dm_mem(dms, auth_user_id):
                return found_message_in_dm(dms, message_id)

    if no_message:
        raise InputError(description="Message was not found")
    raise AccessError(description="User is not in channel or DM")

def found_channel_mem_or_global_owner(channel, auth_user_id):
    '''
    Return True if user is channel member or global owner
    '''
    store = data_store.get()
    for channels in store['channels']:
        if channels['channel_id'] == channel['channel_id']:
            for member in channels['all_members']:
                if auth_user_id == member['u_id']:
                    return True
    if check_global_owner(auth_user_id):
        return True
    return False

def found_dm_mem(dm, auth_user_id):
    '''
    Returns true if owner is dm member
    '''
    store = data_store.get()
    for dms in store['dms']:
        if dms['dm_id'] == dm['dm_id']:
            for member in dms['all_members']:
                if auth_user_id == member['u_id']:
                    return True
    return False

def found_message_in_dm_or_channel_for_owner(message_id, auth_user_id):
    '''
    find the message exists
    '''
    store = data_store.get()
    no_message = True
    for channel in store['channels']:
        if found_message_in_channel(channel, message_id):
            no_message = False
            if found_channel_or_global_owner(channel, auth_user_id):
                return found_message_in_channel(channel, message_id)
    
    for dms in store['dms']:
        if found_message_in_dm(dms, message_id):
            no_message = False
            if found_dm_owner(dms, auth_user_id):
                return found_message_in_dm(dms, message_id)

    if no_message:
        raise InputError(description="Message was not found")
    raise AccessError(description="No owner permissions")

def found_channel_or_global_owner(channel, auth_user_id):
    '''
    Return true if user is channel owner or global owner
    '''
    store = data_store.get()
    for channels in store['channels']:
        if channels['channel_id'] == channel['channel_id']:
            for member in channels['owner_members']:
                if auth_user_id == member['u_id']:
                    return True
    if check_global_owner(auth_user_id):
        return True
    return False

def found_dm_owner(dm, auth_user_id):
    '''
    Returns true if user is dm owner
    '''
    store = data_store.get()
    for dms in store['dms']:
        if dms['dm_id'] == dm['dm_id']:
            for member in dms['owner_members']:
                if auth_user_id == member['u_id']:
                    return True
    return False

def found_message_in_channel(channel, message_id):
    '''
    find if the message exists in the channel
    '''
    store = data_store.get()
    for channels in store['channels']:
        if channels['channel_id'] == channel['channel_id']:
            for messages in channels['messages']:
                if message_id == messages['message_id']:
                    return messages
    return False

def found_message_in_dm(dm, message_id):
    '''
    Find the message in the dm and return the message
    '''
    store = data_store.get()
    for dms in store['dms']:
        if dms['dm_id'] == dm['dm_id']:
            for messages in dm['messages']:
                if message_id == messages['message_id']:
                    return messages
    return False

def handle_to_u_id(handle):
    '''
    Given the handle, returns the auth_user_id
    '''
    store = data_store.get()
    for user in store['users']:
        if user['handle_str'] == handle:
            return user['auth_user_id']

def create_sendlater_message(auth_user_id, channel_id, message):
    '''
    Creates a message for sendlater after wait is over
    '''
    store = data_store.get()
    # check that the dm still exists
    channel = find_channel_id(channel_id)
    store['message_num'] += 1
    message_id = store['message_num']
    
    # check that sender is still a member of channel
    find_channel_member(channel, auth_user_id)
    channel['messages'].append({
        'message_id': message_id,
        'u_id': auth_user_id,
        'message': message,
        'time_sent': int(time()),
        'reacts': [],
        'is_pinned': False,
    })           
    for channel in store['channels']:        
        if channel['channel_id'] == channel_id:
            channel_name = channel['name']
    check_tagging(auth_user_id, channel_name, message, True, channel_id)
    data_store.set(store)   
    return message_id

def messege_send_standup(token, channel_id, message):
    '''
    Sends a message when its a standup
    '''
    store = data_store.get() 
    token_data = decode_jwt(token)
    auth_user_id = token_data['token']
    channel = find_channel_id(channel_id)
    find_channel_member(channel, auth_user_id)
        
    store['message_num'] += 1
    new_message = {
        'message_id': store['message_num'],
        'u_id': auth_user_id,
        'message': message,
        'time_sent': int(time()),
        'reacts': [],
        'is_pinned': False,
    }

    new_message['reacts'].append({
        'react_id': 1,
        'u_ids': [],
        'is_this_user_reacted': False
    })

    channel['messages'].append(new_message)
    data_store.set(store)
    return {
        'message_id': store['message_num'],
    }

def dm_or_channel_2(message_id):
    '''
    find the message exists
    '''
    store = data_store.get()
    for channel in store['channels']:
        if found_message_in_channel(channel, message_id):
            return [channel['name'], True, channel['channel_id'], channel['all_members']]
    
    for dm in store['dms']:
        if found_message_in_dm(dm, message_id):
            return [dm['name'], False, dm['dm_id'], dm[ 'all_members']]

def find_message(message_id):
    '''
    find message id
    '''
    store = data_store.get()
    for channel in store['channels']:
        for message in channel['messages']:
            if message['message_id'] == message_id:
                return message
    for dm in store['dms']:
        for message in dm['messages']:
            if message['message_id'] == message_id:
                return message
    raise InputError(description='Error: Message not found')
    