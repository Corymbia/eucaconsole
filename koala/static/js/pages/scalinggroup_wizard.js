/**
 * @fileOverview Create Scaling Group wizard page JS
 * @requires AngularJS
 *
 */

// Scaling Group wizard includes the AutoScale Tag Editor
angular.module('ScalingGroupWizard', ['AutoScaleTagEditor'])
    .controller('ScalingGroupWizardCtrl', function ($scope) {
        $scope.form = $('#scalinggroup-wizard-form');
        $scope.healthCheckType = 'EC2';
        $scope.healthCheckPeriod = 120;
        $scope.minSize = 0;
        $scope.desiredCapacity = 1;
        $scope.maxSize = 2;
        $scope.urlParams = $.url().param();
        $scope.launchConfig = '';
        $scope.initChosenSelectors = function () {
            $('#launch_config').chosen({'width': '80%', search_contains: true});
            $('#availability_zones').chosen({'width': '100%', search_contains: true});
        };
        $scope.setLaunchConfig = function () {
            $scope.launchConfig = $scope.urlParams['launch_config'] || '';
        };
        $scope.initController = function () {
            $scope.initChosenSelectors();
            $scope.setLaunchConfig();
        };
        $scope.visitNextStep = function (nextStep, $event) {
            // Trigger form validation before proceeding to next step
            $scope.form.trigger('validate');
            var currentStep = nextStep - 1,
                tabContent = $scope.form.find('#step' + currentStep),
                invalidFields = tabContent.find('[data-invalid]');
            if (invalidFields.length) {
                invalidFields.focus();
                $event.preventDefault();
                return false;
            }
            // If all is well, click the relevant tab to go to next step
            $('#tabStep' + nextStep).click();
        };
        $scope.handleSizeChange = function () {
            // Adjust desired/max based on min size change
            if ($scope.desiredCapacity < $scope.minSize) {
                $scope.desiredCapacity = $scope.minSize;
            }
            if ($scope.maxSize < $scope.desiredCapacity) {
                $scope.maxSize = $scope.desiredCapacity;
            }
        };
    })
;

