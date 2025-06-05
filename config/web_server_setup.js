   const express = require('express');
   const path = require('path');
   const app = express();

   // Puerto asignado por Render o por defecto en desarrollo
   const PORT = process.env.PORT || 3000;

   // Servir la carpeta de archivos estáticos
   app.use(express.static(path.join(__dirname, 'public')));

   // Ruta principal que devuelve el HTML
   app.get('/', (req, res) => {
       res.sendFile(path.join(__dirname, 'public', 'index.html'));
   });

   // Escuchar en el puerto configurado
   app.listen(PORT, () => {
       console.log(`Servidor corriendo en el puerto ${PORT}`);
   });