/** @jsx React.DOM */
const React = require('react');
const ReactDOM = require('react-dom');
const VideoApp = require('./components/VideoApp.react.js');

// for material-ui
const injectTapEventPlugin = require("react-tap-event-plugin");
injectTapEventPlugin();

ReactDOM.render(<VideoApp />, document.getElementById('videoapp'));