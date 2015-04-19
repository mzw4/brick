
var dishes = [];
var restaurants = [];

var uploaded_photo = null;

Dropzone.autoDiscover = false;

$(function () {
  $rating_field = $('#rating_field');
  $restaurant_field = $('#restaurant_field');
  $dish_field = $('#dish_field');
  $description_field = $('#description_field');
  $image_field = $('#image_field');
  $img_display = $('#img_display');
  $image_upload_form = $('#image_upload_form');
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

  // submit callback
  $submit_button.on('click', function(event) {
    event.preventDefault();
    ajax_submit_review()
  });

  // image upload callback
  $image_field.on('change', function(event) {
    var reader = new FileReader();
    reader.onload = function(e) {
      var binary = e.target.result;
      uploaded_photo = binary;
      $img_display.attr('src', binary).hide().fadeIn();
    }
    reader.readAsDataURL(this.files[0]);
  });

  // initialize dropzone
  // $image_upload_form.dropzone();
  var myDropzone = new Dropzone("#image_upload_form");
  myDropzone.on("complete", function(file) {
    console.log(file);
  });

  // load name data and initialize typeahead
  ajax_load_name_data().done(function(data) {
    if(data) {
      console.log(data);

      // initialize typeahead when data is received
      dishes = data['dish_names'];
      restaurants = data['restaurant_names'];

      $dish_field.typeahead({
        hint: true,
        highlight: true,
        minLength: 1
      }, {
        name: 'dish_names',
        displayKey: 'value',
        source: substringMatcher(dishes)
      });

      $restaurant_field.typeahead({
        hint: true,
        highlight: true,
        minLength: 1
      }, {
        name: 'restaurant_names',
        displayKey: 'value',
        source: substringMatcher(restaurants)
      });
    }

  });

});

/*
 * Submit the transaction to the server
 */
function ajax_load_name_data() {
  return $.get('/ajax_get_name_data');
}

/*
 * Submit the transaction to the server
 */
function ajax_submit_review() {
  var payload = {
    dish: $dish_field.val(),
    rating: $rating_field.val(),
    restaurant: $restaurant_field.val(),
    review_text: $description_field.val(),
    user_id: 'testuser',
    price: 999,
    photo: uploaded_photo,
    date: (new Date()).toLocaleString(),
    tags: JSON.stringify(['ta', 'da']),
  };

  return $.post('/ajax_submit_review', payload, function(data) {
    if(data) {
      console.log(data);
    }
  });
}

// https://twitter.github.io/typeahead.js/examples/
var substringMatcher = function(strs) {
  return function findMatches(q, cb) {
    var matches, substrRegex;
 
    // an array that will be populated with substring matches
    matches = [];
 
    // regex used to determine if a string contains the substring `q`
    substrRegex = new RegExp(q, 'i');
 
    // iterate through the pool of strings and for any string that
    // contains the substring `q`, add it to the `matches` array
    $.each(strs, function(i, str) {
      if (substrRegex.test(str)) {
        // the typeahead jQuery plugin expects suggestions to a
        // JavaScript object, refer to typeahead docs for more info
        matches.push({ value: str });
      }
    });
 
    cb(matches);
  };
};
