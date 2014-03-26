/**
 * @fileOverview Dashboard JS
 * @requires AngularJS
 *
 */

angular.module('Dashboard', [])
    .controller('DashboardCtrl', function ($scope, $http) {
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.jsonEndpoint = '';
        $scope.selectedZone = '';
        $scope.storedZoneKey = 'dashboard_availability_zone';
        $scope.zoneDropdown = $('#zone-dropdown');
        $scope.itemsLoading = true;
        $scope.setInitialZone = function () {
            var storedZone = localStorage.getItem($scope.storedZoneKey);
            $scope.selectedZone = storedZone || '';
        };
        $scope.initController = function (jsonItemsEndpoint) {
            $scope.jsonEndpoint = jsonItemsEndpoint;
            $scope.setInitialZone();
            $scope.setWatch();
            $scope.getItemCounts();
        };
        $scope.getItemCounts = function() {
            var jsonUrl = $scope.jsonEndpoint;
            if ($scope.selectedZone) {
                jsonUrl += '?zone=' + $scope.selectedZone;
            }
            $http.get(jsonUrl).success(function(oData) {
                var results = oData ? oData : {};
                $scope.itemsLoading = false;
                $scope.totals = results;
            }).error(function (oData, status) {
                var errorMsg = oData['message'] || null;
                if (errorMsg && status === 403) {
                    alert(errorMsg);
                    $('#euca-logout-form').submit();
                }
            });
        };
        $scope.setZone = function (zone) {
            $scope.itemsLoading = true;
            $scope.selectedZone = zone;
            localStorage.setItem($scope.storedZoneKey, zone);
            $scope.zoneDropdown.removeClass('open').removeAttr('style');
            $scope.getItemCounts();
        };
        $scope.setWatch = function () {
            // Click event on the AWS region
            $('#region-dropdown').on('click', 'a.aws-region-option', function(){
                localStorage.setItem('aws-region', $(this).attr('id')); 
            });
        };
    })
;
