import math
from pymongo import MongoClient

def to_url_param(param):
	'''
		Takes string and converts into appropriate URL parameter by replacing whitespace with +'s
	'''
	return '+'.join(param.split(' '))

def get_db_connection(db):
    client = MongoClient()
    return client[db]

def get_db_collection(collection):
    return get_db_connection('brick')[collection]

# compute the distance given latitude and longitude coordinate positions in feet
def get_distance(latlng1, latlng2):
	lat1 = math.radians(latlng1['lat'])
	lng1 = math.radians(latlng1['lng'])
	lat2 = math.radians(latlng2['lat'])
	lng2 = math.radians(latlng2['lng'])

	dist = math.acos(
		math.sin(lat1)*math.sin(lat2) + math.cos(lat1)*math.cos(lat2)*math.cos(lng1-lng2))
	_dia_miles = 3963.191
	return _dia_miles * dist