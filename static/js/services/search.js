app.factory('Search', function ($http) {
  var query = {}
  return {
    saveSearch: function (data) {
      query = {
        text: 'sushi',//data.text,
        search_type: 'dish',//data.search_type,
        location: 'New York',//data.location,
      }
    },
    makeQuery:function () {
      return $http.get('/ajax_get_dish_data', { params: query })
        .then(function(response) {
          return response.data;
        });
    }
  };
});