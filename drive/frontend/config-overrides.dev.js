var BundleTracker = require('webpack-bundle-tracker');

module.exports = function (config) {
  config
    .plugins
    .push(new BundleTracker({path: "./../", filename: 'webpack-stats.json'}));
  config.output.publicPath = 'http://localhost:3000/'
}
