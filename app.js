'use strict';

angular.module('remoteControl', ['ngMaterial'])
    .service('WSService', function() {
	var ws = new WebSocket('ws://10.25.4.63:8000');
	ws.onmessage = function(e) { console.log(e)};
	
	return {
	    send: function(data) {
		ws.send(JSON.stringify(data));
	    }
	}
    })
    .directive('touchZone', function() {
	var hammer;
	function link(scope, elements) {
	    hammer = new Hammer(elements[0]);
	    hammer.on('pan', function(event) { console.log('pan', event)});
	    hammer.on('swipe', function() { console.log('swipe')});
	    hammer.on('tap', function(event) { console.log('tap', event)});
	    hammer.on('doubletap', function() { console.log('doubletap')});
	    hammer.on('pinch', function() { console.log('pinch')});
	    hammer.on('rotate', function() { console.log('rotate')});
	};
	return {
	    restrict: 'A',
	    link: link
	}
    })
    .controller('WSController', function($scope, WSService) {
	$scope.key = function(keys) {
	    var msg = {key: {keys: keys}};
	    WSService.send(msg);
	};
	$scope.click = function(button) {
	    button = button ? button : 1
	    var msg = {click: {button: button}};
	    WSService.send(msg);
	};
    });
