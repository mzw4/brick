var searchCtrl = function($scope, $rootScope, Search, $http) {
	var result = Search.getResult().then(function(data) {
		$scope.results = data.data.dishes;
		console.log(data.data.dishes)
	})
	$scope.dish = {
		_id: -1,
		name: "",
		num_ratings: 0,
		price: 0,
		rating: 0,
		restaurant_id: "",
		reviews: []
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
		$scope.dish.reviews = new Array(10);
	}
}

angular
	.module('dishout')
	.controller('searchCtrl', searchCtrl)