angular
	.module('dishout', ['ngAnimate','ngRoute'])
	.config(function($locationProvider, $routeProvider) {
        $routeProvider.when('/', {
           templateUrl: '../templates/home.html', 
           controller: homeCtrl
        });
	});