from curses.ascii import isalnum
from src.data_store import initial_object, data_store

def check_tagging(sender_id, message_name, message, is_channel, id):
    '''
    contains tagging functions for message
    '''
    # get first 20 characters of the message
    start = message[0:20]    
    # get sender handle
    store = data_store.get()
    for user in store['users']:
        if user['auth_user_id'] == sender_id:
            sender = user['handle_str']
    names_tagged = find_tagged_users(sender, message)
    # if the message was sent in a channel:
    if is_channel == True: 
        for handle in names_tagged:
            # check the tagged person is a member of the channel
            for channel in store['channels']:
                for member in channel['all_members']:
                    id = handle_to_u_id(handle)
                    if member['u_id'] == id:
                        message = "%s tagged you in %s: %s" % (sender, message_name, start)
                        for user in store['users']:
                            if user['auth_user_id'] == id:
                                note = {'channel_id': id, 'dm_id': -1, 'notification_message': message}
                                user['notifications'].append(note)
    # if the message was sent in a dm:
    elif is_channel == False:
        for handle in names_tagged:
            # check the tagged user is part of the dm
            for dm in store['dms']:
                ## we get here
                for member in dm['all_members']:
                    id = handle_to_u_id(handle)
                    if member['u_id'] == id:
                        message = "%s tagged you in %s: %s" % (sender, message_name, start)
                        for user in store['users']:
                            if user['auth_user_id'] == id:
                                note = {'channel_id': -1, 'dm_id': id, 'notification_message': message}
                                user['notifications'].append(note)
    data_store.set(store)
    return

def handle_to_u_id(handle):
    '''
    returns auth_user_id given handle
    '''
    store = data_store.get()
    for user in store['users']:
        if user['handle_str'] == handle:
            return user['auth_user_id']

def find_tagged_users(sender, message):
    '''
    Finds which user has been tagged
    '''
    name_check = 0
    names_tagged = []
    name = []
    for char in message:
        # if @ is found and the next character is nonalphanumberic, add the name to names_tagged
        if name_check == 1 and not char.isalnum():
            name_check = 0
            x = "".join(name)
            # check for duplicates
            check = 0
            for n in names_tagged:
                if x == n:
                    check = 1
            # check tagged is not sender
            if check == 0 and x != sender:
                names_tagged.append(x)
            name = []
        # if @ is found and the next character is alphanumeria, append the character to the users name
        if name_check == 1 and char.isalnum():
            name.append(char)
        # if the character is @, set to found. 
        if char == '@':
            name_check = 1
    # is the tagged name was at the end of the message...
    if (name_check == 1):
        x = "".join(name)
        # check for duplicates
        check = 0
        for n in names_tagged:
            if x == n:
                check = 1
            # check tagged is not sender
        if check == 0 and x != sender:
            names_tagged.append(x)
    return names_tagged
    