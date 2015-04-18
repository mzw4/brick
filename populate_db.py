from pymongo import MongoClient
import urllib
import urllib2
import oauth2
import json
import pprint
import itertools

CONSUMER_KEY = '41Gqwxv9uNmAarZqhSdOlQ'
CONSUMER_SECRET = 'Q0LSBcmxBrtM41ufYiuH2EX24FM'
TOKEN = 'SR1_IiK-T9hqw8DRKyPP4xukmC7PnYhK'
TOKEN_SECRET = 'cKrWG2yYCyHazOZe_vsgMJH6_lE'

API_HOST = 'api.yelp.com'
SEARCH_PATH = '/v2/search/'
BUSINESS_PATH = '/v2/business/'
DEFAULT_TERM = 'food'

def get_db_connection(db):
    client = MongoClient()
    return client[db]

def get_db_collection(collection):
    return get_db_connection('brick')[collection]

def request(host, path, url_params=None):
    """Prepares OAuth authentication and sends the request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        urllib2.HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = 'http://{0}{1}?'.format(host, urllib.quote(path.encode('utf8')))

    consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    oauth_request = oauth2.Request(method="GET", url=url, parameters=url_params)

    oauth_request.update(
        {
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': oauth2.generate_timestamp(),
            'oauth_token': TOKEN,
            'oauth_consumer_key': CONSUMER_KEY
        }
    )
    token = oauth2.Token(TOKEN, TOKEN_SECRET)
    oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
    signed_url = oauth_request.to_url()
    
    print u'Querying {0} ...'.format(url)

    conn = urllib2.urlopen(signed_url, None)
    try:
        response = json.loads(conn.read())
    finally:
        conn.close()

    return response

def search(term, location):
    """Query the Search API by a search term and location.
    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
    Returns:
        dict: The JSON response from the request.
    """
    
    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'offset': 980
    }
    return request(API_HOST, SEARCH_PATH, url_params=url_params)

def get_business(business_id):
    """Query the Business API by a business ID.
    Args:
        business_id (str): The ID of the business to query.
    Returns:
        dict: The JSON response from the request.
    """
    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path)

def query_api(term, location):
    """Queries the API by the input values from the user.
    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """
    response = search(term, location)
    businesses = response.get('businesses')

    if not businesses:
        print u'No businesses for {0} in {1} found.'.format(term, location)
        return

    business_id = businesses[0]['id']

    return businesses

connection = get_db_connection('brick')
restaurants = get_db_collection('restaurants')
ny_food_response = query_api('food', 'new+york')
sf_food_response = query_api('food', 'san+francisco')
food_responses = ny_food_response + sf_food_response
for entry in food_responses:
	location = entry['location']
	restaurants.insert(
		{
			'_id': entry['id'],
			'name': entry['name'],
			'address': location['address'][0] + ' ' + location['city'] + ', '
				+ location['state_code'] + ' ' + location['postal_code'],
			'phone': entry['phone'],
			'dishes': [],
			'type': list(itertools.chain(entry['categories'])),
			'rating': entry['rating']
		}
	)
