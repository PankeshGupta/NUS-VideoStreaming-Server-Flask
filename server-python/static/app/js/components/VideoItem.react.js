/** @jsx React.DOM */
var React = require('react');
var ReactPropTypes = React.PropTypes;

var classNames = require('classnames');
var VideoActions = require('../actions/VideoActions');
var VideoTextInput = require('./VideoTextInput.react.js');

class VideoItem {

    getInitialState() {
        return {
            isEditing: false
        };
    }

    get propTypes() {
        return {
            video: ReactPropTypes.object.isRequired,
        }
    }

    render() {

        let video = this.props.video;
        let input;

        if (this.state.isEditing) {
            input = <VideoTextInput className="edit" onSave={this._onSave} value={video.title}/>
        }

        return (
            <li className={classNames({
		          'completed': video.completed,
		          'editing': this.state.isEditing
		        })}

                key={video.video_id}>

                <div className="view">
                    <label>
                        {video.video_id}
                    </label>

                    <label onDoubleClick={this._onDoubleClick}>
                        {video.title}
                    </label>

                    <button className="destroy" onClick={this._onDestroyClick}/>
                </div>

                {input}
            </li>
        )
    }

    _onSave(title) {
        VideoActions.updateTitle(this.props.video.video_id, title);
        this.setState({isEditing: false});
    }

    _onDestroyClick() {
        VideoActions.destroy(this.props.video.video_id);
    }

    _onDoubleClick() {
        this.setState({
            isEditing: true
        });
    }
}

module.exports = React.createClass(VideoItem.prototype);