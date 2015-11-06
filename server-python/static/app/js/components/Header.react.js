/** @jsx React.DOM */
var React = require('react');
var ReactPropTypes = React.PropTypes;
var VideoActions = require('../actions/VideoActions');

class Header {

    get propTypes() {
        return {
            videos: ReactPropTypes.object.isRequired
        }
    }

    render() {
        let itemCount = this.props.videos.length;
        let itemsLeftPhrase = itemCount === 1 ? ' video' : ' videos';

        return (
            <footer id="footer">
				<span id="video-count">
					<strong>
                        {itemCount}
                    </strong>
                    {itemsLeftPhrase}
				</span>
                <button id="destroy-all" onClick={this._onDestroyAllClick}>
                    Delete All
                </button>
            </footer>
        )
    }

    _onDestroyAllClick() {
        VideoActions.destroyAll();
    }
}

module.exports = React.createClass(Header.prototype);