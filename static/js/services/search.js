angular.module('dishout')
    .factory('Search', function ($http) {
        var result = {}
        return {
            saveResult:function (data) {
                result = data;
            },
            getResult:function () {
                var params = result['selection'] + '=' + result['params'];
                params += '&search_type=' + result['selection'];
                params += '&location=' + result['location'];

				return $http.get('/ajax_get_dish_data?' + params);
            }
        };
    });