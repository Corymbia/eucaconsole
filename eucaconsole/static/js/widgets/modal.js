angular.module('ModalModule', [])
.directive('modal', ['ModalService', function (ModalService) {
    var template = '<div class="modal-bg"></div><div class="modal-content"><a class="close-modal">×</a><ng-transclude></ng-transclude></div>';
    return {
        restrict: 'A',
        transclude: true,
        compile: function(tElem, tAttrs) {
            tElem.append(template);
            return function (scope, element, attrs) {
                element.find('.close-modal').attr('ng-click', 'closeModal(\''+attrs.modal+'\')')
                ModalService.registerModal(attrs.modal, element);
            };
        },
        controller: ['$scope', function ($scope) {
            $scope.closeModal = function (name) {
                ModalService.closeModal(name);
            };
        }]
    };
}])
.factory('ModalService', ['$rootScope', function ($rootScope) {
    var _modals = {};

    function registerModal (name, element) {
        if(name in _modals) {
            console.error('Modal with name ', name, ' already registered.');
            return;
        }
        _modals[name] = element;
    }

    function openModal (name) {
        var modal = _modals[name];
        if(!modal) {
            return;
        }

        modal.addClass('open');
    }

    function closeModal (name) {
        var modal = _modals[name];
        if(!modal) {
            return;
        }

        modal.removeClass('open');
        $rootScope.$broadcast('modal:close', name);
    }

    return {
        openModal: openModal,
        closeModal: closeModal,
        registerModal: registerModal
    };
}]);
