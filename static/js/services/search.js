angular.module('dishout')
    .factory('Search', function ($http) {
        var result = {}
        return {
            saveResult:function (data) {
                result = data;
            },
            getResult:function () {
				return $http.get('http://puentes.ca:9000/ajax_get_dish_data?dish=5-dish');
            }
        };
    });