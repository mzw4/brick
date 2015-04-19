from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient, ReturnDocument
from populate_db import to_url_param

import urllib2
import json

app = Flask(__name__)

###############################################################################
################################     Constants      ###########################
###############################################################################

MAX_QUERY_LENGTH = 100
GOOGLE_API_KEY = 'AIzaSyAKVuw31IAwXeb5fuz4G8-Uept41q936hg'

###############################################################################
################################     URLS      ################################
###############################################################################

@app.route("/")
def main():
  get_dish_data()
  return render_template('main.html')

# dishes and corresponding restaurants
@app.route("/ajax_get_dish_data", methods=['GET'])
def get_dish_data():
  # if request.method == 'POST':

    # dish = request.args.get('dish', '')
    # sort_by = request.args.get('sort_by', '')
    # sort_dir = request.args.get('sort_dir', '')

  dish = '5-dish'
  sort_by = 'rating' # price, distance
  sort_dir = 'desc'

  # get collections
  dishes = get_db_collection('dishes')
  restaurants = get_db_collection('restaurants')
  reviews = get_db_collection('reviews')

  # query for dishes
  dishes_list = list(dishes.find({ 'name': dish })\
    .sort(sort_by,  (pymongo.DESCENDING if sort_dir == 'desc' else pymongo.ASCENDING))\
    .limit(MAX_QUERY_LENGTH))

  # get associated restaurant data
  restaurant_ids = map(lambda dish: dish['restaurant_id'], dishes_list)
  restaurant_list = restaurants.find({'_id': {'$in': restaurant_ids}});

  review_ids = []
  for dish in dishes_list:
    review_ids += dish['reviews']
  reviews_list = reviews.find({ '_id': { '$in': review_ids } })

  result = {
    'dishes': format_data_response(dishes_list),
    'restaurants': format_data_response(restaurant_list),
    'reviews': format_data_response(reviews_list),
  }
  return result
  # else:
  #   return 'failed'

@app.route("/ajax_submit_review", methods=['POST'])
def submit_review():
  # if request.method == 'POST':
  # dish = request.args.get('dish', '')
  # restaurant = request.args.get('restaurant', '')
  # rating = request.args.get('rating', '')
  # description = request.args.get('description', '')
  # user_id = request.args.get('user_id', '')
  # price = request.args.get('price', '')
  # tags = request.args.get('tags', '')
  # photo = request.args.get('photo', '')
  # date = request.args.get('date', '')

  dish = '5-dish'
  restaurant = '5r'
  review_text = 'omgomgomg'
  rating = 5.0
  user_id = 9000
  price = 9999
  tags = ['tasty', 'flaming hot']
  photo = 'eadawd'
  date = 'some day'

  # get collections
  dishes = get_db_collection('dishes')
  restaurants = get_db_collection('restaurants')
  reviews = get_db_collection('reviews')

  reviewed_restaurant = restaurants.find_one({ 'name': restaurant })
  if reviewed_restaurant:
    reviewed_restaurant_id = reviewed_restaurant['_id']
    reviewed_dish_id = None
    new_review_id = next_id('reviews')

    # update the dish with the new_review, or add it if it doesn't exist
    reviewed_dish = dishes.find_one({ 'name': dish, 'restaurant_id': reviewed_restaurant_id })
    if reviewed_dish:
      reviewed_dish_id = reviewed_dish['_id']

      update_result = dishes.update_one(
        { '_id': reviewed_dish_id },
        {
          '$push': {
            'reviews': new_review_id,         # add new_review
            'tags': { '$each': tags }         # add tags
          },
          '$inc': { 'num_ratings': 1 },       # increment num_ratings values
          '$set': {                           # update running average of rating
            'rating': (reviewed_dish['rating'] * reviewed_dish['num_ratings'] + rating) / (reviewed_dish['num_ratings'] + 1)
          }
        },
      )
      print update_result.raw_result
    else:
      # add the dish
      reviewed_dish_id = dishes.insert({
        '_id': next_id('dishes'),
        'name': dish,
        'restaurant_id': reviewed_restaurant_id,
        'price': price,
        'reviews': [new_review],
        'rating': rating,
        'num_ratings': 1,
        'tags': tags
      })

    # construct review and insert it
    new_review = {
      '_id': new_review_id,
      'user_id': user_id,
      'dish_id': reviewed_dish_id,
      'restaurant_id': reviewed_restaurant_id,
      'rating': rating,
      'text': review_text,
      'date': date,
      'photo': photo,
      'votes': 0,
    }
    reviews.insert(new_review)

  print dishes.find_one({ '_id': reviewed_dish['_id'] })
  print [r for r in reviews.find()]
  return 'success'

@app.route("/ajax_upvote_review", methods=['POST'])
def upvote_review():
  review_id = request.args.get('review_id', '')

	reviews = get_db_collection('reviews')
	reviews.update({ '_id': review_id }, {'$inc': { 'votes': 1 }})
	return 'success'

@app.route("/ajax_downvote_review", methods=['POST'])
def downvote_review():
  review_id = request.args.get('review_id', '')

	reviews = get_db_collection('reviews')
	reviews.update({ '_id': review_id }, {'$inc': { 'votes': -1 }})
	return 'success'

@app.route("/filter_by_distance", methods=['GET'])
def filter_by_distance(restaurants, user_location, distance):
	'''
		Takes the user location by address and finds all restaurants within the distance in feet
	'''
	restaurants_in_range = []
	url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + to_url_param(user_location) + '&key=' + GOOGLE_API_KEY
	response = urllib2.urlopen(url).read()
	location = response['results'][0]['geometry']['location']
	user_latlng = { 'lat': location['lat'], 'lng': location['lng'] }

	for restaurant in restaurants:
		restaurant_latlng = { 'lat': restaurant['lat_lng'][0], 'lng': restaurant['lat_lng'[1]] }
		dist_in_feet = get_distance(user_latlng, restaurant_latlng)
		if dist_in_feet <= distance:
			restaurants_in_range.append(restaurant)
	return restaurants_in_range

###############################################################################
######################     Helper functions      ##############################
###############################################################################

# compute the distance given latitude and longitude coordinate positions in feet
def get_distance(latlng1, latlng2):
  lat1 = math.radians(latlng1['lat'])
  lng1 = math.radians(latlng1['lng'])
  lat2 = math.radians(latlng2['lat'])
  lng2 = math.radians(latlng2['lng'])

  dist = math.acos(
    math.sin(lat1)*math.sin(lat2) + math.cos(lat1)*math.cos(lat2)*math.cos(lng1-lng2))
  _dia_miles = 3963.191
  return _dia_miles * dist * 5280

###############################################################################
################################     DB      ##################################
###############################################################################

def get_db_connection(db):
    client = MongoClient()
    return client[db]

def get_db_collection(collection):
    return get_db_connection('brick')[collection]

"""
Gets the next auto-incrementing id for the specified collection
"""
def next_id(collection):
  counters = get_db_collection('counters')
  result = counters.find_one_and_update(
    { '_id': collection },
    { '$inc': { 'seq': 1 } },
    upsert=True,
    return_document=ReturnDocument.AFTER
  )
  return result['seq'];

"""
Format the db response in an easy to interpret way for the frontend
Converts the list into a dict of {id -> object}
"""
def format_data_response(data):
  formatted_data = {}
  for d in data:
    formatted_data[d['_id']] = d
  return formatted_data

def populate_mock_db():
  get_db_collection('dishes').remove({})
  get_db_collection('restaurants').remove({})
  get_db_collection('reviews').remove({})
  get_db_collection('counters').remove({})

  dishes = get_db_collection('dishes')
  for i in range(100):
    dish = {
      '_id': i,
      'name': str(i%10) + '-dish',
      'price': 1,
      'rating': 4.5,
      'num_ratings': 100,
      'restaurant_id': i%15,
      'reviews': [],
      'tags': [],
    }
    dishes.insert_one(dish)

  restaurants = get_db_collection('restaurants')
  for i in range(15):
    r = {
      '_id': i,
      'name': str(i) + 'r',
      'address': 'crazyshit',
      'rating': 4.5,
      'type': ['Mexican'],
    }
    restaurants.insert_one(r)

###############################################################################
###############################     Main      ################################
###############################################################################
populate_mock_db()
submit_review()
get_dish_data()

if __name__ == "__main__":
    app.run(port=5000)
