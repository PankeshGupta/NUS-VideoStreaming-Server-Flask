var AppDispatcher = require('../dispatchers/AppDispatcher');
var MessageConstants = require('../constants/MessageConstants');

class MessageActions {

    showInfo(text) {
        AppDispatcher.trigger(MessageConstants.INFO_MESSAGE, {
            text: text
        });
    }

    showWarning(text) {
        AppDispatcher.trigger(MessageConstants.WARNING_MESSAGE, {
            text: text
        });
    }

    showError(text) {
        AppDispatcher.trigger(MessageConstants.ERROR_MESSAGE, {
            text: text
        });
    }
}

module.exports = new MessageActions();