import requests

# Firebase Realtime Database URL
database_url = 'https://te2003bgame-default-rtdb.firebaseio.com/'

# API key for authentication
api_key = 'AIzaSyBlBnUsgOurHicryXZnSgsym_3l98Nlj'

# Path to the node you want to update
node = 'game'  # Update this with the path to your node

# New value to set
node_value = 'result' # Update this with the new value you want to set

from firebase import firebase  
firebase = firebase.FirebaseApplication(database_url, None)  
data =  2
# replace the value at "value" for data
result = firebase.put(node, node_value, 2)
