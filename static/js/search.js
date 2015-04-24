var searchCtrl = function($scope, $rootScope, Search, $http) {
	var result = Search.makeQuery().then(function(data) {
		$scope.dishes = data.dishes;
		$scope.restaurants = data.restaurants;
		$scope.reviews = data.reviews;
		$scope.query = data.query;
		console.log($scope);
		console.log("Photo url 	" + $scope.reviews[$scope.dishes[0]['popular_review_id']].photo_url);
	})
	$scope.dish = {
		_id: result['_id'],
		name: result['name'],
		num_ratings: result['num_ratings'],
		price: result['price'],
		rating: result['rating'],
		restaurant_id: result['restaurant_id'],
		reviews: result['reviews']
	}
	$scope.calcRating = function(rating, type) {
		if (type=='full') {
			return new Array(Math.floor(rating));
		}
		else if (type=='half') {
			if (rating - Math.floor(rating) > 0) {
				return [1]
			}
			else {
				return [];
			}
		}
		else if (type=='empty') {
			return new Array(5 - Math.ceil(rating))
		}
	}
	$scope.calcPrice = function(price) {
		return new Array(price)
	}
	$scope.setDish = function(dish) {
		$scope.dish = dish;
		$scope.dish.active = true;
	}
}

app.controller('searchCtrl', searchCtrl)
