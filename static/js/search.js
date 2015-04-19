var searchCtrl = function($scope, $rootScope, Search, $http) {
	var result = Search.getResult().then(function(data) {
		$scope.results = data.data.dishes;
		console.log(data.data.dishes)
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
		console.log(rating);
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
		//$scope.dish.reviews = dish.reviews;
	}
}

angular
	.module('dishout')
	.controller('searchCtrl', searchCtrl)