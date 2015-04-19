angular.module('dishout')
    .factory('Search', function () {
        var result = {};

        return {
            saveResult:function (data) {
                result = data;
            },
            getResult:function () {
                return result;
            }
        };
    });