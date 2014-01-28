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
        $http.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $scope.items = [];
        $scope.unfilteredItems = [];
        $scope.sortBy = '';
        $scope.sortReverse = false;
        $scope.landingPageView = "tableview";
        $scope.jsonEndpoint = '';
        $scope.searchFilter = '';
        $scope.itemsLoading = true;
        $scope.pageResource = '';
        $scope.sortByKey = '';
        $scope.sortReverseKey = '';
        $scope.landingPageViewKey = '';
        $scope.initController = function (pageResource, sortKey, jsonItemsEndpoint) {
            $scope.jsonEndpoint = jsonItemsEndpoint;
            $scope.initLocalStorageKeys(pageResource);
            $scope.setInitialSort(sortKey);
            $scope.setWatch();
            $scope.getItems();
        };
        $scope.initLocalStorageKeys = function (pageResource){
            $scope.pageResource = pageResource;
            $scope.sortByKey = $scope.pageResource + "-sortBy";
            $scope.sortReverseKey = $scope.pageResource + "-sortReverse";
            $scope.landingPageViewKey = $scope.pageResource + "-landingPageView";
        };
        $scope.setInitialSort = function (sortKey) {
            var storedSort = localStorage.getItem($scope.sortByKey),
                storedSortReverse = localStorage.getItem($scope.sortReverseKey),
                storedLandingPageView = localStorage.getItem($scope.landingPageViewKey);
            $scope.sortBy = storedSort || sortKey;
            $scope.sortReverse = storedSortReverse == null ? false : (storedSortReverse === 'true');
            $scope.landingPageView = storedLandingPageView == null ? "tableview" : storedLandingPageView;
        };
        $scope.setWatch = function () {
            var sortingDropdown = $('#sorting-dropdown'),
                sortingReverse = $('#sorting-reverse');
            $scope.$watch('sortBy',  function () {
                if (sortingDropdown.hasClass('open')) {
                    sortingDropdown.removeClass('open');
                    sortingDropdown.removeAttr('style');
                }
                // Set sortBy in localStorage
                localStorage.setItem($scope.sortByKey, $scope.sortBy);
            });
            $scope.$watch('sortReverse', function(){
                if ($scope.sortReverse == true) {
                    sortingReverse.removeClass('down-caret');
                    sortingReverse.addClass('up-caret');
                } else {
                    sortingReverse.removeClass('up-caret');
                    sortingReverse.addClass('down-caret');
                }
                // Set SortReverse in localStorage
                localStorage.setItem($scope.sortReverseKey, $scope.sortReverse);
            });
            $scope.$watch('landingPageView', function () {
                var gridviewBtn = $('#gridview-button'),
                    tableviewBtn = $('#tableview-button');
               if ($scope.landingPageView == 'gridview') {
                   gridviewBtn.addClass("selected");
                   tableviewBtn.removeClass("selected");
               } else {
                   tableviewBtn.addClass("selected");
                   gridviewBtn.removeClass("selected");
               }
               // Set landingPageView in localStorage
               localStorage.setItem($scope.landingPageViewKey, $scope.landingPageView);
            }); 
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
            }).error(function (oData, status) {
                var errorMsg = oData['error'] || null;
                if (errorMsg && status === 403) {
                    alert(errorMsg);
                    $('#euca-logout-form').submit();
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
        $scope.reverseSort = function(){
           $scope.sortReverse = !$scope.sortReverse
        };
        $scope.switchView = function(view){
            $scope.landingPageView = view;
        };
    })
;

