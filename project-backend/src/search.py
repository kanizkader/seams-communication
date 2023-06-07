from src.error import InputError, AccessError
from src.error import InputError, AccessError
from helpers.valid_user_helper import check_valid_auth_user_id, decode_jwt, find_user, check_token_valid
from helpers.channel_helper import get_num_channels
from helpers.message_helper import check_message_len
from src.data_store import data_store

def search_v1(token, query_str):
    '''
    Given a query string, return a collection of messages in all of the channels/DMs that the user has joined that contain the query (case-insensitive). 
    There is no expected order for these messages.

    Arguments:
        token : token of user starting standup
        query_str : search query input by valid user
        
    Exceptions:
        InputError: 
            length of query_str is greater than 1000 or lesser than 1

    Return:
        messages : collection of messages that contain the query, in no particular order 
    '''
    check_token_valid(token)
    token_data = decode_jwt(token)
    auth_user_id = token_data['auth_user_id']
    check_valid_auth_user_id(auth_user_id)
    check_message_len(query_str)

    msg_list = []

    # checks if query is a substring of channel
    store = data_store.get()
    for channel in store['channels']:
        for message in channel['messages']:
            if query_str.lower() in message['message'].lower():
                if auth_user_id in channel['all_members']:
                    msg_list.append(message)

    for dm in store['dms']:
        for message in dm['messages']:
            if query_str.lower() in dm['message'].lower():
                if auth_user_id in channel['all_members']:
                    msg_list.append(message)

    return {
        'messages': msg_list
    }
