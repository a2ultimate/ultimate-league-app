var path = require("path");
var webpack = require("webpack");

var BundleTracker = require("webpack-bundle-tracker");
var MiniCssExtractPlugin = require("mini-css-extract-plugin");

require("es6-promise").polyfill();

module.exports = {
  mode: "production",
  entry: {
    main: path.resolve(__dirname, "src/main.js"),
  },
  output: {
    path: path.resolve(__dirname, "build"),
    filename: "[name].[chunkhash].js",
  },
  plugins: [
    new BundleTracker({
      path: __dirname,
      filename: path.resolve(__dirname, "build/stats.json"),
    }),
    new MiniCssExtractPlugin({
      filename: "[name].[chunkhash].css",
    }),
  ],
  module: {
    rules: [
      // FONTS
      {
        test: /\.(woff|woff2|eot|ttf|otf|svg)$/i,
        type: "asset",
        parser: {
          dataUrlCondition: {
            maxSize: 4 * 1024, // 4kb
          },
        },
        generator: {
          filename: "fonts/[name]-[contenthash][ext]",
        },
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
        use: [MiniCssExtractPlugin.loader, "css-loader", "postcss-loader"],
      },
      {
        test: /\.scss$/,
        use: [
          MiniCssExtractPlugin.loader,
          "css-loader",
          "postcss-loader",
          "sass-loader",
        ],
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
