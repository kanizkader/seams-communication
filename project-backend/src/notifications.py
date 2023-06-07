'''
Module for notifications
'''
from src.error import InputError, AccessError
from helpers.valid_user_helper import check_valid_auth_user_id, decode_jwt, find_user, check_token_valid
from helpers.channel_helper import get_num_channels
from src.data_store import data_store

# WHEN WHOULD A NOTIFICATION BE RAISED?????
def notifications_get_v1(token):
    '''
    Return the user's most recent 20 notifications, ordered from most recent to least recent.
    GET
    Parameters:{ token }
    Return Type:{ notifications }
    '''
    '''
    notifications = 
        List of dictionaries, where each dictionary contains types 
        { channel_id, dm_id, notification_message } 
        where channel_id is the id of the channel that the event happened in, 
        and is -1 if it is being sent to a DM. dm_id is the DM that the event happened in, 
        and is -1 if it is being sent to a channel. 
        Notification_message is a string of the following format for each trigger action:
      
        - tagged: "{User’s handle} tagged you in {channel/DM name}: {first 20 characters of the message}"
        - reacted message: "{User’s handle} reacted to your message in {channel/DM name}"
        - added to a channel/DM: "{User’s handle} added you to {channel/DM name}"
    '''
    # message send dm +channel invite should save to data store

    # check vaild token

    # determine which user we need notifications for 

    # Get the most recent 20 notifications from them and atatch to a notifications

    store = data_store.get()
    check_token_valid(token)
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)
    for user in store['users']:
        if user['auth_user_id'] == auth_user_id:
            notifications_list = user['notifications']          
    notifications_list.reverse()         
    notifications_list = notifications_list[0:20]       
    return {'notifications': notifications_list}


