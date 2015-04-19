angular.module('dishout')
    .factory('Search', function ($http) {
        var result = {}
        return {
            saveResult:function (data) {
                result = data;
            },
            getResult:function () {
                var params = result['selection'] + '=' + result['params']
                if (result['selection'] === 'location' || result['selection'] === 'dish')
                    params += '&search_type=' + result['selection']
				return $http.get('/ajax_get_dish_data?' + params);
            }
        };
    });