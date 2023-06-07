from sqlite3 import Timestamp
from helpers.valid_user_helper import check_valid_auth_user_id, check_valid_u_id, find_user, decode_jwt, check_token_valid
from helpers.channel_helper import find_channel_id, find_channel_member, already_member, already_owner, find_channel_member_u_id
from helpers.membership_helper import owner_or_global_owner
from helpers.message_helper import messege_send_standup
from src.data_store import data_store
from src.error import InputError, AccessError
import datetime

def standup_start_v1(token, channel_id, length):
    '''
    For a given channel, start the standup period whereby for the next "length" seconds if someone calls "standup/send" with a message,
    it is buffered during the X second window then at the end of the X second window a message will be added to the 
    message queue in the channel from the user who started the standup. 
    "length" is an integer that denotes the number of seconds that the standup occurs for. 
    If no standup messages were sent during the duration of the standup, no message should be sent at the end.
    
    Arguments:
        token : token of user starting standup
        channel_id : channel id of channel where standup is being created
        length : number of seconds the standup is active for
        
    Exceptions:
        InputError: 
            channel_id does not refer to a valid channel
            length is a negative integer
            an active standup is currently running in the channel
      
        AccessError:
            channel_id is valid and the authorised user is not a member of the channel
    
    Return:
        time_finish : time when standup ends
    '''
    # checks if token is valid
    check_token_valid(token)
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)

    # checks if channel is valid
    channel = find_channel_id(channel_id)

    # checks if auth_user_id is a member of the channel
    find_channel_member(channel, auth_user_id)

    # checks if length is a negative integer
    if length < 0:
        raise InputError(description="Length is a negative integer.")

    # checks if standup that is active is already running
    # if len(channel['standup']) > 1:
        # checks if standup that is active is already running
    if channel['standup']['is_active'] == True:
        raise InputError(description= "An active standup is already running in the channel.")

    store = data_store.get()
    time_finish = datetime.datetime.now().timestamp() + length
    # for standup in channel['standup']:
    channel['standup'] = {
        'auth_user_id': auth_user_id,
        'is_active': True,
        'time_finish': time_finish,
        'message_queue': ''
    }

    data_store.set(store)   
  
    return {'time_finish': time_finish}


def standup_active_v1(token, channel_id):
    '''
    For a given channel, return whether a standup is active in it, and what time the standup finishes. If no standup is active, then time_finish returns None.

    Arguments:
        token : token of user retrieving standup status
        channel_id : channel id of channel where standup is being created

    Exceptions:
        InputError: 
            channel_id does not refer to a valid channel
      
        AccessError:
            channel_id is valid and the authorised user is not a member of the channel
    
    Return:
        is_active : whether a standup in the given channel is empty
        time_finish : time when standup ends
    '''
 
    # checks if token is valid
    check_token_valid(token)
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)

    # checks if channel is valid
    channel = find_channel_id(channel_id)

    # checks if auth_user_id is a member of the channel
    find_channel_member(channel, auth_user_id)

    time_now = datetime.datetime.now().timestamp()
    standup = channel['standup']

    if standup['time_finish'] < time_now:
        if standup['is_active'] == True:
            standup['is_active'] = False
            messege_send_standup(standup['auth_user_id'], channel_id, standup['message_queue'])
        return  {
            'is_active' : False, 
            'time_finish' : None
        }
    return {
        'is_active' : True, 
        'time_finish' : standup['time_finish']
        }

def standup_send_v1(token, channel_id, message):
    '''
    Sending a message to get buffered in the standup queue, assuming a standup is currently active. 
    Note: @ tags should not be parsed as proper tags when sending to standup/send
    
    Arguments:
        token (str)
        channel_id (int)
        message (dict)

    Exceptions:
        Input Errors:
            channel_id does not refer to a valid channel
            length of message is over 1000 characters
            an active standup is not currently running in the channel
        Access Errors:
            channel_id is valid and the authorised user is not a member of the channel      
    
    Return:
        {}
    '''
    # checks if token is valid
    check_token_valid(token)
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)
    user = find_user(auth_user_id)
    username = user['handle_str']

    # checks if channel is valid
    channel = find_channel_id(channel_id)

    # checks if auth_user_id is a member of the channel
    find_channel_member(channel, auth_user_id)

    # checks if length of message is greater than 1000 characters
    if len(message) > 1000:
        raise InputError(description= "Error: Length of message is over 1000 characters.")

    # if len(channel['standup']) > 1:
    # checks if standup that is active is already running
    if channel['standup']['is_active'] == False:
        raise InputError(description= "An active standup is not running in the channel.")

    # create message and append it to the msg queue
    if channel['standup']['time_finish'] - datetime.datetime.utcnow().timestamp() > 0:
        channel = find_channel_id(channel_id)
        user = find_user(auth_user_id)
        channel["standup"]["message_queue"] += username + ":" + message + '\n'

    return {}
