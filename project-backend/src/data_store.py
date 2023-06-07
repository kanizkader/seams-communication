'''
data_store.py

This contains a definition for a Datastore class which you should use to store your data.
You don't need to understand how it works at this point, just how to use it :)

The data_store variable is global, meaning that so long as you import it into any
python file in src, you can access its contents.

Example usage: 

    from data_store import data_store

    store = data_store.get()
    print(store) # Prints { 'names': ['Nick', 'Emily', 'Hayden', 'Rob'] }

    names = store['names']

    names.remove('Rob')
    names.append('Jake')
    names.sort()

    print(store) # Prints { 'names': ['Emily', 'Hayden', 'Jake', 'Nick'] }
    data_store.set(store)
'''

## YOU SHOULD MODIFY THIS OBJECT BELOW
initial_object = {
    'users': [
        #{
            # auth_user_id
            # email
            # password
            # name_first
            # name_last
            # handle_str
            # session_id
            # perm_id
        #}
    ],
    'channels': [
         #{
            # name
            # channel_id
            # is_public: bool
            # owner_members: [
                # {
                    # u_id
                    # name_first
                    # name_last
                # }
            # ]
            # all_members: [
                # {
                    # u_id
                    # name_first
                    # name_last
                # }
            # ]
            # 'messages': [
                #  {
                    # 'message_id':
                    # 'u_id'
                    # 'message'
                    # 'time created'
                    # 'reacts': [
                    #     {
                            #'react_id' : 1,
                            #'u_ids': [list of reacted u_id]
                            #'is_this_user_reacted': Bool
                    #     }
                    # ]
                    # 'is_pinned'
                
                #  },
            # ]
            # "standup": [
                # {
                    # 'is_active': False,
                    # 'time_finish': 0,
                    # 'message': '',
                # }
            # ]   

       # },

    ],
    'dms' : [
        # "dm_id": 
        # "name" : 
        # "owner_members": [
            # 'u_id': 
            # 'email': 
            # 'name_first': 
            # 'name_last': 
            # 'handle_str':            
        #]    
        # "all_members": [
            # 'u_id': 
            # 'email': 
            # 'name_first': 
            # 'name_last': 
            # 'handle_str':
        #]
        # "messages": [
            # 'message_id'
            # 'u_id'
            # 'message'
            # 'is_pinned'
            # 'reacts': [
            #   {
                    #'react_id' : 1,
                    #'u_ids': [list of reacted u_id]
                    #'is_this_user_reacted': Bool
            #   }
            # ]
        # ]
        # "dm_list": [
            # "dm_id":
            # "name":
        # ]
        # "dm_details": [
            # "dm_name"
            # "members"
        # ]
    ],
    'removed_users': [],
    'message_num': 0,
    'workspace_stats': {
        'channels_exist': [],
        'dms_exist': [],
        'messages_exist': [], 
        'utilization_rate': 0
    },
    'total_users' : 0
}
## YOU SHOULD MODIFY THIS OBJECT ABOVE

## YOU ARE ALLOWED TO CHANGE THE BELOW IF YOU WISH
class Datastore:
    def __init__(self):
        self.__store = initial_object

    def get(self):
        return self.__store

    def set(self, store):
        if not isinstance(store, dict):
            raise TypeError('store must be of type dictionary')
        self.__store = store

print('Loading Datastore...')

global data_store
data_store = Datastore()


