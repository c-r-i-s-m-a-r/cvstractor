import { useMemo, useState } from 'react'
import { extraerCv } from './api/extract.js'
import {
  cargarHistorial,
  guardarEntrada,
  eliminarEntrada,
  vaciarHistorial,
} from './storage/history.js'
import { contiene } from './search.js'
import UploadForm from './components/UploadForm.jsx'
import SearchBar from './components/SearchBar.jsx'
import ResultsCard from './components/ResultsCard.jsx'
import HistoryList from './components/HistoryList.jsx'

export default function App() {
  const [archivo, setArchivo] = useState(null)
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState('')
  const [resultado, setResultado] = useState(null)
  const [nombreArchivo, setNombreArchivo] = useState('')
  const [consulta, setConsulta] = useState('')
  const [historial, setHistorial] = useState(cargarHistorial)

  async function manejarExtraccion(file) {
    setCargando(true)
    setError('')
    try {
      const datos = await extraerCv(file)
      setResultado(datos)
      setNombreArchivo(file.name)
      setHistorial(
        guardarEntrada({
          id: crypto.randomUUID(),
          nombre: file.name,
          fecha: new Date().toISOString(),
          data: datos,
        })
      )
    } catch (e) {
      setError(e.message || 'Error desconocido al procesar el archivo')
    } finally {
      setCargando(false)
    }
  }

  function abrirEntrada(entrada) {
    setResultado(entrada.data)
    setNombreArchivo(entrada.nombre)
    setError('')
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const historialFiltrado = useMemo(() => {
    const q = consulta.trim().toLowerCase()
    if (!q) return historial
    return historial.filter(
      (e) => contiene(e.data, q) || e.nombre.toLowerCase().includes(q)
    )
  }, [historial, consulta])

  return (
    <div className="app">
      <header className="cabecera">
        <h1>CVstractor</h1>
        <p>Extrae datos estructurados de currículums .docx y .odt</p>
      </header>

      <div className="contenedor">
        <main className="principal">
          <UploadForm
            archivo={archivo}
            setArchivo={setArchivo}
            onExtract={manejarExtraccion}
            cargando={cargando}
          />

          {error && (
            <div className="error" role="alert">
              {error}
            </div>
          )}

          <SearchBar consulta={consulta} onCambio={setConsulta} />

          {cargando && <p className="estado">Procesando el documento…</p>}

          {resultado && !cargando && (
            <ResultsCard
              datos={resultado}
              consulta={consulta}
              nombreArchivo={nombreArchivo}
            />
          )}

          {!resultado && !error && !cargando && (
            <p className="vacio">Sube un currículum para comenzar.</p>
          )}
        </main>

        <aside className="lateral">
          <div className="historial-cabecera">
            <h2>Historial</h2>
            {historial.length > 0 && (
              <button
                type="button"
                className="boton-secundario"
                onClick={() => setHistorial(vaciarHistorial())}
              >
                Vaciar
              </button>
            )}
          </div>
          <HistoryList
            entradas={historialFiltrado}
            onAbrir={abrirEntrada}
            onEliminar={(id) => setHistorial(eliminarEntrada(id))}
            consulta={consulta.trim()}
          />
        </aside>
      </div>
    </div>
  )
}
