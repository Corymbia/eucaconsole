/**
   * @fileOverview Common JS for Custom Filters
   * @requires AngularJS, jQuery, and Purl jQuery URL parser plugin
**/

angular.module('CustomFilters', [])
.filter('escapeURL', function() {
    return function(input) {
      return encodeURIComponent(input);
    };
})
.filter('ellipsis', function () {
    return function (line, num) {
        if( line.length <= num ){
            return line;
        }
        return line.substring(0, num) + "...";
    };
});

