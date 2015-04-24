app.directive('hoverslide', function () {
    return {
      restrict: 'A',
      link: function (scope, element, attrs) {
        element.bind('mouseover', function (hover) {
          var el = element.find('.wrapper');
          el.addClass('small_info');
        });
        element.bind('mouseout', function (hover) {
          var el = element.find('.wrapper');
          element.find('.wrapper').removeClass('small_info');
        });
      }
    };
  });

app.directive('stopEvent', function () {
    return {
        restrict: 'A',
        link: function (scope, element, attr) {
            element.bind('click', function (e) {
                console.log('stopping propagation');
                e.stopPropagation();
            });
        }
    };
 });


// Here we create a module to group these directives jquery related
    var jqueryDirectives = angular.module("jqueryDirectives", []);

    // Here we add a directive to the module. camelCase naming in this file (mySlide) and dash separated in html (my-Slide)
    jqueryDirectives.directive("mySlide", [
      function() {
        return {

          // This means the directive can be used as an attribute only. Example <div data-my-slide="variable"> </div>
          restrict: "A",

          // This is the functions that gets executed after Angular has compiled the html
          link: function(scope, element, attrs) {

            // We dont want to abuse on watch but here it is critical to determine if the parameter has changed.
            scope.$watch(attrs.mySlide, function(newValue, oldValue) {

              // This is our logic. If parameter is true slideDown otherwise slideUp.
              // TODO: This should be transformed into css transition or angular animator if IE family supports it
              if (newValue) {
                return element.slideDown();
              } else {
                return element.slideUp();
              }
            });
          }
        };
      }
    ]);