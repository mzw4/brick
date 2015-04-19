from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient, ReturnDocument
from bson.binary import Binary
from datetime import datetime

from utils import get_db_connection, get_db_collection, to_url_param, get_distance

import pymongo
import urllib2
import json
import math
import ast

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
  return render_template('main.html')

@app.route("/review")
def review():
  return render_template('review.html')

# dishes and corresponding restaurants
@app.route("/ajax_get_dish_data", methods=['GET'])
def get_dish_data():
  if request.method == 'GET':

    dish = request.args.get('dish', '')
    sort_by = request.args.get('sort_by', 'rating')
    sort_dir = request.args.get('sort_dir', 'desc')
    location = request.args.get('location', 'new+york')
    distance = request.args.get('distance', '10')
    restaurant_id = request.args.get('restaurant_id', '')
    search_type = request.args.get('search_type', 'location')
  # if True:
  #   dish = '5-dish'
  #   sort_by = 'rating'  # price, distance
  #   sort_dir = 'desc'
  #   location = '775 New York, Brooklyn, New York 11203'
  #   distance = 5
  #   search_type = 'dish'

    # get collections
    dishes = get_db_collection('dishes')
    restaurants = get_db_collection('restaurants')
    reviews = get_db_collection('reviews')
    images = get_db_collection('images')

    # filter restaurants by distance to specified location
    all_restaurants = restaurants.find()
    filtered_restaurants = filter_by_distance(all_restaurants, location, float(distance))
    filtered_restaurants_ids = map(lambda r: r['_id'], filtered_restaurants)

    dishes_list = []
    if search_type == 'dish':
      # query for dishes matching the specified name or tags and within the specified distance
      dishes_list = list(dishes.find({ 'name': dish, 'restaurant_id': { '$in': filtered_restaurants_ids } })\
        .sort(sort_by,  (pymongo.DESCENDING if sort_dir == 'desc' else pymongo.ASCENDING))\
        .limit(MAX_QUERY_LENGTH))
    elif search_type == 'location':
      # query for dishes within the specified distance
      dishes_list = list(dishes.find({ 'restaurant_id': { '$in': filtered_restaurants_ids } })\
        .sort(sort_by,  (pymongo.DESCENDING if sort_dir == 'desc' else pymongo.ASCENDING))\
        .limit(MAX_QUERY_LENGTH))
    elif search_type == 'restaurant':
      # query for dishes at this restaurant
      dishes_list = list(dishes.find({ 'restaurant_id': restaurant_id })\
        .sort(sort_by,  (pymongo.DESCENDING if sort_dir == 'desc' else pymongo.ASCENDING))\
        .limit(MAX_QUERY_LENGTH))
      formatted_search_type = 'Restaurants'
    else:
      print 'INVALID SEARCH TYPE'

    # get associated restaurant data
    restaurant_ids = set(map(lambda dish: dish['restaurant_id'], dishes_list))
    restaurant_list = filter(lambda r: r if r['_id'] in restaurant_ids else None, filtered_restaurants)

    # get associated review data
    review_ids = []
    for dish in dishes_list:
      review_ids += dish['reviews']
    reviews_list = list(reviews.find({ '_id': { '$in': review_ids } }))

    photo_ids = []
    for r in reviews_list:
      photo_ids += [r['photo']]
    print photo_ids
    photos_list = list(images.find({ '_id': { '$in': photo_ids } }))

    # print dishes_list
    # print restaurant_list
    # print reviews_list

    # form response
    result = {
      'dishes': format_data_response(dishes_list),
      'restaurants': format_data_response(restaurant_list),
      'reviews': format_data_response(reviews_list),
      'photos': format_data_response(photos_list)
    }
    print photos_list
    return jsonify(result)

  else:
    return 'failed'


@app.route("/ajax_submit_review", methods=['POST'])
def submit_review():
  if request.method == 'POST':
    dish = request.form.get('dish', '')
    restaurant = request.form.get('restaurant', '')
    rating = int(request.form.get('rating', ''))
    review_text = request.form.get('review_text', '')
    user_id = request.form.get('user_id', '')
    price = request.form.get('price', '')
    tags = ast.literal_eval(request.form.get('tags', ''))
    photo = request.form.get('photo', '')
    date = datetime.now()

  # if True:
  #   dish = '5-disddh'
  #   restaurant = 'The Cobra Club'
  #   review_text = 'omgomgomg'
  #   rating = 5.0
  #   user_id = '9000'
  #   price = '9999'
  #   tags = ['tasty', 'flaming hot']
  #   photo = 'eadawd'
  #   date = 'some day'

    print dish, restaurant, rating, review_text, user_id, price, tags, photo, date

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
        num_ratings = int(reviewed_dish['num_ratings'])

        update_result = dishes.update_one(
          { '_id': reviewed_dish_id },
          {
            '$push': {
              'reviews': new_review_id,         # add new_review
              'tags': { '$each': tags }         # add tags
            },
            '$inc': { 'num_ratings': 1 },       # increment num_ratings values
            '$set': {                           # update running average of rating
              'rating': (float(reviewed_dish['rating']) * int(num_ratings) + int(rating)) / (int(num_ratings) + 1)
            }
          },
        )
        print update_result.raw_result
      else:
        # add the dish
        new_dish = {
          '_id': next_id('dishes'),
          'name': dish,
          'restaurant_id': reviewed_restaurant_id,
          'price': price,
          'reviews': [new_review_id],
          'rating': rating,
          'num_ratings': 1,
          'tags': tags
        }
        reviewed_dish_id = dishes.insert(new_dish)
        print 'added new dish ' + str(reviewed_dish_id)

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

      print "ADDED REVIEW"
      print [r for r in reviews.find({ '_id': new_review_id })]
    return 'success'
  else:
    return 'fail'

@app.route("/ajax_upvote_review", methods=['POST'])
def upvote_review():
  review_id = request.form.get('review_id', '')

  reviews = get_db_collection('reviews')
  reviews.update({ '_id': review_id }, {'$inc': { 'votes': 1 }})
  return 'success'

@app.route("/ajax_downvote_review", methods=['POST'])
def downvote_review():
  review_id = request.form.get('review_id', '')

  reviews = get_db_collection('reviews')
  reviews.update({ '_id': review_id }, {'$inc': { 'votes': -1 }})
  return 'success'

@app.route("/ajax_get_name_data", methods=['GET'])
def get_name_data():
  if request.method == 'GET':
    dishes = get_db_collection('dishes')
    restaurants = get_db_collection('restaurants')

    pipeline = [
      {"$group": {"_id": "$name", "count": {"$sum": 1}}},
    ]
    dish_names = map(lambda d: d['_id'], list(dishes.aggregate(pipeline)))
    restaurant_names = map(lambda r: r['_id'], list(restaurants.aggregate(pipeline)))
    return jsonify({ 'dish_names': dish_names, 'restaurant_names': restaurant_names })

###############################################################################
######################     Helper functions      ##############################
###############################################################################

@app.route("/filter_by_distance", methods=['GET'])
def filter_by_distance(restaurants, user_location, distance):
  '''
    Takes the user location by address and finds all restaurants within the distance in feet
  '''
  restaurants_in_range = []
  url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + to_url_param(user_location) + '&key=' + GOOGLE_API_KEY
  response = json.loads(urllib2.urlopen(url).read())
  location = response['results'][0]['geometry']['location']
  user_latlng = { 'lat': location['lat'], 'lng': location['lng'] }

  for restaurant in restaurants:
    restaurant_latlng = { 'lat': restaurant['lat_long'][0], 'lng': restaurant['lat_long'][1] }
    dist_mi = get_distance(user_latlng, restaurant_latlng)
    if dist_mi <= distance:
      restaurants_in_range.append(restaurant)
  return restaurants_in_range

###############################################################################
################################     DB      ##################################
###############################################################################


def next_id(collection):
	"""
	Gets the next auto-incrementing id for the specified collection
	"""
	counters = get_db_collection('counters')
	result = counters.find_one_and_update(
		{ '_id': collection },
		{ '$inc': { 'seq': 1 } },
		upsert=True,
		return_document=ReturnDocument.AFTER
	)
	return result['seq'];


def format_data_response(data):
	"""
	Format the db response in an easy to interpret way for the frontend
	Converts the list into a dict of {id -> object}
	"""
	formatted_data = {}
	for d in data:
		formatted_data[d['_id']] = d
	return formatted_data


def populate_mock_db():
  get_db_collection('dishes').remove({})
  # get_db_collection('restaurants').remove({})
  # get_db_collection('reviews').remove({})
  get_db_collection('counters').remove({})

  dishes = get_db_collection('dishes')
  for i in range(100):
    dish = {
      '_id': next_id('dishes'),
      'name': str(i%10) + '-dish',
      'price': 1,
      'rating': 4.5,
      'num_ratings': 100,
      'restaurant_id': 'the-cobra-club-bushwick',
      'reviews': [],
      'tags': [],
    }
    dishes.insert_one(dish)

  # restaurants = get_db_collection('restaurants')
  # for i in range(15):
  #   r = {
  #     '_id': i,
  #     'name': str(i) + 'r',
  #     'address': 'crazyshit',
  #     'rating': 4.5,
  #     'type': ['Mexican'],
  #   }
  #   restaurants.insert_one(r)

  dish = {
    '_id': next_id('dishes'),
    'name': 'sushi',
    'price': 15.99,
    'rating': 4.5,
    'num_ratings': 10,
    'restaurant_id': 'the-cobra-club-bushwick',
    'reviews': [],
    'tags': [],
  }
  dishes.insert_one(dish)
  dish = {
    '_id': next_id('dishes'),
    'name': 'sushi',
    'price': 15.99,
    'rating': 4.5,
    'num_ratings': 10,
    'restaurant_id': 'shabu-house-san-francisco-3',
    'reviews': [],
    'tags': [],
  }
  dishes.insert_one(dish)

###############################################################################
###############################     Main      ################################
###############################################################################
populate_mock_db()
# submit_review()
# get_dish_data()
# get_name_data()

if __name__ == "__main__":
  app.debug = True
  app.run(host="0.0.0.0", port=9000)
