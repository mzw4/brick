var homeCtrl = function($scope, $rootScope, $animate, $timeout, Search) {
	
	$scope.submitSearch = function(query) {
		Search.saveResult(query);
	}
}

angular
	.module('dishout')
	.controller('homeCtrl', homeCtrl)