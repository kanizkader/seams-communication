#from src.data_store import initial_object
from src.data_store import data_store
from time import time
from src.error import AccessError
from helpers.other_helper import get_auth_id

def update_total_users_num_workspace_stats():
    '''
    Updates the total number of users
    '''
    store = data_store.get()
    stats = store["workspace_stats"]
    
    if store["total_users"] == 0:
        store["total_users"] = 1
        stats["channels_exist"].append({
            "num_channels_exist": 0,
            "time_stamp": int(time())
        })
        stats["dms_exist"].append({
            "num_dms_exist": 0,
            "time_stamp": int(time())
        })
        stats["messages_exist"].append({
            "num_messages_exist": 0,
            "time_stamp": int(time())
        })
        stats["utilization_rate"] = 0
    else:
        store["total_users"] += 1
        
    data_store.set(store)
 
def update_channel_num_workspace_stats():
    '''
    Updates stats when a new channel is created 
    '''
    store = data_store.get()
    stats = store["workspace_stats"]
    
    new_num = stats["channels_exist"][-1]["num_channels_exist"] + 1
    stats["channels_exist"].append({
        "num_channels_exist": new_num,
        "time_stamp": int(time())
    })
    
    data_store.set(store)
 
def update_dm_num_workspace_stats(sent):
    '''
    Updates stats when a new dm is added or removed 
    '''
    store = data_store.get()
    stats = store["workspace_stats"]
    dm_num = stats["dms_exist"][-1]["num_dms_exist"]
    
    if sent:
        dm_num += 1
    else:
        dm_num -= 1
        
    stats["dms_exist"].append({
        "num_dms_exist": dm_num,
        "time_stamp": int(time())
    })
    data_store.set(store)
  
def update_messages_workspace_stats(sent):
    '''
    Updates stats when a message is sent or removed 
    '''
    store = data_store.get()
    stats = store["workspace_stats"]
    msg_num = stats["messages_exist"][-1]["num_messages_exist"]
    
    if sent:
        msg_num += 1
    else:
        msg_num -= 1

    stats["messages_exist"].append({
        "num_messages_exist": msg_num,
        "time_stamp": int(time())
    })
    data_store.set(store)   

def auth_id_to_user(auth_user_id):
    '''
    Returns user given auth_user_id
    '''
    store = data_store.get()
    for user in store["users"]:
        if get_auth_id(user) == auth_user_id:
            return user
    raise AccessError
