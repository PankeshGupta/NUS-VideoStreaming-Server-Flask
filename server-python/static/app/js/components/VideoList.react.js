/** @jsx React.DOM */
var React = require('react');
var ReactPropTypes = React.PropTypes;

var VideoActions = require('../actions/VideoActions');
var VideoItem = require('./VideoItem.react.js');

class VideoList {

    get propTypes() {
        return {
            videos: ReactPropTypes.object.isRequired,
        }
    }

    render() {

        let videos = this.props.videos.toJSON().map((video) => {
            return <VideoItem key={video.video_id} video={video}/>
        });

        return (
            <section id="main">
                <ul id="video-list">
                    {videos}
                </ul>
            </section>
        )
    }
}

module.exports = React.createClass(VideoList.prototype);