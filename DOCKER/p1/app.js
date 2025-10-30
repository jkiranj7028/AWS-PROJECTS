const express = require('express');
const os = require('os');

const app = express();
const PORT = 8080;

app.get('/', (req, res) => {
    console.log(`Request received by container: ${os.hostname()}`);
    res.send(`Hello from a container! My ID is: ${os.hostname()}\n`);
});

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});