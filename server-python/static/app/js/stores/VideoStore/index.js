var AppDispatcher = require('../../dispatchers/AppDispatcher');
var VideoConstants = require('../../constants/VideoConstants');
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
            _videoList.get(id).destroy();
            break;
        }

        case VideoConstants.VIDEO_UPDATE_TITLE:
        {
            let id = payload.video_id;
            let title = payload.title.trim();
            if (title !== '') {
                _videoList.get(id).save({title: title});
            }
            break;
        }

        case VideoConstants.VIDEO_DESTROY_ALL:
        {
            _videoList.destroyAll();
            break;
        }

        default:
            return;
    }
});

module.exports = _videoList;