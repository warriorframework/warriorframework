/*
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

*/

//==========================================================================
// DISCLAIMER OF WARRANTY
// This source code is provided "as is" and without any express or implied
// warranties as to performance, fitness for purpose, or merchantability.
// The author or distributors of this source code may have made statements
// about this source code. Any such statements do not constitute warranties.
// The user is advised to test the source code thoroughly before relying on
// it. The user assumes the entire risk of using the source code.
//
// History:
//  05/15/2015 - Version 0.9
//==========================================================================
angular.module('chariot').directive('modal', function () {
   return {
      template: '<div class="modal fade">' +
         '<div class="modal-dialog">' +
            '<div class="modal-content">' +
               '<div class="modal-header">' +
                  '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>' +
                  '<h4 class="modal-title">{{ title }}</h4>' +
               '</div>' +
            '<div class="modal-body" ng-transclude></div>' +
         '</div>' +
         '</div>' +
         '</div>',
      restrict: 'E',
      transclude: true,
      replace:true,
      scope:{
          title: '@',
          showModal: '='
      },
      link: function postLink(scope, element, attrs) {
         if( typeof( scope.showModal.visible ) === "undefined" ) {
              scope.showModal.visible = false;
         }
         scope.$watch('showModal.visible', function(value){
            if(value == true)
               $(element).modal('show');
            else
               $(element).modal('hide');
         });

         $(element).on('shown.bs.modal', function(){
            scope.$apply(function(){
               scope.showModal.visible = true;
            });
         });

         $(element).on('hidden.bs.modal', function(){
            scope.$apply(function(){
               scope.showModal.visible = false;
            });
         });
      }
   };
});