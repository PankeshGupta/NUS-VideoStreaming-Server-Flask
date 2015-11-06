var Backbone = require('backbone');
var VideoModel = require('./VideoModel');
var ServerSettings = require('../ServerSettings');

class VideoCollection extends Backbone.Collection {

    get model() {
        return VideoModel;
    }

    get url() {
        return ServerSettings.PROTOCOL_HOST_PORT + '/videos';
    }

    getAll() {
        return this;
    }

    destroyAll(options) {
        this.getAll().every(video => video.destroy(options));
    }
}

module.exports = VideoCollection;