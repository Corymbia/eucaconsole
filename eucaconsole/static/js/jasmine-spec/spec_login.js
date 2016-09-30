/**
 * Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * @fileOverview Jasmine Unittest for Login JS 
 * @requires Jasmine, AngularJS mock
 *
 */

describe("LoginPage", function() {

    beforeEach(angular.mock.module('LoginPage'));

    var scope, ctrl, timeout;
    // inject the $controller and $rootScope services
    // in the beforeEach block
    beforeEach(angular.mock.inject(function($controller, $rootScope, $timeout) {
        // Create a new scope that's a child of the $rootScope
        scope = $rootScope.$new();
        // Create the controller
        ctrl = $controller('LoginPageCtrl', {
            $scope: scope
        });
        timeout = $timeout;
    }));

    beforeEach(function() {
        var template = window.__html__['templates/login.pt'];
        // remove <script src> and <link> tags to avoid phantomJS error
        template = template.replace(/script src/g, "script ignore_src"); 
        template = template.replace(/<link/g, "<ignore_link"); 
        setFixtures(template);
    });

    describe("Initial Values Test", function() {

        it("should have value of showHttpsWarning is false", function() {
            expect(scope.showHttpsWarning).not.toBeTruthy();
        });

        it("should have value of isLoggingIn is false", function() {
            expect(scope.isLoggingIn).not.toBeTruthy();
        });
    });

    describe("Function initController() Test", function() {

        it("Should call prefillForms() when initController() is called", function() {
            spyOn(scope, 'prefillForms');
            scope.initController('{"account": "acct", "username": "user"}');
            expect(scope.prefillForms).toHaveBeenCalled();
        });
    });

    describe("Button enablement logic Test", function() {

        it("should have value of eucaNotValid is true", function() {
            expect(scope.eucaNotValid).toBe(true);
        });

        it("should have value of eucaNotValid is false", function() {
            $("#account").val("blah");
            $("#username").val("blah");
            $("#password").val("blah");
            console.log("account = "+$("#account").val());
            timeout.flush();
            expect(scope.eucaNotValid).toBe(false);
        });

        it("should have value of awsNotValid is true", function() {
            expect(scope.awsNotValid).toBe(true);
        });

        it("should have value of awsNotValid is false", function() {
            $("#access_key").val("blah");
            $("#secret_key").val("blah");
            timeout.flush();
            expect(scope.awsNotValid).toBe(false);
        });

    });
});
