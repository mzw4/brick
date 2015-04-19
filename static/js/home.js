var homeCtrl = function($scope, $rootScope, $animate, $timeout, Search) {
	
	$scope.submitSearch = function(selection, query, location) {
		Search.saveResult({'selection': selection, 'params': query, 'location': location });
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

  $('.dish-search').val('sushi');
  $('.location-search').val('354 Clement St San Francisco, CA 94118');
}

angular
	.module('dishout')
	.controller('homeCtrl', homeCtrl)