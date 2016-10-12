var path = require('path');
var webpack = require('webpack');

var BundleTracker  = require('webpack-bundle-tracker');
var ExtractTextPlugin = require('extract-text-webpack-plugin');

var autoprefixer = require('autoprefixer');

module.exports = {
  entry: {
    main:[
      'webpack/hot/dev-server',
      'webpack-dev-server/client?http://localhost:8080',
      path.resolve(__dirname, 'static/src/main.js'),
    ],
    forum: path.resolve(__dirname, 'static/src/forum.js'),
  },
  output: {
    path: path.resolve(__dirname, 'static/build'),
    filename: '[name].bundle.js',
    publicPath: 'http://localhost:8080/static/',
  },
  plugins: [
    new BundleTracker({
      path: path.resolve(__dirname, 'static/build'),
      filename: 'stats.json',
    }),
    new webpack.optimize.DedupePlugin(),
    new webpack.optimize.OccurenceOrderPlugin(),
    new webpack.optimize.UglifyJsPlugin({
      compressor: {
        drop_debugger: false,
        warnings: false,
      },
    }),
  ],
  module: {
    loaders: [

      // FONTS
      {
        test: /\.woff(\?v=\d+\.\d+\.\d+)?$/,
        loader: 'url-loader?limit=8192&mimetype=application/font-woff',
        include: [
          path.resolve(__dirname, 'static/src/fonts'),
        ],
      }, {
        test: /\.woff2(\?v=\d+\.\d+\.\d+)?$/,
        loader: 'url-loader?limit=8192&mimetype=application/font-woff',
        include: [
          path.resolve(__dirname, 'static/src/fonts'),
        ],
      }, {
        test: /\.ttf(\?v=\d+\.\d+\.\d+)?$/,
        loader: 'url-loader?limit=8192&mimetype=application/octet-stream',
        include: [
          path.resolve(__dirname, 'static/src/fonts'),
        ],
      }, {
        test: /\.eot(\?v=\d+\.\d+\.\d+)?$/,
        loader: 'url-loader?limit=8192&mimetype=application/vnd.ms-fontobject',
        include: [
          path.resolve(__dirname, 'static/src/fonts'),
        ],
      }, {
        test: /\.otf(\?v=\d+\.\d+\.\d+)?$/,
        loader: 'url-loader?limit=8192&mimetype=image/font-otf',
        include: [
          path.resolve(__dirname, 'static/src/fonts'),
        ],
      }, {
        test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
        loader: 'url-loader?limit=8192&mimetype=image/svg+xml',
        include: [
          path.resolve(__dirname, 'static/src/fonts'),
        ],
      },

      // IMAGES
      {
        test: /\.(ico|jpe?g|png|gif|svg)$/i,
        loaders: [
            'file?hash=sha512&digest=hex&name=images/assets/[name].[ext]',
            'image-webpack?bypassOnDebug&optimizationLevel=7&interlaced=false&progressive=true',
        ],
        include: [
          path.resolve(__dirname, 'static/src/images/assets/'),
        ],
      },
      {
        test: /\.(jpe?g|png|gif|svg)$/i,
        loader: 'url?limit=8192&name=images/includes/[name].[ext]',
        include: [
          path.resolve(__dirname, 'static/src/images/includes'),
        ],
      },

      // STYLES
      {
        test: /\.css$/,
        loader: 'style!css!postcss',
      },
      {
        test: /\.scss$/,
        loader: 'style!css!postcss!sass',
      },
    ]
  },
  postcss: [
    autoprefixer({ browsers: ['last 2 versions'] }),
  ],
};
