var mainCtrl = function($scope, $rootScope, $animate, $timeout) {
	console.log("Main Controller")
	$rootScope.$on('done-loading', function() {
		$timeout(function() {
			$rootScope.loading = false;
		}, 500);
	});
}

angular
	.module('dishout')
	.controller('mainCtrl', mainCtrl)