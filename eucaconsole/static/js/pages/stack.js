/**
 * @fileOverview Stack Detail Page JS
 * @requires AngularJS
 *
 */

angular.module('StackPage', ['EucaConsoleUtils'])
    .controller('StackPageCtrl', function ($scope, eucaUnescapeJson) {
        $scope.initController = function (optionsJson) {
            var options = JSON.parse(eucaUnescapeJson(optionsJson));
            $scope.stack_name = optionsJson.stack_name;
            $scope.setWatch();
            $scope.setFocus();
        };
        $scope.setWatch = function () {
            $(document).on('submit', '[data-reveal] form', function () {
                $(this).find('.dialog-submit-button').css('display', 'none');                
                $(this).find('.dialog-progress-display').css('display', 'block');                
            });
        };
        $scope.setFocus = function () {
            $(document).on('ready', function(){
                $('.actions-menu').find('a').get(0).focus();
            });
            $(document).on('opened', '[data-reveal]', function () {
                var modal = $(this);
                var modalID = $(this).attr('id');
                if (modalID.match(/delete/)) {
                    var closeMark = modal.find('.close-reveal-modal');
                    if(!!closeMark){
                        closeMark.focus();
                    }
                } else {
                    var inputElement = modal.find('input[type!=hidden]').get(0);
                    var modalButton = modal.find('button').get(0);
                    if (!!inputElement) {
                        inputElement.focus();
                    } else {
                        if (!!modalButton) {
                            modalButton.focus();
                        }
                    }
                }
            });
        };
    })
;

