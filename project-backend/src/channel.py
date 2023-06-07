'''
Implementation for:
    - channel_invite_v2
    - channel_details_v2
    - channel_messages_v2
    - channel_join_v2
    - channel_leave_v1
    - channel_addowner_v1
    - channel_removeowner_v1
'''
from helpers.valid_user_helper import check_valid_auth_user_id, check_valid_u_id, find_user, decode_jwt, check_token_valid
from helpers.channel_helper import find_channel_id, find_channel_member, find_channel_owner_u_id, find_channel_member_u_id, already_member, already_owner
from helpers.membership_helper import check_global_owner, owner_or_global_owner, member_or_global_owner
from src.data_store import data_store
from src.error import InputError, AccessError
from time import time
#-----------------------------------------------------------------------------
def channel_invite_v2(token, channel_id, u_id):
    '''
    <Invites a user with ID u_id to join a channel with ID channel_id. 
    Once invited, the user is added to the channel immediately. 
    In both public and private channels, all members are able to invite users>
    Arguments:
        - token :: [str] - The user's token
        - channel_id :: [int] - The channel_id of the channel, user is invited to
        - u_id :: [int] - The user being invited to the channel    
    Exceptions:
        InputError - Occurs when:      
            - channel_id does not refer to a valid channel
            - u_id does not refer to a valid user
            - u_id refers to a user who is already a member of the channel
        AccessError - Occurs when:     
            - channel_id is valid and the authorised user is not a member of the channel
    Return Value:
        {}
    '''
    check_token_valid(token)
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)
    check_valid_u_id(u_id)

    channel = find_channel_id(channel_id)
    member_or_global_owner(channel, auth_user_id) 
    already_member(channel, u_id)    
        
    user = find_user(u_id)
    channel['all_members'].append(
        {
            'u_id': u_id, 
            'name_first': user['name_first'], 
            'name_last': user['name_last']
        }
    )
    # ADD TO NOTIFICATIONS
    store = data_store.get()
    # get the handle
    for user in store['users']:
        if user['auth_user_id'] == auth_user_id:
            user_handle = user['handle_str']
    # get the channel name
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            name = channel['name']   
    # create the notification     
    message = "%s added you to %s" % (user_handle, name)
    # store notification
    for user in store['users']:
        if user['auth_user_id'] == u_id:
            note = {'channel_id': channel_id, 'dm_id': -1, 'notification_message': message}
            user['notifications'].append(note)
            
    user["user_stats"]["channels_joined"].append({
        "num_channels_joined" : user["user_stats"]["channels_joined"][-1]["num_channels_joined"] + 1,
        "time_stamp" : int(time())
    })
    data_store.set(store)

    return {}
#-----------------------------------------------------------------------------
def channel_details_v2(token, channel_id):
    '''
    <Given a channel with ID channel_id that the authorised user is a member of, 
    provide basic details about the channel>
    Arguments:
        - token :: [str] - The user's token
        - channel_id :: [int] - The channel_id of the channel
    Exceptions:    
        InputError - Occurs when:      
            - channel_id does not refer to a valid channel
        AccessError - Occurs when:      
            - channel_id is valid and the authorised user is not a member of the channel
    Return Value:
        { name, is_public, owner_members, all_members }
    '''
    check_token_valid(token)
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)
    
    channel = find_channel_id(channel_id)
    find_channel_member(channel, auth_user_id)  
             
    return {
        'name': channel['name'],
        'is_public': channel['is_public'], 
        'owner_members': channel['owner_members'],
        'all_members': channel['all_members']
    }
#-----------------------------------------------------------------------------
def channel_messages_v2(token, channel_id, start):
    '''
    <Given a channel with ID channel_id that the authorised user is a member of, return up to 
    50 messages between index "start" and "start + 50". Message with index 0 is the most 
    recent message in the channel. This function returns a new index "end" which is the value
    of "start + 50", or, if this function has returned the least recent messages in the channel, 
    returns -1 in "end" to indicate there are no more messages to load after this return>
    Arguments:
        - token :: [str] - The user's token
        - channel_id :: [int] - The channel_id of the channel
        - start :: [int] - The start of messages
    Exceptions:
        InputError - Occurs when:      
            - channel_id does not refer to a valid channel
            - start greater than total number of messages in channel
        AccessError - Occurs when:      
            - channel_id is valid and the authorised user is not a member of the channel
    Return Value:
        { messages, start, end }
    '''
    store = data_store.get()
    check_token_valid(token)
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)
    
    channel = find_channel_id(channel_id)
    member_or_global_owner(channel, auth_user_id)
    num_messages = len(list(channel['messages']))

    # if there are no messages and start is 0
    if num_messages == 0 and start == 0:
        return {
            'messages': [],
            'start': start,
            'end': -1
        }

    # if start is greater than number of messages
    if start > num_messages:
        raise InputError(description='Error: Start is larger than number of messages')

    end_messages = start + 50
    iterator = 0
    msgs = []

    while iterator < 50:
        index = start + iterator
        if index >= end_messages or index >= num_messages:
            break

        # new message 
        channel = find_channel_id(channel_id)
        for message in channel['messages']:
            new_message= {
                'message_id': message['message_id'],
                'u_id': message['u_id'],
                'message': message['message'],
                'time_sent': message['time_sent'''],
                'reacts': [],
                'is_pinned': False
            }
        
        # append the new message
        msgs.append(new_message)
        iterator = iterator + 1

        if iterator < 50:
            end_messages = -1
        
        data_store.set(store)
        
    # return messages, start and end values
    return {
        'messages': msgs,
        'start': start,
        'end': end_messages,
    }
#-----------------------------------------------------------------------------
def channel_join_v2(token, channel_id):
    '''
    <Given a channel_id of a channel that the authorised user can join, adds 
    them to that channel>
    Arguments:
        - token :: [str] - The user's token
        - channel_id :: [int] - The channel_id of the channel, user is joining
    Exceptions:
        InputError - Occurs when:      
            - channel_id does not refer to a valid channel
            - authorised user is already a member of the channel
        AccessError - Occurs when:      
            - channel_id refers to channel that is private and the authorised user is not a member of the channel and not a global owner
    Return Value: 
        {}
    '''
    store = data_store.get()
    check_token_valid(token)
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)
    
    channel = find_channel_id(channel_id)
    already_member(channel, auth_user_id)
    
    person = {}
    user = find_user(auth_user_id)
    person = {
        'u_id': user['auth_user_id'],
        'email': user['email'],
        'name_first': user['name_first'],
        'name_last': user['name_last'],
        'handle_str': user['handle_str']
    }    
        
    if channel['is_public'] == True or check_global_owner(auth_user_id) == True:
        channel['all_members'].append(person)
    else:
        raise AccessError(description='Error: Channel is private')  
    
    user["user_stats"]["channels_joined"].append({
        "num_channels_joined" : user["user_stats"]["channels_joined"][-1]["num_channels_joined"] + 1,
        "time_stamp" : int(time())
    })
    data_store.set(store)

    return {}
#-----------------------------------------------------------------------------
def channel_leave_v1(token, channel_id):
    '''
    <Given a channel with ID channel_id that the authorised user is a member of, 
    remove them as a member of the channel. Their messages should remain in the 
    channel. If the only channel owner leaves, the channel will remain>
    Arguments:
        - token :: [str] - The user's token
        - channel_id :: [int] - The channel_id of the channel
    Exceptions:
        InputError - Occurs when:      
            - channel_id does not refer to a valid channel
            - the authorised user is the starter of an active standup in the channel
        AccessError - Occurs when:      
        - channel_id is valid and the authorised user is not a member of the channel
    Return Value:
        {}
    '''
    store = data_store.get()
    check_token_valid(token)
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)

    channel = find_channel_id(channel_id)
    find_channel_member(channel, auth_user_id)

    user = find_user(auth_user_id)
    channel['all_members'].remove(
        {
            'u_id': auth_user_id, 
            'name_first': user['name_first'], 
            'name_last': user['name_last']
        }
    )
    user["user_stats"]["channels_joined"].append({
        "num_channels_joined" : user["user_stats"]["channels_joined"][-1]["num_channels_joined"] - 1,
        "time_stamp" : int(time())
    })
    data_store.set(store)
    return {}
#-----------------------------------------------------------------------------    
def channel_addowner_v1(token, channel_id, u_id):
    '''
    <Make user with user_id u_id an owner of the channel> 
    Arguments:
        - token :: [str] - The user's token
        - channel_id :: [int] - The channel_id of the channel, user is invited to
        - u_id :: [int] - The user becoming channel owner
    Exceptions:
        InputError - Occurs when:      
            - channel_id does not refer to a valid channel
            - u_id does not refer to a valid user
            - u_id refers to a user who is not a member of the channel
            - u_id refers to a user who is already an owner of the channel
        AccessError - Occurs when:      
            - channel_id is valid and the authorised user does not have owner permissions in the channel
    Return Value:
        {}
    '''
    check_token_valid(token)
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)
    user = find_user(u_id)
    check_valid_u_id(u_id)

    channel = find_channel_id(channel_id)

    # checks both auth_user_id and u_id are members of the channel
    find_channel_member(channel, auth_user_id)
    find_channel_member_u_id(channel, u_id)

    # check if inviter has owner permissions
    owner_or_global_owner(channel, auth_user_id)
    # u_id is already owner   
    already_owner(channel, u_id)

    channel['owner_members'].append(
        {
            'u_id': u_id, 
            'name_first': user['name_first'], 
            'name_last': user['name_last']
        }
    )    
    return {}
#-----------------------------------------------------------------------------
def channel_removeowner_v1(token, channel_id, u_id):
    '''
    <Remove user with user_id u_id owner permissions of the channel> 
     Arguments:
        - token :: [str] - The user's token
        - channel_id :: [int] - The channel_id of the channel, user is invited to
        - u_id :: [int] - The user losing owner permissions
    Exceptions:
        InputError - Occurs when:
            - channel_id does not refer to a valid channel
            - u_id does not refer to a valid user
            - u_id refers to a user who is not an owner of the channel
            - u_id refers to a user who is currently the only owner of the channel
        AccessError - Occurs when:
            - channel_id is valid and the authorised user does not have owner permissions in the channel
    Return Value:
        {}
    '''
    check_token_valid(token)
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)
    check_valid_u_id(u_id)

    channel = find_channel_id(channel_id)

    # check if inviter has owner permissions
    owner_or_global_owner(channel, auth_user_id)

    # checks u_id are members of the channel
    find_channel_member_u_id(channel, u_id)

    # u_id is not a owner
    find_channel_owner_u_id(channel, u_id)
            
    # check if user u_id is the only owner of the channel
    if len(channel['owner_members']) == 1:
        raise InputError('Error: User is currently the only owner of the channel')

    user = find_user(u_id)
    channel['owner_members'].remove(
        {
            'u_id': u_id, 
            'name_first': user['name_first'], 
            'name_last': user['name_last']
        }
    )
    return {}
#-----------------------------------------------------------------------------
