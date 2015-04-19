angular.module('dishout')
    .factory('Search', function ($http) {
        var result = {}
        return {
            saveResult:function (data) {
                result = data;
            },
            getResult:function () {
				return $http.get('/ajax_get_dish_data?dish=1-dish');
            }
        };
    });