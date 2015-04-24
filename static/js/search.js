var searchCtrl = function($scope, $rootScope, Search, $http) {
	var result = Search.makeQuery().then(function(data) {
		$scope.dishes = data.dishes;
		$scope.restaurants = data.restaurants;
		$scope.reviews = data.reviews;
		$scope.query = data.query;
		console.log($scope);
		console.log("Photo url 	" + $scope.reviews[$scope.dishes[0]['popular_review_id']].photo_url);
	})
	$scope.dish;

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

app.controller('searchCtrl', searchCtrl)