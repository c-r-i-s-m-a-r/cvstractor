const express = require('express');
const fileupload = require('express-fileupload');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
app.use(fileupload());
app.use(express.json());

app.get('/api/up', (req, res) => {
    res.status(200)
    res.send('Servidor arriba')
})

app.post('/api/extract', (req, res) => {
  if (!req.files || Object.keys(req.files).length === 0) {
    return res.status(400).json({ error: 'No se recibieron archivos' });
  }

  const archivo = req.files.cv;
  if (!archivo.name.endsWith('.docx') && !archivo.name.endsWith('.odt')) {
    return res.status(400).json({ error: 'Formato de documento no soportado' });
  }

  const tempPath = path.join('/tmp', `${Date.now()}_${archivo.name}`);
  const pythonScript = path.resolve('python/extractor.py');

  try {
    archivo.mv(tempPath, (err) => {
      if (err) {
        return res.status(500).json({ error: 'Error al guardar archivo temporal' });
      }

      const python = spawn('python3', [pythonScript, tempPath]);

      let resultado = '';
      python.stdout.on('data', (data) => {
        resultado += data.toString();
      });

      python.stderr.on('data', (data) => {
        console.error('Python error:', data.toString());
      });

      python.on('close', (code) => {
        try {
          fs.unlinkSync(tempPath);
        } catch (e) {
          // Ignore cleanup errors
        }

        if (code === 0) {
          try {
            const datos = JSON.parse(resultado.trim());
            res.json(datos);
          } catch (e) {
            res.status(500).json({ error: 'Error parsing Python output', detail: resultado });
          }
        } else {
          res.status(500).json({ error: 'Error en el procesamiento Python', code });
        }
      });
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Servidor corriendo en puerto ${PORT}`);
});