/** @jsx React.DOM */
const React = require('react');
const ReactPropTypes = React.PropTypes;
const merge = require('merge');

const VideoActions = require('../actions/VideoActions');
const VideoTextInput = require('./VideoTextInput.react.js');

const Avatar = require('material-ui/lib/avatar');
const Colors = require('material-ui/lib/styles/colors');
const Card = require('material-ui/lib/card/card');
const CardHeader = require('material-ui/lib/card/card-header');
const CardActions = require('material-ui/lib/card/card-actions');
const CardText = require('material-ui/lib/card/card-text');
const FlatButton = require('material-ui/lib/flat-button');
const RaisedButton = require('material-ui/lib/raised-button');
const TextField = require('material-ui/lib/text-field');
const Paper = require('material-ui/lib/paper');

class VideoItem {

    getInitialState() {
        return {
            isEditing: false
        };
    }

    static get propTypes() {
        return {
            video: ReactPropTypes.object.isRequired,
        }
    }

    render() {

        let video = this.props.video;
        let nonEditingStyle = {};
        let editingStyle = {};

        if (this.state.isEditing) {
            nonEditingStyle.display = 'none';
            editingStyle.display = 'block';
        } else {
            nonEditingStyle.display = 'block';
            editingStyle.display = 'none';
        }

        return (
            <Card style={{width: '80%', margin: '20px auto'}}>

                <CardHeader
                    style={nonEditingStyle}
                    title={video.title}
                    subtitle={"[" + video.video_id + "] " + video.created_at}
                    avatar={
                        <Avatar color={Colors.teal50} backgroundColor={Colors.teal800}>V</Avatar>
                    }
                    onDoubleClick={this._onEditClick}/>

                <div style={merge({margin: '0 20px'}, editingStyle)}>
                    <TextField
                        ref="titleText"
                        hintText="Example: NUS Hackathon"
                        floatingLabelText="Enter a new title"
                        onEnterKeyDown={this._onTitleTextFinished}/>

                    <RaisedButton style={{margin: '0 20px'}} label="Save" primary={true} onTouchTap={this._onTitleTextFinished}/>
                    <RaisedButton style={{margin: '0'}} label="Cancel" onTouchTap={this._onTitleTextCanceled}/>
                </div>

                <CardText expandable={false}>
                    Information about the segments
                </CardText>

                <CardActions float="right" expandable={false}>
                    <FlatButton label="Delete" primary={true} onTouchTap={this._onDestroyClick}/>
                </CardActions>
            </Card>
        );
    }

    _onTitleTextFinished() {
        if (!this.state.isEditing) {
            return;
        }

        let titleText = this.refs.titleText;
        let title = titleText.getValue().trim();
        titleText.setValue(title);

        if (title !== '' && this.props.video.title !== title) {
            VideoActions.updateTitle(this.props.video.video_id, title);
        }

        this.state.isEditing = false;
        this.forceUpdate();
    }

    _onTitleTextCanceled() {
        if (!this.state.isEditing) {
            return;
        }

        this.state.isEditing = false;
        this.forceUpdate();
    }

    _onEditClick() {
        this.state.isEditing = true;

        let titleText = this.refs.titleText;
        titleText.setValue(this.props.video.title);
        titleText.focus();

        this.forceUpdate();
    }

    _onDestroyClick() {
        VideoActions.destroy(this.props.video.video_id);
    }
}

module.exports = React.createClass(VideoItem.prototype);