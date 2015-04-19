var homeCtrl = function($scope, $rootScope, $animate, $timeout, Search) {
	$rootScope.loading = true;
	
	$scope.submitSearch = function(query) {
		Search.saveResult(query);
	}
	
	$timeout(function() {
		$rootScope.$emit('done-loading');
	}, 4000);
}

angular
	.module('dishout')
	.controller('homeCtrl', homeCtrl)