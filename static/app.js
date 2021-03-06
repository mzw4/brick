var app = angular
	.module('dishout', ['ngAnimate','ngRoute', 'customFilters'])
	.config(function($locationProvider, $routeProvider) {
        $routeProvider
			.when('/', {
			   templateUrl: 'static/partials/home.html', 
			   controller: homeCtrl
			})
			.when('/search', {
			   templateUrl: 'static/partials/search.html', 
			   controller: searchCtrl
			})
			.when('/review', {
			   templateUrl: 'static/partials/review.html', 
			   controller: homeCtrl
			})
	});