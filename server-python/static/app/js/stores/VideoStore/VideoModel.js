var Backbone = require('backbone');
var ServerSettings = require('../ServerSettings');

class VideoModel extends Backbone.Model {

    defaults() {
        return {
            video_id: '',
            title: '',
            created_at: '',
            status: '',
            type: ''
        }
    }


    get idAttribute() {
        return "video_id";
    }

    get url() {
        return ServerSettings.PROTOCOL_HOST_PORT + '/video/' + this.attributes['video_id'];
    }

}

module.exports = VideoModel;