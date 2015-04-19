
$(function () {
  $rating_field = $('#rating_field');
  $restaurant_field = $('#restaurant_field');
  $dish_field = $('#dish_field');
  $description_field = $('#description_field');
  $submit_button = $('#submit_button');

  $restaurant_field.val('The Cobra Club');


  // initialize star rating input
  $rating_field.barrating({
    'initialRating': null,
    'showSelectedRating': false,
    onSelect: function(val, text) {
      $rating_field.val(val);
    }
  });

  // Submit callback
  $submit_button.on('click', function(event) {
    event.preventDefault();
    ajax_submit_review()
  });

});

/*
 * Submit the transaction to the server
 */
function ajax_submit_review() {
  var payload = {
    dish: $dish_field.val(),
    rating: $rating_field.val(),
    restaurant: $restaurant_field.val(),
    description: $description_field.val(),
    user_id: 'testuser',
    price: 999,
    photo: 'photo',
    date: (new Date()).toLocaleString(),
    tags: JSON.stringify(['hi', 'da']),
  };

  return $.post('/ajax_submit_review', payload, function(data) {
    if(data) {
      console.log(data);
    }
  });
}