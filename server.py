from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient

app = Flask(__name__, static_folder='/home/pango/projects/dishout/static')
###############################################################################
################################     Constants      ###########################
###############################################################################

MAX_QUERY_LENGTH = 100

###############################################################################
################################     URLS      ################################
###############################################################################

@app.route("/")
def main():
  return render_template('main.html')

@app.route('/<path:path>')
def static_proxy(path):
  # send_static_file will guess the correct MIME type
  return app.send_static_file(path)

# dishes and corresponding restaurants
@app.route("/ajax_get_dish_data", methods=['GET'])
def get_dish_data():
  dish = request.args.get('dish', '')
  sort_by = request.args.get('sort_by', '')
  sort_dir = request.args.get('sort_dir', '')

  dishes = get_db_collection('dishes')
  dishes_list = []
  if sort_by == 'rating':
    dishes_list = dishes.find({ name: dish }).sort({ rating: -1 if sort_dir == 'desc' else 1 }).limit(MAX_QUERY_LENGTH)
  elif sort_by == 'price':
    dishes_list = dishes.find({ name: dish }).sort({ price: -1 if sort_dir == 'desc' else 1 }).limit(MAX_QUERY_LENGTH)
  elif sort_by == 'distance':
    # do later
    pass

  # for associated restaurant data
  restaurant_list = []


  return jsonify(dishes_list)

@app.route("/ajax_submit_review", methods=['POST'])
def submit_review():
  if request.method == 'POST':
    user_phone = request.form['phone']
    user_name = request.form['name']
    user_friends = request.form['friends'] #list

    user = {
        'phone' : user_phone,
        'name' : user_name,
        'friends' : user_friends
    }
    user_mongo_id = users.insert(user)
  return 'success'

###############################################################################
################################     DB      ##################################
###############################################################################

def get_db_connection(db):
    client = MongoClient()
    return client[db]

def get_db_collection(collection):
    return get_db_connection('brick')[collection]

def populate_mock_db():
  dishes = get_db_collection('dishes')
  for i in range(10):
    dish = {
      'name': str(i) + '-dish',
      'price': 1,
      'rating': 4.5,
      'num_ratings': 100,
      'restaurant_id': 123,
    }
    dishes.insert_one(dish)
  # for dish in dishes.find():
  #   print dish

###############################################################################
###############################     Main      ################################
###############################################################################

if __name__ == "__main__":
    populate_mock_db()
    app.run(
	host="0.0.0.0",
	port=9000)
