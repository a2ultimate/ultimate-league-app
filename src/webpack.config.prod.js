var path = require("path");
var webpack = require("webpack");

var BundleTracker = require("webpack-bundle-tracker");
var MiniCssExtractPlugin = require("mini-css-extract-plugin");

require("es6-promise").polyfill();

module.exports = {
  mode: "production",
  entry: {
    main: path.resolve(__dirname, "static/src/main.js"),
  },
  output: {
    path: path.resolve(__dirname, "static/build"),
    filename: "[name].[chunkhash].js",
  },
  plugins: [
    new BundleTracker({
      path: path.resolve(__dirname, "static/build"),
      filename: "stats.json",
    }),
  ],
  module: {
    rules: [
      // FONTS
      {
        test: /\.woff(\?v=\d+\.\d+\.\d+)?$/,
        type: "asset/inline",
      },
      {
        test: /\.woff2(\?v=\d+\.\d+\.\d+)?$/,
        type: "asset/inline",
      },
      {
        test: /\.ttf(\?v=\d+\.\d+\.\d+)?$/,
        type: "asset/inline",
      },
      {
        test: /\.eot(\?v=\d+\.\d+\.\d+)?$/,
        type: "asset/inline",
      },
      {
        test: /\.otf(\?v=\d+\.\d+\.\d+)?$/,
        type: "asset/inline",
      },
      {
        test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,

        type: "asset/resource",
      },

      // IMAGES
      {
        test: /\.(ico|jpe?g|png|gif|svg)$/i,
        type: "asset/resource",
        generator: {
          filename: "images/[name][ext]",
        },
      },

      // STYLES
      {
        test: /\.css$/,
        use: ["style-loader", "css-loader", "postcss-loader"],
      },
      {
        test: /\.scss$/,
        use: ["style-loader", "css-loader", "postcss-loader", "sass-loader"],
      },

      // MISC
      {
        test: /\.xml$/,
        type: "asset/resource",
      },
    ],
  },
  devtool: "source-map",
};
