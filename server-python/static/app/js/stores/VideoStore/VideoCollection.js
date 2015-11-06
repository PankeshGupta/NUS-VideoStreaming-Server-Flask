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

    destroyAll() {
        this.getAll().every(video => video.destroy());
    }
}

module.exports = VideoCollection;