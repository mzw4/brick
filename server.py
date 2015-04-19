from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient, ReturnDocument

import urllib2
import json

app = Flask(__name__)

###############################################################################
################################     Constants      ###########################
###############################################################################

MAX_QUERY_LENGTH = 100

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
  if request.method == 'POST':

    # dish = request.args.get('dish', '')
    # sort_by = request.args.get('sort_by', '')
    # sort_dir = request.args.get('sort_dir', '')

    dish = '3-dish'
    sort_by = 'rating' # price, distance
    sort_dir = 'desc'

    # query for dishes
    dishes = get_db_collection('dishes')
    dishes_list = dishes.find({ 'name': dish })\
      .sort(sort_by,  (pymongo.DESCENDING if sort_dir == 'desc' else pymongo.ASCENDING))\
      .limit(MAX_QUERY_LENGTH)

    # get associated restaurant data
    restaurant_ids = map(lambda dish: dish['restaurant_id'], dishes_list)
    restaurants = get_db_collection('restaurants')
    restaurant_list = restaurants.find({'_id': {'$in': restaurant_ids}});

    result = {
      'dishes': dishes_list,
      'restaurants': restaurant_list,
    }
    return result
  else:
    return 'failed'

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

  dishes = get_db_collection('dishes')
  restaurants = get_db_collection('restaurants')
  reviews = get_db_collection('reviews')

  reviewed_restaurant = restaurants.find_one({ 'name': restaurant })
  if reviewed_restaurant:
    reviewed_restaurant_id = reviewed_restaurant['_id']
    new_review = {
      '_id': next_id('reviews'),
      'user_id': user_id,
      'rating': rating,
      'text': review_text,
      'photo': photo,
      'votes': 0,
    }
    new_review_id = reviews.insert(new_review)

    dish_id = { 'name': dish, 'restaurant_id': reviewed_restaurant_id }
    reviewed_dish = dishes.find_one(dish_id)
    if reviewed_dish:
      # update the dish with the new_review
      print reviewed_dish
      print dishes.update_one(dish_id,
        {
          '$push': {
            'reviews': new_review_id,            # add new_review
            'tags': { '$each': tags }           # add tags
          },
          '$inc': { 'num_ratings': 1 },       # increment num_ratings values
          '$set': {                           # update running average of rating
            'rating': (reviewed_dish['rating'] * reviewed_dish['num_ratings'] + rating) / (reviewed_dish['num_ratings'] + 1)
          }
        },
      )
    else:
      # add the dish
      dishes.insert({
        '_id': next_id('dishes'),
        'name': dish,
        'restaurant_id': reviewed_restaurant_id,
        'price': price,
        'reviews': [new_review],
        'rating': rating,
        'num_ratings': 1,
        'tags': tags
      })

  print dishes.find_one({ 'name': dish })
  return 'success'

@app.route("/ajax_upvote_review", methods=['POST'])
def upvote_review(review_id):
	reviews = get_db_collection('reviews')
	reviews.update({ '_id': review_id }, {'$inc': { 'votes': 1 }})
	return 'success'

@app.route("/ajax_downvote_review", methods=['POST'])
def downvote_review(review_id):
	reviews = get_db_collection('reviews')
	reviews.update({ '_id': review_id }, {'$inc': { 'votes': -1 }})
	return 'success'

@app.route("/filter_by_distance", methods=['GET'])
def filter_by_distance(restaurants, user_location, distance):
	'''
		Takes the user location by address and finds all restaurants within the distance in feet
	'''
	user_location = "+".join(user_location.split(' '))
	restaurants_in_range = []

	for restaurant in restaurants:
		destination = restaurant['address']
		url = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins=' + user_location
			+ '&destination=' + destination + '&units=imperial&key=' + GOOGLE_DISTANCE_API_KEY
		response = urllib2.urlopen(url).read()
		dist_in_feet = response['rows'][0]['elements'][0]['distance']['value']
		if dist_in_feet <= distance:
			restaurants_in_range.append(restaurant)
	return restaurants_in_range


###############################################################################
################################     DB      ##################################
###############################################################################

def get_db_connection(db):
    client = MongoClient()
    return client[db]

def get_db_collection(collection):
    return get_db_connection('brick')[collection]

def next_id(collection):
  counters = get_db_collection('counters')
  result = counters.find_one_and_update(
    { '_id': collection },
    { '$inc': { 'seq': 1 } },
    upsert=True,
    return_document=ReturnDocument.AFTER
  )
  return result['seq'];

def populate_mock_db():
  get_db_collection('dishes').remove()
  get_db_collection('restaurants').remove()

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

if __name__ == "__main__":
    app.run(port=5000)
