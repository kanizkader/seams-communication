from src.data_store import data_store
from helpers.user_stat_helper import auth_id_to_user
from src.error import AccessError, InputError

def find_channel_id(channel_id):
    ''' 
    finds the valid channel id
    '''
    store = data_store.get()
    valid_channels = store['channels']
    for channel in valid_channels:
        if channel['channel_id'] == channel_id:
            return channel
    raise InputError(description='Error: Invalid Channel ID')

def find_channel_owner_u_id(channel, u_id):
    '''
    Find the u_id of the channel owner
    '''
    store = data_store.get()
    for channels in store['channels']:
        if channels['channel_id'] == channel['channel_id']:
            for member in channels['owner_members']:
                if member['u_id'] == u_id:
                    return member
    raise InputError(description='Error: User is not owner of the channel')

def find_channel_member(channel, auth_user_id):
    '''
    Check if user is a member of the channel
    '''
    store = data_store.get()
    for channels in store['channels']:
        if channels['channel_id'] == channel['channel_id']:
            for member in channels['all_members']:
                if member['u_id'] == auth_user_id:
                    return member
    raise AccessError(description='Error: User is not a member of the channel') 

def find_channel_member_u_id(channel, u_id):
    '''
    Find the channel member u_id
    '''
    store = data_store.get()
    for channels in store['channels']:
        if channels['channel_id'] == channel['channel_id']:
            for member in channels['all_members']:
                if member['u_id'] == u_id:
                    return member
    raise InputError(description='Error: User is not a member of the channel') 

def already_member(channel, u_id):
    '''
    Check if the user is already a member of the channel
    '''
    store = data_store.get()
    for channels in store['channels']:
        if channels['channel_id'] == channel['channel_id']:
            for member in channels['all_members']:
                if member['u_id'] == u_id:
                    raise InputError(description="Error: User is already a member of the channel")

def already_owner(channel, u_id):
    '''
    Check if user is already a channel owner
    '''
    store = data_store.get()
    for channels in store['channels']:
        if channels['channel_id'] == channel['channel_id']:
            for member in channels['owner_members']:
                if member['u_id'] == u_id:
                    raise InputError('Error: User is already an owner of the channel')

def channel_id_to_channel(channel_id):
    store = data_store.get()
    for channel in store["channels"]:
        if channel['channel_id'] == channel_id:
            return channel
    raise InputError

def get_num_channels():
    '''
    retrieve number of channels stored
    '''
    store = data_store.get()
    return len(store['channels'])

def auth_user_in_channel(auth_user_id, channel_id):
    '''
    Find whether user is in channel members or owners.
    Return Boolean Value.
    '''
    user = auth_id_to_user(auth_user_id)
    channel = channel_id_to_channel(channel_id)
    if user in channel["all_members"] or user in channel["owner_members"]:
        return True
    return False
