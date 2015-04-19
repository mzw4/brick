var searchCtrl = function($scope, $rootScope, Search) {
	var result = Search.getResult();
	console.log(result)
}

angular
	.module('dishout')
	.controller('searchCtrl', searchCtrl)