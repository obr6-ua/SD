const { defineConfig } = require('@vue/cli-service');
module.exports = defineConfig({
  transpileDependencies: true,
  pages: {
    index: {
      // punto de entrada para la página
      entry: 'src/main.js',
      // la fuente de la plantilla
      template: 'public/index.html',
      // salida de la plantilla
      filename: 'index.html',
      // cuando se usa la opción title, inyecta el título en la plantilla
      // usando las opciones de htmlWebpackPlugin.options.title
      title: 'ART WITH DRONES',
    },
  }
})
