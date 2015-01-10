(function(){
  var app = angular.module('GA',[]);
  app.controller("gaCtrl",['$scope','$http','$interval',function($scope,$http,$interval){
    $scope.items = [];
    $scope.heads = [];

    $scope.draw = function(){
      $http.get('./api/getEvent.php?beta=T').
      success(function(data, status, headers, config) {
        $scope.items = data;
        $scope.heads = [];
        for(var i in $scope.items[0]){
          $scope.heads.push(i);
        }

      }).
      error(function(data, status, headers, config) {
        console.log(data);
        console.log(status);
      });
    };
    $scope.draw();
    $interval(function(){
      $scope.draw();
      console.log(Math.floor(Date.now() / 1000));
    },60000);



  }]);

  //dataCrtl
   app.controller("dataCtrl",['$scope','$http','$interval',function($scope,$http,$interval){
    $scope.items = [];
    $scope.heads = [];

    $scope.draw = function(){
      $http.get('./api/getDataInfo.php?beta=T').
      success(function(data, status, headers, config) {
        $scope.items = data;
        $scope.heads = [];
        for(var i in $scope.items[0]){
          $scope.heads.push(i);
        }

      }).
      error(function(data, status, headers, config) {
        console.log(data);
        console.log(status);
      });
    };
    $scope.draw();
    $interval(function(){
      $scope.draw();
      console.log(Math.floor(Date.now() / 1000));
    },60000);



  }]);


})();
