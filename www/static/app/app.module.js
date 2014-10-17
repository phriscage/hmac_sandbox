var app = angular.module('myApp', []);

// required if using the jinja2 syntax to avoid overlap from interpreted vars
//app.config(['$interpolateProvider', function($interpolateProvider) {
  //$interpolateProvider.startSymbol('{[');
  //$interpolateProvider.endSymbol(']}');
//}]);

app.controller("TestController", function($scope){
    $scope.understand = "I now understand how the scope works!";
    $scope.people = [
        {
            id: 0,
            name: 'Leon',
            music: [
                'Rock',
                'Metal',
                'Dubstep',
                'Electro'
            ],
            live: true
        },
        {
            id: 1,
            name: 'Chris',
            music: [
                'Indie',
                'Drumstep',
                'Dubstep',
                'Electro'
            ],
            live: true
        },
        {
            id: 2,
            name: 'Harry',
            music: [
                'Rock',
                'Metal',
                'Thrash Metal',
                'Heavy Metal'
            ],
            live: false
        },
        {
            id: 3,
            name: 'Allyce',
            music: [
                'Pop',
                'RnB',
                'Hip Hop'
            ],
            live: true
        }
    ];
});

