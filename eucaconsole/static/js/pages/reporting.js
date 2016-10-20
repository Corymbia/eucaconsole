/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview ElasticIP Detail Page JS
 * @requires AngularJS
 *
 */

angular.module('ReportingPage', ['ngRoute'])
.directive('navigation', function () {
    return {
        restrict: 'A',
        link: function (scope, element, attrs, ctrl) {
             ctrl.setInitialTab(attrs.reportingConfigured);
        },
        controller: ['$scope', '$location', function ($scope, $location) {
            this.isTabActive = function(name) {
                var path = $location.path();
                if (path.indexOf(name) > -1)
                    return 'active';
                if (name === 'dashboard' &&
                    ['reports', 'preferences'].every(function(val) { return path.indexOf(val) === -1; }) )
                    return 'active';
                return '';
            };
            this.setInitialTab = function(reportingConfigured) {
                if (reportingConfigured !== 'true') {
                    $location.path('/reporting/preferences');
                }
            };
        }],
        controllerAs: 'nav'
    };
})
.controller('DashboardController', ['$scope', '$routeParams', function ($scope, $routeParams) {
    console.log('dashboard');
}])
.controller('ReportsController', ['$scope', '$routeParams', function ($scope, $routeParams) {
    console.log('reports');
}])
.controller('PreferencesController', ['$scope', '$routeParams', function ($scope, $routeParams) {
    console.log('preferences');
}])
.config(function ($routeProvider, $locationProvider) {
    $routeProvider
        .when('/reporting/reports', {
            templateUrl: '/_template/reporting/reporting_reports',
            controller: 'ReportsController',
            controllerAs: 'reports'
        })
        .when('/reporting/preferences', {
            templateUrl: '/_template/reporting/reporting_preferences',
            controller: 'PreferencesController',
            controllerAs: 'preferences'
        })
        .otherwise({
            templateUrl: '/_template/reporting/reporting_dashboard',
            controller: 'DashboardController',
            controllerAs: 'dashboard',
        });

    $locationProvider.html5Mode(true);
});

