from src.data_store import data_store
from src.error import InputError, AccessError
from helpers.other_helper import email_to_auth_id
from helpers.valid_user_helper import check_valid_auth_user_id, check_valid_u_id, find_user, decode_jwt, check_token_valid
from helpers.dm_helper import find_dm_id, find_dm_member, find_dm_owner, create_sendlaterdm, auth_user_in_dm
from helpers.channel_helper import find_channel_id, find_channel_member
from helpers.message_helper import check_message_len, create_sendlater_message
from helpers.notifications_helper import check_tagging
from helpers.user_stat_helper import update_dm_num_workspace_stats, update_messages_workspace_stats
import jwt
import json
import time
import datetime
from datetime import timezone

def dm_create_v1(token, u_ids):
    '''
    u_ids contains the user(s) that this DM is directed to, and will not include 
    the creator. The creator is the owner of the DM. name should be automatically 
    generated based on the users that are in this DM. The name should be an 
    alphabetically-sorted, comma-and-space-separated list of user handles, 
    e.g. 'ahandle1, bhandle2, chandle3'.
    
    HTTP METHOD: POST
    Parameters:{ token, u_ids }
    Return Type:{ dm_id }
    
    InputError when any of:    
        - any u_id in u_ids does not refer to a valid user
        - there are duplicate 'u_id's in u_ids
    '''
    store = data_store.get()
    check_token_valid(token)
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)
    
    # Check if user is valid
    for u_id in u_ids:
        check_valid_u_id(u_id) 
                
    # If user ids valid, store details of owner
    user = find_user(auth_user_id)   
    user_details = {
        'u_id' : user['auth_user_id'],
        'email' : user['email'],
        'name_first' : user['name_first'],
        'name_last' : user['name_last'],
        'handle_str' : user['handle_str'],
        'password' : user['password']
    }
    
    # Store handles of members
    dm_name_list = []
    dm_name_list.append(user_details['handle_str'])
    
    for u_id in u_ids:
        user = find_user(u_id)  
        dm_name_list.append(user['handle_str'])
        
    sorted_dm_name_list = sorted(dm_name_list, key=str.lower)
    dm_num = len(store['dms']) + 1
    dm_name = ', '.join(sorted_dm_name_list)
    
    members = []
    members.append(user_details)
    new_dm = {
                'dm_id' : dm_num,
                'name' : dm_name,
                'owner_members' : [],
                'all_members' : [],
                'messages': [],
    }

    # add owner to owner_members and all_members
    user = find_user(auth_user_id)  
    new_dm['owner_members'].append({
        'u_id': auth_user_id,
        'email': user['email'],
        'name_first': user['name_first'],
        'name_last': user['name_last'],
        'handle_str': user['handle_str']                
    })
    new_dm['all_members'].append({
        'u_id': auth_user_id,
        'email': user['email'],
        'name_first': user['name_first'],
        'name_last': user['name_last'],
        'handle_str': user['handle_str']
    })
        
    #append all u_ids in dm members
    for u_id in u_ids:
        user = find_user(u_id)
        new_dm['all_members'].append({
            'u_id': u_id,
            'email': user['email'],
            'name_first': user['name_first'],
            'name_last': user['name_last'],
            'handle_str': user['handle_str']
        })

    store['dms'].append(new_dm)
    
    # ADD NOTIFICATION FOR U_IDS
    # get handle
    for user in store['users']:
        if user['auth_user_id'] == auth_user_id:
            user_handle = user['handle_str']
    # create notification
    message = "%s added you to %s" % (user_handle, dm_name)
    # store notification
    for user in store['users']:
        for u_id in u_ids:
            if user['auth_user_id'] == u_id:
                note = {'channel_id': -1, 'dm_id': dm_num, 'notification_message':message}
                user['notifications'].append(note)

    for member in new_dm['all_members']:
        member_email = member['email']
        auth_id = email_to_auth_id(member_email)
        user = find_user(auth_id)
        user['user_stats']["dms_joined"].append({
        "num_dms_joined" : user["user_stats"]["dms_joined"][-1]["num_dms_joined"] + 1,
        "time_stamp" : int(time.time())
        })
    data_store.set(store)
    update_dm_num_workspace_stats(True)

    return {'dm_id': dm_num}        

    
def dm_list_v1(token):
    '''
    Returns the list of DMs that the user is a member of.
    
    HTTP METHOD: GET
    Parameters:{ token }
    Return Type:{ dms }
    '''
    store = data_store.get()
    check_token_valid(token)
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)

    dm_list = []

    for dm in store['dms']:
        found_dm = find_dm_member(dm, auth_user_id)
        dm_list.append({
            'dm_id': found_dm['dm_id'],
            'name': found_dm['name']
        })
    data_store.set(store)
    return {"dms": dm_list}
    
def dm_remove_v1(token, dm_id):
    '''
    Remove an existing DM, so all members are no longer in the DM. 
    This can only be done by the original creator of the DM.
    
    HTTP METHOD: DELETE
    Parameters:{ token, dm_id }
    Return Type:{}
    
    AccessError when:
        - dm_id is valid and the authorised user is not the original DM creator
        - dm_id is valid and the authorised user is no longer in the DM
    '''
    store = data_store.get()  
    check_token_valid(token) 
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)

    dm = find_dm_id(dm_id)
    found_dm = find_dm_owner(dm, auth_user_id)
    store['dms'].remove(found_dm)
    
    for member in dm['all_members']:
        member_email = member['email']
        auth_id = email_to_auth_id(member_email)
        user = find_user(auth_id)
        user['user_stats']["dms_joined"].append({
        "num_dms_joined" : user["user_stats"]["dms_joined"][-1]["num_dms_joined"] - 1,
        "time_stamp" : int(time.time())
    })
    update_dm_num_workspace_stats(False)
    data_store.set(store)
    return {}
 
def dm_details_v1(token, dm_id):
    '''
    Given a DM with ID dm_id that the authorised user is a member of, provide 
    basic details about the DM.
    
    HTTP METHOD: GET
    Parameters:{ token, dm_id }
    Return Type:{ name, members }
    
    InputError when:      
        - dm_id does not refer to a valid DM
      
    AccessError when:      
        - dm_id is valid and the authorised user is not a member of the DM
    '''
    store = data_store.get()    
    check_token_valid(token)
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)

    dm = find_dm_id(dm_id)
    find_dm_member(dm, auth_user_id)

    dm_details = {}         
    dm_details['name'] = dm['name']

    # Check the all_members section of each channel.
    dm_details['all_members'] = []
    for member in dm['all_members']:
        dm_details['all_members'].append({
            'u_id': member['u_id'],
            'email': member['email'],
            'name_first': member['name_first'],
            'name_last': member['name_last'],       
            'handle_str': member['handle_str'],            
        }) 
    data_store.set(store)              
    return dm_details
            
def dm_leave_v1(token, dm_id):
    '''
    Given a DM ID, the user is removed as a member of this DM. The creator is allowed to 
    leave and the DM will still exist if this happens. This does not update the name of 
    the DM.
    
    HTTP METHOD: POST
    Parameters:{ token, dm_id }
    Return Type:{}
    
    InputError when:      
        - dm_id does not refer to a valid DM
      
    AccessError when:
        - dm_id is valid and the authorised user is not a member of the DM
    '''
    store = data_store.get()
    check_token_valid(token)
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)
    user = find_user(auth_user_id)            
    dm = find_dm_id(dm_id)
    find_dm_member(dm, auth_user_id)

    for member in dm['all_members']:
        if member['u_id'] == auth_user_id:                   
            dm['all_members'].remove(member)

    for members in dm['owner_members']:
        if members['u_id'] == auth_user_id:
            dm['owner_members'].remove(members)
            
    user["user_stats"]["dms_joined"].append({
        "num_dms_joined" : user["user_stats"]["dms_joined"][-1]["num_dms_joined"] - 1,
        "time_stamp" : int(time.time())
    })
    data_store.set(store) 

    data_store.set(store)                   
    return {}

def message_senddm_v1(token, dm_id, message):
    '''
    Send a message from authorised_user to the DM specified by dm_id. 
    Note: Each message should have it's own unique ID, 
    i.e. no messages should share an ID with another message, even if that other message is in a different channel or DM.

    HTTP METHOD: POST
        
    Parameters:{ token, dm_id, message }
    Return Type:{ message_id }

    InputError when any of:
        - dm_id does not refer to a valid DM
        - length of message is less than 1 or over 1000 characters
    AccessError when:
        - dm_id is valid and the authorised user is not a member of the DM
    '''
    store = data_store.get()
    check_token_valid(token)
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)

    check_message_len(message)

    store['message_num'] += 1
    message_id = store['message_num']

    dm = find_dm_id(dm_id)
    find_dm_member(dm, auth_user_id)

    new_message = {
        'message_id': message_id,
        'u_id': auth_user_id,
        'message': message,
        'time_sent': datetime.datetime.now().timestamp(),
        'reacts': [],
        'is_pinned': False
    }         
    new_message['reacts'].append({
        'react_id': 1,
        'u_ids': [],
        'is_this_user_reacted': False
    })

    dm['messages'].append(new_message)
    # check message for tags
    for dm in store['dms']:        
        if dm['dm_id'] == dm_id:
            dm_name = dm['name']
    check_tagging(auth_user_id, dm_name, message, False, dm_id)
    user = find_user(auth_user_id)
    
    user["user_stats"]["messages_sent"].append({
        "num_messages_sent" : user["user_stats"]["messages_sent"][-1]["num_messages_sent"] + 1,
        "time_stamp" : int(time.time())
    })
    update_messages_workspace_stats(True)
    update_dm_num_workspace_stats(True)
    data_store.set(store)                      
    return {'message_id': message_id}

def dm_messages_v1(token, dm_id, start):
    '''
    Given a DM with ID dm_id that the authorised user is a member of, 
    return up to 50 messages between index "start" and "start + 50". 
    Message with index 0 is the most recent message in the DM. This 
    function returns a new index "end" which is the value of "start + 50",
    or, if this function has returned the least recent messages in the 
    DM, returns -1 in "end" to indicate there are no more messages to load 
    after this return.

    HTTP METHOD: GET

    Parameters:{ token, dm_id, start }
    Return Type:{ messages, start, end }

    InputError when any of:      
        - dm_id does not refer to a valid DM
        - start is greater than the total number of messages in the channel
      
      AccessError when:      
        - dm_id is valid and the authorised user is not a member of the DM
    '''
    check_token_valid(token)
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)

    dm = find_dm_id(dm_id)
    find_dm_member(dm, auth_user_id)
    messages = dm['messages']
    
    if start > len(messages) or start < 0:
        raise InputError(description='Error: Invalid Start Value')

    end = start
    output = []
    while end < 50 and end < len(messages):
        output.append(messages[::-end-1])
        end += 1
    if end < 50:
        end = -1
    return {
        'messages': output,
        'start': start,
        'end': end,
    }

def  message_sendlaterdm_v1(token, dm_id, message, time_sent):
    '''
    Send a message from the authorised user to the DM specified 
    by dm_id automatically at a specified time in the future. The 
    returned message_id will only be considered valid for other 
    actions (editing/deleting/reacting/etc) once it has been sent 
    (i.e. after time_sent). If the DM is removed before the message 
    has sent, the message will not be sent. You do not need to consider 
    cases where a user's token is invalidated or a user leaves before 
    the message is scheduled to be sent.

    HTTP METHOD: POST
    Parameters:{ token, dm_id, message, time_sent }
    Return Type:{ message_id }

    InputError when any of:      
        - dm_id does not refer to a valid DM
        - length of message is less than 1 or over 1000 characters
        - time_sent is a time in the past
      
      AccessError when:      
        - dm_id is valid and the authorised user is not a member of the DM they are trying to post to
    '''
    # check valid token
    check_token_valid(token)
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    # check valid auth_user_id
    user = find_user(auth_user_id)
    check_valid_auth_user_id(auth_user_id)

    # check valid dm_id
    dm = find_dm_id(dm_id)
    # check valid message length
    check_message_len(message)
    # check token is member of dm
    find_dm_member(dm, auth_user_id)
    # check if time sent is in the past
    if int(time_sent) < int(datetime.datetime.now().timestamp()): 
        raise InputError(description="Error: scheduled time is in the past")

    wait_time = time_sent - datetime.datetime.now().timestamp() 
    time.sleep(wait_time)    
    message_id = create_sendlaterdm(auth_user_id, dm_id, message)
    user["user_stats"]["messages_sent"].append({
        "num_messages_sent" : user["user_stats"]["messages_sent"][-1]["num_messages_sent"] + 1,
        "time_stamp" : int(time.time())
    })
    update_messages_workspace_stats(True)
    return {'message_id': message_id}
    
def message_sendlater_v1(token, channel_id, message, time_sent):
    check_token_valid(token)
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)
    user = find_user(auth_user_id)
    # check valid channel_id
    channel = find_channel_id(channel_id)
    # check valid message length
    check_message_len(message)
    # check token is member of channel
    find_channel_member(channel, auth_user_id)
    # check if time sent is in the past
    if int(time_sent) < int(datetime.datetime.now().timestamp()): 
        raise InputError(description="Error: scheduled time is in the past")

    wait_time = time_sent - datetime.datetime.now().timestamp() 
    time.sleep(wait_time)    
    message_id = create_sendlater_message(auth_user_id, channel_id, message)
    user["user_stats"]["messages_sent"].append({
        "num_messages_sent" : user["user_stats"]["messages_sent"][-1]["num_messages_sent"] + 1,
        "time_stamp" : int(time.time())
    })
    update_messages_workspace_stats(True)
    return {'message_id': message_id}
