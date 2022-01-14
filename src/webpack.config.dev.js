var path = require("path");
var webpack = require("webpack");

var BundleTracker = require("webpack-bundle-tracker");
var MiniCssExtractPlugin = require("mini-css-extract-plugin");

require("es6-promise").polyfill();

module.exports = {
  mode: "development",
  entry: {
    main: path.resolve(__dirname, "static/src/main.js"),
  },
  output: {
    path: path.resolve("./static/build/"),
    filename: "[name]-[fullhash].js",
    publicPath: "http://localhost:8080/static/",
  },
  plugins: [
    new BundleTracker({
      path: __dirname,
      filename: path.resolve(__dirname, "static/build/stats.json"),
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
  devServer: {
    headers: { "Access-Control-Allow-Origin": "*" },
    allowedHosts: [
      'localhost',
      'annarborultimate.org',
    ],
  },
  devtool: "eval-source-map",
};
