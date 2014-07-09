/**
 * @fileOverview Image page JS
 * @requires AngularJS
 *
 */

// Image page includes the tag editor, so pull in that module as well.
angular.module('ImagePage', ['BlockDeviceMappingEditor', 'TagEditor'])
    .controller('ImagePageCtrl', function ($scope) {
        $scope.isPublic = '';
        $scope.launchPermissions = [];
        $scope.isAccountNotTyped = true;
        $scope.isNotChanged = true;
        $scope.disabledExplanationVisible = false;
        $scope.initController = function (isPublic, launchPermissions){
            $scope.isPublic = isPublic;
            $scope.launchPermissions = launchPermissions;
            $scope.setWatch();
            $scope.setFocus();
        };
        $scope.setWatch = function () {
            $scope.$on('tagUpdate', function($event) {
                $scope.isNotChanged = false;
            });
            $(document).on('input', '#description', function () {
                $scope.isNotChanged = false;
                $scope.$apply();
            });
            $(document).on('input', '#add-account-inputbox', function () {
                $scope.isAccountNotTyped = false;
                $scope.$apply();
            });
            // Handle the unsaved tag issue
            $(document).on('submit', '#image-detail-form', function(event) {
                $('input.taginput').each(function(){
                    if($(this).val() !== ''){
                        event.preventDefault(); 
                        $('#unsaved-tag-warn-modal').foundation('reveal', 'open');
                        return false;
                    }
                });
            });
        };
        $scope.setFocus = function () {
            $(document).on('ready', function(){
                $('.actions-menu').find('a').get(0).focus();
            });
        };
        $scope.removeAccount = function (account) {
            var index = $scope.launchPermissions.indexOf(account);
            if (index > -1) {
                $scope.launchPermissions.splice(index, 1);
            }        
            $scope.isNotChanged = false;
            $scope.$apply();
        };
        $scope.addAccount = function () {
           if( $scope.newAccount !== "" && $scope.newAccount !== undefined ){
               $scope.launchPermissions.push($scope.newAccount);
               $scope.newAccount = "";
               $scope.isAccountNotTyped = true;
               $scope.isNotChanged = false;
           } 
        };
    })
;

