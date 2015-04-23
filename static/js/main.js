var mainCtrl = function($scope, $rootScope, $animate, $timeout) {
	console.log("Main Controller")
	$rootScope.$on('done-loading', function() {
		$timeout(function() {
			$rootScope.loading = false;
		}, 0);
	});

  $('#review_button').on('click', function(event) {
    
  });
}

app.controller('mainCtrl', mainCtrl)