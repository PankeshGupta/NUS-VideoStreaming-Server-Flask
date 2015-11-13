module.exports = {
    entry: './app/js/main.js',
    output: {
        filename: 'app/js/bundle.js'
    },
    module: {
        loaders: [
            { test: /\.js$/, loader: 'es6-loader!jsx-loader' } // loaders can take parameters as a querystring
        ]
    }
};