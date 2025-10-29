module.exports = {
  presets: [
    ['@babel/preset-env', {
      targets: {
        node: '18'
      }
    }]
  ],
  plugins: [],
  env: {
    test: {
      plugins: [
        '@babel/plugin-transform-modules-commonjs'
      ]
    }
  }
};



