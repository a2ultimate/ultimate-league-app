var path = require("path");
var webpack = require("webpack");

var BundleTracker = require("webpack-bundle-tracker");
var MiniCssExtractPlugin = require("mini-css-extract-plugin");

require("es6-promise").polyfill();

module.exports = {
  mode: "development",
  entry: {
    main: path.resolve(__dirname, "src/main.js"),
  },
  output: {
    path: path.resolve("./build/"),
    filename: "[name]-[fullhash].js",
    publicPath: "http://localhost:8080/static/",
  },
  plugins: [
    new BundleTracker({
      path: __dirname,
      filename: path.resolve(__dirname, "build/stats.json"),
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
    allowedHosts: ["localhost", "annarborultimate.org"],
  },
  devtool: "eval-source-map",
};
