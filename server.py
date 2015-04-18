from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)

###############################################################################
################################     URLS      ################################
###############################################################################

@app.route("/")
def main():
    return render_template('main.html')

# dishes and corresponding restaurants
@app.route("/ajax_get_dish_data", methods=['GET'])
def get_dish_data():
    dishes = get_db_collection('dishes')

    return []

@app.route("/ajax_submit_review", methods=['POST']))
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
    return get_db_connection('dishout')[collection]

def populate_mock_db():
  # dishes = get_db_collection('dishes')
  # for i in range(10):
  #   dish = {
  #     name: str(i) + '-dish',
  #     price: 1,
  #     rating: 4.5,
      
  #   }
  #   dishes.insert

###############################################################################
###############################     Main      ################################
###############################################################################

if __name__ == "__main__":
    app.run()
