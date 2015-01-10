(function(){
  var app = angular.module('GA',[]);

  app.controller("impCtrl",['$scope','$http','$interval','$filter',function($scope,$http,$interval,$filter){
    //Begin of impCtrl
    $scope.events = [];
    $scope.s = null;
    $scope.draw = function(){
      $http.get('./api/getImpEvent.php?beta=T&limit=3').
      success(function(data, status, headers, config) {
        $scope.events = data["data"];
      }).
      error(function(data, status, headers, config) {
        console.log(data);
        console.log(status);
      });
    };
    $scope.draw();
    //5 min refresh
    $interval(function(){
      $scope.draw();
      console.log("udpate: "+Math.floor(Date.now() / 1000));
    },300000);

    //End of impCtrl
  }]);





  app.controller("gaCtrl",['$scope','$http','$interval','$filter',function($scope,$http,$interval,$filter){
    $scope.items = [];
    $scope.heads = [];
    $scope.sources=[];
    $scope.s = null;
    $scope.draw = function(){
      $http.get('./api/getEvent_2.php?beta=T').
      success(function(data, status, headers, config) {
        $scope.items = data["data"];
        $scope.heads = [];
        //$scope.types = data["type"];
        $scope.sources=data["sources"];
        if ($scope.s==null){
          $scope.setSource($scope.sources[0]);
        }
        for(var i in $scope.items[0]){
//          if(i!="s"){
            $scope.heads.push(i);
//          }

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
    $scope.draw();
    $scope.setSource=function(s){
      $scope.s = s;
      $scope.filtered_items = $filter('filter')($scope.items, function(value,i){ return value.s == s }, true);
    }

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
    $scope.draw();


  }]);


})();
