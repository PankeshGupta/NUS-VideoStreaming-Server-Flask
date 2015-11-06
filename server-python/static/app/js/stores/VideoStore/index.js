var AppDispatcher = require('../../dispatchers/AppDispatcher');
var VideoConstants = require('../../constants/VideoConstants');
var MessageActions = require('../../actions/MessageActions');
var VideoCollection = require('./VideoCollection');

var _videoList = new VideoCollection();

// fetch video list from server
// todo add polling here
_videoList.fetch();

AppDispatcher.on('all', function (eventName, payload) {
    switch (eventName) {
        case VideoConstants.VIDEO_DESTROY:
        {
            let id = payload.video_id;
            let model = _videoList.get(id);
            model.destroy({
                wait: true,
                error: function (model, response) {
                    MessageActions.showError(`Error deleting video [${id}]. Details: '${response}'.`);
                }
            });
            break;
        }

        case VideoConstants.VIDEO_UPDATE_TITLE:
        {
            let id = payload.video_id;
            let title = payload.title.trim();
            if (title !== '') {
                let model = _videoList.get(id);
                model.save({title: title}, {
                    wait: true,
                    error: function (model, response) {
                        model.set(model.previousAttributes(), {silent: true});
                        MessageActions.showError(`Error updating video [${id}]. Details: '${response}'.`);
                    }
                });
            }
            break;
        }

        case VideoConstants.VIDEO_DESTROY_ALL:
        {
            _videoList.destroyAll({
                wait: true,
                error: function (model, response) {
                    MessageActions.showError(`Error deleting videos. Details: '${response}'.`);
                }
            });
            break;
        }

        default:
            return;
    }
});

module.exports = _videoList;