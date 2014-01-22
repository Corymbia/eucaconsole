/**
 * @fileOverview Volumes landing page JS
 * @requires AngularJS, jQuery
 *
 */

angular.module('VolumesPage', ['CustomFilters'])
    .controller('VolumesCtrl', function ($scope) {
        $scope.volumeID = '';
        $scope.volumeZone = '';
        $scope.instancesByZone = '';
        $scope.urlParams = $.url().param();
        $scope.displayType = $scope.urlParams['display'] || 'gridview';
        $scope.initPage = function (instancesByZone) {
            $scope.instancesByZone = instancesByZone;
        };
        $scope.revealModal = function (action, volume) {
            var modal = $('#' + action + '-volume-modal'),
                volumeZone = volume['zone'];
            $scope.volumeID = volume['id'];
            if (action === 'attach') {
                // Set instance choices for attach to instance widget
                modal.on('open', function() {
                    var instanceSelect = $('#instance_id'),
                        instances = $scope.instancesByZone[volumeZone],
                        options = '';
                    if (instances === undefined) {
                        options = "<option value=''>No available instances in the same availability zone</option>";
                    }
                    else {
                      instances.forEach(function (instance) {
                          options += '<option value="' + instance['id'] + '">' + instance['name'] + '</option>';
                      });
                    }
                    instanceSelect.html(options);
                    instanceSelect.trigger('chosen:updated');
                    instanceSelect.chosen({'width': '75%', search_contains: true});
                });
            }
            modal.foundation('reveal', 'open');
        };
    })
    .controller('ItemsCtrl', function ($scope, $http, $timeout) {
        $scope.items = [];
        $scope.unfilteredItems = [];
        $scope.sortBy = '';
        $scope.jsonEndpoint = '';
        $scope.searchFilter = '';
        $scope.itemsLoading = true;
        $scope.setInitialSort = function (sortKey) {
            $scope.sortBy = sortKey;
        };
        $scope.initController = function (sortKey, jsonItemsEndpoint) {
            $scope.jsonEndpoint = jsonItemsEndpoint;
            $scope.setInitialSort(sortKey);
            $scope.getItems();
        };
        $scope.getItems = function () {
            $http.get($scope.jsonEndpoint).success(function(oData) {
                var results = oData ? oData.results : [];
                var transitionalCount = 0;
                $scope.itemsLoading = false;
                $scope.items = results;
                $scope.unfilteredItems = results;
                $scope.items.forEach(function (item) {
                    if (item['transitional']) {
                        transitionalCount += 1;
                    }
                });
                // Auto-refresh volumes if any of them are in progress
                if (transitionalCount > 0) {
                    $timeout(function() { $scope.getItems(); }, 5000);  // Poll every 5 seconds
                }
            });
        };
        /*  Filter items client side based on search criteria.
         *  @param {array} filterProps Array of properties to filter items on
         */
        $scope.searchFilterItems = function(filterProps) {
            $scope.items = $scope.unfilteredItems;  // reset prior to applying filter
            var filterText = ($scope.searchFilter || '').toLowerCase();
            // Leverage Array.prototype.filter (ECMAScript 5)
            var filteredItems = $scope.items.filter(function(item) {
                for (var i=0; i < filterProps.length; i++) {  // Can't use $.each or Array.prototype.forEach here
                    var propName = filterProps[i];
                    var itemProp = item.hasOwnProperty(propName) && item[propName];
                    if (itemProp && typeof itemProp === "string" && itemProp.toLowerCase().indexOf(filterText) !== -1) {
                        return item;
                    }
                }
            });
            $scope.items = filterText ? filteredItems : $scope.unfilteredItems;
        };
    })
;

