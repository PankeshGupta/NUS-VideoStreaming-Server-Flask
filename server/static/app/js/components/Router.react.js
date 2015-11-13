/** @jsx React.DOM */
const React = require('react');
const Routes = require('react-router').Routes;
const Route = require('react-router').Route;

const App  = require('./App.react');
const Home = require('./Home.react');
const About = require('./About.react');

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