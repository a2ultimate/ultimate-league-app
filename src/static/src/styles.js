console.log('styles.js');

require.context('./images/assets', true, /\.(jpe?g|png|gif|svg)$/i);

require('normalize.css');

require('bourbon');
require('bourbon-neat');

require('./styles/_app.scss');
