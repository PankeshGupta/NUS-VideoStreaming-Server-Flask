var AppDispatcher = require('../dispatchers/AppDispatcher');
var VideoConstants = require('../constants/VideoConstants');


class VideoActions {

    /**
     * @param  {string} id
     * @param  {string} text
     */
    updateTitle(video_id, title) {
        AppDispatcher.trigger(VideoConstants.VIDEO_UPDATE_TITLE, {
            video_id: video_id,
            title: title
        });
    }

    destroyAll() {
        AppDispatcher.trigger(VideoConstants.VIDEO_DESTROY_ALL, {});
    }

    /**
     * @param  {string} id
     */
    destroy(video_id) {
        AppDispatcher.trigger(VideoConstants.VIDEO_DESTROY, {
            video_id: video_id
        });
    }
}

module.exports = new VideoActions();