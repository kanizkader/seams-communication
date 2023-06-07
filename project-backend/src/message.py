from src.error import AccessError, InputError
from helpers.valid_user_helper import check_valid_auth_user_id, find_user, decode_jwt, check_token_valid
from helpers.message_helper import check_message_len, find_message_id, check_message_owner_or_sender_dm, check_message_owner_or_sender_channel, found_message_in_dm_or_channel_for_mem, found_message_in_dm_or_channel_for_owner, dm_or_channel_2, find_message
from helpers.channel_helper import find_channel_id, find_channel_member
from helpers.dm_helper import find_dm_message_id
from helpers.membership_helper import check_global_owner
from helpers.notifications_helper import check_tagging, find_tagged_users
from src.dm import message_senddm_v1
from helpers.user_stat_helper import update_messages_workspace_stats

from src.data_store import data_store
from time import time
import threading
import jwt
import datetime
from datetime import timezone

def message_send_v1(token, channel_id, message):    
    '''
    <Send a message from the authorised user to the channel specified by channel_id. 
    Note: Each message should have its own unique ID, i.e. no messages should share 
    an ID with another message, even if that other message is in a different channel.>
    Arguments:
        token :: [str] - The user's token
        channel_id :: [int] - The channel_id of the channel, user is invited to
        message :: [str] - a string of the message the user wants to send
    Exceptions: 
        InputError when:      
            - channel_id does not refer to a valid channel
            - length of message is less than 1 or over 1000 characters
        
        AccessError when:      
            - channel_id is valid and the authorised user is not a member of the channel
    Return value:
        { message_id }
    '''
    store = data_store.get() 
    check_token_valid(token) 
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)
    user = find_user(auth_user_id)

    channel = find_channel_id(channel_id)
    find_channel_member(channel, auth_user_id)
    
    check_message_len(message)
    
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

    # check for tagging 
    for channel in store['channels']:        
        if channel['channel_id'] == channel_id:
            channel_name = channel['name']
    check_tagging(auth_user_id, channel_name, message, True, channel_id)

    user["user_stats"]["messages_sent"].append({
        "num_messages_sent" : user["user_stats"]["messages_sent"][-1]["num_messages_sent"] + 1,
        "time_stamp" : int(time())
    })
    data_store.set(store)
    update_messages_workspace_stats(True)
    return {
        'message_id': store['message_num'],
    }

def message_remove_v1(token, message_id):
    '''
    Given a message_id for a message, this message is removed from the channel/DM
    
    
    Parameters:{ token, message_id }
    Return Type:{}
    
    InputError when:
        - message_id does not refer to a valid message within a channel/DM that the authorised user has joined
      
      AccessError when message_id refers to a valid message in a joined channel/DM and none of the following are true:      
        - the message was sent by the authorised user making this request
        - the authorised user has owner permissions in the channel/DM
    
    '''
    store = data_store.get()   
    check_token_valid(token) 
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)

    dm_channel = dm_or_channel_2(message_id)
    message = find_message(message_id)
    if dm_channel[1] == True: 
        for channel in store['channels']:
        # Check if the user trying to delete is a channel owner or sender
            check_message_owner_or_sender_channel(channel, message, auth_user_id)
            channel['messages'].remove(message)
    if dm_channel[1] == False:
        for dm in store['dms']:
            check_message_owner_or_sender_dm(dm, message, auth_user_id)
            dm['messages'].remove(message)
    
    data_store.set(store)
    update_messages_workspace_stats(False)
    return {}


def message_edit_v1(token, message_id, message):
    '''
    Given a message, update its text with new text. If the new message is an empty string, the message is deleted.
    
    HTTP: PUT
    
    Parameters:{ token, message_id, message }
    Return Type:{}
    
    InputError when any of:      
        - length of message is over 1000 characters
        - message_id does not refer to a valid message within a channel/DM that the authorised user has joined
      
    AccessError when message_id refers to a valid message in a joined channel/DM and none of the following are true:      
        - the message was sent by the authorised user making this request
        - the authorised user has owner permissions in the channel/DM
    '''
    store = data_store.get()
    check_token_valid(token)
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)
        
    edit = message
    check_message_len(message)
    dm_channel = dm_or_channel_2(message_id)
    message = find_message(message_id)
    if dm_channel[1] == True: 
        for channel in store['channels']:
            # Check if the user trying to delete is a channel owner or sender
            check_message_owner_or_sender_channel(channel, message, auth_user_id)
            message['message'] = edit
    if dm_channel[1] == False:
        for dm in store['dms']:
            check_message_owner_or_sender_dm(dm, message, auth_user_id)

    # check to see if new message has any new tags
    for user in store['users']:
        if user['auth_user_id'] == auth_user_id:
            sender = user['handle_str']
    names_tagged_new = find_tagged_users(sender, edit)
    names_tagged_old = find_tagged_users(sender, message['message'])
    if names_tagged_new == names_tagged_old:
        data_store.set(store)
        return {}
    for name in names_tagged_new:
        for n in names_tagged_old:
            if name == n:
                names_tagged_new.remove(name)
    names = ''
    for name in names_tagged_new:
        names = names + '@' + name
    check_tagging(auth_user_id, dm_channel[0], names, dm_channel[1], message['message_id'])
    data_store.set(store)
    return {}
    
def message_pin_v1(token, message_id):
    '''
    Given a message within a channel or DM, mark it as "pinned".

    HTTP METHOD: POST
    Parameters:{ token, message_id }
    Return Type:{}

    InputError when any of:      
        - message_id is not a valid message within a channel or DM that the authorised user has joined
        - the message is already pinned
      
      AccessError when:      
        - message_id refers to a valid message in a joined channel/DM and the authorised user does not have owner permissions in the channel/DM
    '''
    store = data_store.get()
    check_token_valid(token)
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)

    message = found_message_in_dm_or_channel_for_owner(message_id, auth_user_id)  

    if message['is_pinned'] == True:
        raise InputError(description="This message is already pinned")
    else:
        message['is_pinned'] = True

    data_store.set(store)
    return {}

def message_unpin_v1(token, message_id):
    '''
    Given a message within a channel or DM, remove its mark as pinned.

    HTTP METHOD: POST
    Parameters:{ token, message_id }
    Return Type:{}

    InputError when any of:      
        - message_id is not a valid message within a channel or DM that the authorised user has joined
        - the message is not already pinned
      
      AccessError when:      
        - message_id refers to a valid message in a joined channel/DM and the authorised user does not have owner permissions in the channel/DM
    '''
    store = data_store.get()
    check_token_valid(token)
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)
    
    message = found_message_in_dm_or_channel_for_owner(message_id, auth_user_id)        
    
    if message['is_pinned'] == False:
        raise InputError(description="This message is already unpinned")
   
    else:
        message['is_pinned'] = False

    data_store.set(store)
    return {}

def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    '''
    < A new message should be sent to the channel/DM identified by the channel_id/dm_id that contains the contents
    of both the original message and the optional message. The format does not matter as 
    long as both the original and optional message exist as a substring within the new message. 
    Once sent, this new message has no link to the original message, so if the original 
    message is edited/deleted, no change will occur for the new message >

    HTTP METHOD: POST
    Arguments:
        - token :: [str] - The user's token
        - og_message_id :: [int] - og_message_id is the ID of the original message
        - message :: [str] - message is the optional message in addition to the shared message, 
        and will be an empty string '' if no message is given.
        - channel_id :: [int] - channel_id is the channel that the message is being 
        shared to, and is -1 if it is being sent to a DM.
        - dm_id :: [int] - dm_id is the DM that the message is being shared to, and is -1 if it is being 
        sent to a channel.
    
    Exceptions:
        InputError when any of:      
            - both channel_id and dm_id are invalid
            - neither channel_id nor dm_id are -1        
            - og_message_id does not refer to a valid message within a channel/DM that the 
            authorised user has joined
            - length of message is more than 1000 characters
        AccessError when:      
            - the pair of channel_id and dm_id are valid (i.e. one is -1, the other is valid) and 
            the authorised user has not joined the channel or DM they are trying to share the message to
    Return Value: 
        { shared_message_id }
    
    '''  
    check_token_valid(token)
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)
  
    if len(message) > 1000:
        raise InputError(description='Error: Message is over 1000 characters')

    copy_message = ''
    found_message = found_message_in_dm_or_channel_for_mem(og_message_id, auth_user_id)
    copy_message = found_message['message']           

    #Update message to format seen on frontend
    send_message = message + '\n' + '"""' +'\n' + copy_message + '\n' +'"""'
    
    # Share to channel
    if channel_id != -1: 
        shared_message_id = message_send_v1(token, channel_id, send_message)
        return {'shared_message_id': shared_message_id}

    # Share to dm
    if dm_id != -1:
        shared_message_id = message_senddm_v1(token, dm_id, send_message)
        return {'share_message_id': shared_message_id}

def message_react_v1(token, message_id, react_id):
    '''
    <Given a message within a channel or DM the authorised user is 
    part of, add a "react" to that particular message>

    HTTP METHOD: POST
    Arguments:
        - token :: [str] - The user's token
        - message_id :: [int] - The message_id of the message
        - react_id :: [int] - The id of the react
    
    Exceptions:
        InputError when any of:      
            - message_id is not a valid message within a channel or DM that the authorised user has joined
            - react_id is not a valid react ID - currently, the only valid react ID the frontend has is 1
            - the message already contains a react with ID react_id from the authorised user
    Return Value:
        {}
    '''
    store = data_store.get()  
    check_token_valid(token)
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)

    if react_id != 1:
        raise InputError(description="Invalid react_id")

    message = found_message_in_dm_or_channel_for_mem(message_id, auth_user_id)
    
    for react in message['reacts']:
        if react['react_id'] == react_id:
            if react['is_this_user_reacted']:
                raise InputError(description="You have already reacted to this message")
            else:
                react['u_ids'].append(auth_user_id)
                react['is_this_user_reacted'] = True
    # store reaction in notifications
    store = data_store.get()
    dm_channel = dm_or_channel_2(message_id)
    # get the handle
    for user in store['users']:
        if user['auth_user_id'] == auth_user_id:
            user_handle = user['handle_str']
    # get the channel name/ dm name?????//
    name = dm_channel[0]   
    # create the notification     
    message1 = "%s reacted to your message in %s" % (user_handle, name)
    # store notification
    # check member is still a member of the dm/channel
    still_member = False
    for user in dm_channel[3]:
        if user['u_id'] == message['u_id']:
            still_member = True
    if still_member == False:
        data_store.set(store)
        return {}
    for user in store['users']:
        if user['auth_user_id'] == message['u_id']:
            if dm_channel[1]:
                note = {'channel_id': dm_channel[2], 'dm_id': -1, 'notification_message': message1}
            else:
                note = {'channel_id': -1, 'dm_id': dm_channel[2], 'notification_message': message1}
            user['notifications'].append(note)
    data_store.set(store)
    return {}


def message_unreact_v1(token, message_id, react_id):
    '''
    <Given a message within a channel or DM the authorised user is 
    part of, remove a "react" to that particular message>

    HTTP METHOD: POST
    Arguments:
        - token :: [str] - The user's token
        - message_id :: [int] - The message_id of the message
        - react_id :: [int] - The id of the react
    
    Exceptions:
        InputError when any of:      
            - message_id is not a valid message within a channel or DM that the authorised user has joined
            - react_id is not a valid react ID
            - the message does not contain a react with ID react_id from the authorised user
    Return Value:
        {}
    '''
    store = data_store.get()  
    check_token_valid(token)
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)
    
    if react_id != 1:
        raise InputError(description="Invalid react_id")

    message = found_message_in_dm_or_channel_for_mem(message_id, auth_user_id)
 
    for react in message['reacts']:
        if react['react_id'] == react_id:
            if not react['is_this_user_reacted']:
                raise InputError(description="You have not reacted to this message")
            else:
                react['u_ids'].remove(auth_user_id)
                react['is_this_user_reacted'] = False

    data_store.set(store)
    return {}
