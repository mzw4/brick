var homeCtrl = function($scope, $rootScope, $animate, $timeout, Search) {
	
	$scope.submitSearch = function(selection, params) {
		Search.saveResult({'selection': selection, 'params': params});
	}

	$scope.options = {
		"values": {"By Dish": "dish", "By Restaurant": "restaurant_id", "By Location": "location"},
		"name": "search_type",
		"value": "dish"
	};

	$scope.options = {
    "AL" : "Alabama",
    "AK" : "Alaska",
    "AS" : "American Samoa"
  };
}

angular
	.module('dishout')
	.controller('homeCtrl', homeCtrl)