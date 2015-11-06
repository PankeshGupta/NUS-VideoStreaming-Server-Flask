/** @jsx React.DOM */
var React = require('react');
var Routes = require('react-router').Routes;
var Route = require('react-router').Route;

var App  = require('./App.react');
var Home = require('./Home.react');
var About = require('./About.react');

class Router {
	render () {
		return (
			<Routes>
				<Route handler={App}>
					<Route name="home" path="/" handler={Home} />
					<Route name="about" path="/about" handler={About}/>
				</Route>
			</Routes>
		)
	}
}

module.exports = React.createClass(Router.prototype);