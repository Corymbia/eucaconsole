/**
 * @fileOverview Instance Volumes page JS
 * @requires AngularJS
 *
 */

angular.module('InstanceVolumes', [])
    .controller('InstanceVolumesCtrl', function ($scope, $http, $timeout) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        // Volume states are: "attached", "attaching", "detaching"
        // 'detached' state doesn't apply here since it won't be attached to the instance
        $scope.loading = false;
        $scope.volumes = [];
        $scope.jsonEndpoint = '';
        $scope.initialLoading = true;
        $scope.detachFormAction = '';
        $scope.initController = function (jsonEndpoint) {
            $scope.jsonEndpoint = jsonEndpoint;
            $scope.initChosenSelector();
            $scope.getInstanceVolumes();
        };
        $scope.initChosenSelector = function () {
            $(document).ready(function() {
                $('#attach-volume-modal').on('open', function() {
                    $('#volume_id').chosen({'width': '100%', search_contains: true});
                });
            });
        };
        $scope.revealDetachModal = function (action, name) {
            var modal = $('#detach-volume-modal');
            $scope.detachFormAction = action;
            $scope.detachVolumeName = name;
            modal.foundation('reveal', 'open');
            setTimeout(function(){
                    var inputElement = modal.find('input[type!=hidden]').get(0);
                    if( inputElement != undefined ){
                        inputElement.focus()
                    }else{
                        modal.find('button').get(0).focus();
                    }
               }, 1000);
        };
        $scope.getInstanceVolumes = function () {
            $http.get($scope.jsonEndpoint).success(function(oData) {
                var transitionalCount = 0;
                $scope.volumes = oData ? oData.results : [];
                $scope.initialLoading = false;
                // Detect if any volume states are transitional
                $scope.volumes.forEach(function(volume) {
                    if (volume['transitional']) {
                        transitionalCount += 1;
                    }
                });
                // Auto-refresh volumes if any of them are transitional
                if (transitionalCount > 0) {
                    $timeout(function() {$scope.getInstanceVolumes()}, 4000);  // Poll every 4 seconds
                }
            }).error(function (oData, status) {
                var errorMsg = oData['error'] || null;
                if (errorMsg && status === 403) {
                    alert(errorMsg);
                    $('#euca-logout-form').submit();
                }
            });
        };
    })
;

