/** @jsx React.DOM */
var React = require('react');
var VideoStore = require('../stores/VideoStore');
var VideoList = require('./VideoList.react.js');
var Header = require('./Header.react.js');


function getAppState() {
    return {
        allVideos: VideoStore.getAll()
    };
}


class VideoApp {

    getInitialState() {
        return getAppState();
    }

    componentDidMount() {
        VideoStore.on('all', this._onChange);
    }

    componentWillUnmount() {
        VideoStore.off('all', this._onChange);
    }

    _onChange() {
        this.setState(getAppState());
    }

    render() {
        return (
            <div>
                <Header videos={this.state.allVideos}/>
                <VideoList videos={this.state.allVideos}/>
            </div>
        )
    }
}

module.exports = React.createClass(VideoApp.prototype);