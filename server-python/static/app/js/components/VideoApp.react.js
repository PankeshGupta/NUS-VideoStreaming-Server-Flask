/** @jsx React.DOM */
const React = require('react');
const VideoStore = require('../stores/VideoStore');
const VideoList = require('./VideoList.react.js');
const Header = require('./Header.react.js');


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