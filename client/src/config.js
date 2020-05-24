const baseConfig = {};

const devConfig = {
    SERVER_URL: 'http://localhost:5000'
};

const prodConfig = {
    SERVER_URL: 'http://cs.catlin.edu:8021'
};

Object.assign(devConfig, baseConfig);
Object.assign(prodConfig, baseConfig);

export default devConfig;
