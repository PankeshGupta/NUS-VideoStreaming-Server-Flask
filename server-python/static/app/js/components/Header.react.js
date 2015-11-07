/** @jsx React.DOM */
const React = require('react');
const ReactPropTypes = React.PropTypes;
const VideoActions = require('../actions/VideoActions');

const AppBar = require('material-ui/lib/app-bar');
const Toolbar = require('material-ui/lib/toolbar/toolbar');
const ToolbarGroup = require('material-ui/lib/toolbar/toolbar-group');
const ToolbarSeparator = require('material-ui/lib/toolbar/toolbar-separator');
const ToolbarTitle = require('material-ui/lib/toolbar/toolbar-title');

const RaisedButton = require('material-ui/lib/raised-button');

class Header {

    get propTypes() {
        return {
            videos: ReactPropTypes.object.isRequired
        }
    }

    render() {
        let itemCount = this.props.videos.length;
        let itemsLeftPhrase = itemCount === 1 ? ' Video' : ' Videos';

        /*
         return (
         <footer id="footer">
         <span id="video-count">
         <strong>
         {itemCount}
         </strong>
         {itemsLeftPhrase}
         </span>
         </footer>
         )
         */

        /*
        return (
            <Toolbar>
                <ToolbarGroup key={0} float="left">
                    <ToolbarTitle text={itemCount + " " + itemsLeftPhrase}/>
                </ToolbarGroup>
                <ToolbarGroup key={1} float="right">
                    <ToolbarSeparator/>
                    <RaisedButton label="Refresh" primary={true}/>
                </ToolbarGroup>
            </Toolbar>
        );
        */

        return (
            <AppBar
                title={itemCount + " " + itemsLeftPhrase}/>
        );
    }

    _onDestroyAllClick() {
        VideoActions.destroyAll();
    }
}

module.exports = React.createClass(Header.prototype);