/**
   * @fileOverview Common JS for Custom Filters
   * @requires AngularJS, jQuery, and Purl jQuery URL parser plugin
**/

angular.module('CustomFilter', []).filter('escapeURL', function() {
  return function(input) {
    return encodeURIComponent(input);
  };
});


