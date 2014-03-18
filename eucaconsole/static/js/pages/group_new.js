/**
 * @fileOverview IAM Create Group Page JS
 * @requires AngularJS
 *
 */

angular.module('GroupPage', [])
    .controller('GroupPageCtrl', function ($scope, $timeout) {
        $scope.initController = function (group_users, all_users) {
            $scope.setFocus();
        };
        $scope.setFocus = function () {
            $('input#group-name').focus();
        };
    })
;



