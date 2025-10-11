const axios = require('axios');

axios.get('https://my-jenkins-server.com', {
  headers: {
    'bypass-tunnel-reminder': 'true'
  }
}).then(response => {
  console.log(response.data);
});