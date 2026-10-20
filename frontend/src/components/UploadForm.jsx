import { useRef, useState } from 'react'

const TAMANO_MAXIMO = 10 * 1024 * 1024

function validar(file) {
  if (!file) return 'No se seleccionó ningún archivo'
  if (!/\.(docx|odt)$/i.test(file.name)) {
    return 'Formato no soportado: solo se aceptan archivos .docx o .odt'
  }
  if (file.size > TAMANO_MAXIMO) return 'El archivo supera los 10 MB'
  return ''
}

export default function UploadForm({ archivo, setArchivo, onExtract, cargando }) {
  const [arrastrando, setArrastrando] = useState(false)
  const [aviso, setAviso] = useState('')
  const inputRef = useRef(null)

  function seleccionar(file) {
    const error = validar(file)
    setAviso(error)
    setArchivo(error ? null : file)
  }

  function soltar(evento) {
    evento.preventDefault()
    setArrastrando(false)
    const file = evento.dataTransfer.files && evento.dataTransfer.files[0]
    if (file) seleccionar(file)
  }

  function enviar(evento) {
    evento.preventDefault()
    if (archivo && !cargando) onExtract(archivo)
  }

  return (
    <form className="formulario" onSubmit={enviar}>
      <div
        className={`zona-suelto ${arrastrando ? 'arrastrando' : ''} ${archivo ? 'con-archivo' : ''}`}
        onDragOver={(e) => {
          e.preventDefault()
          setArrastrando(true)
        }}
        onDragLeave={() => setArrastrando(false)}
        onDrop={soltar}
        onClick={() => {
          if (inputRef.current) inputRef.current.click()
        }}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            if (inputRef.current) inputRef.current.click()
          }
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".docx,.odt"
          className="oculto"
          onChange={(e) => {
            const file = e.target.files && e.target.files[0]
            if (file) seleccionar(file)
            e.target.value = ''
          }}
        />
        {archivo ? (
          <div className="archivo-seleccionado">
            <strong>{archivo.name}</strong>
            <span>{(archivo.size / 1024).toFixed(1)} KB</span>
            <button
              type="button"
              className="quitar"
              onClick={(e) => {
                e.stopPropagation()
                setArchivo(null)
                setAviso('')
              }}
            >
              Quitar
            </button>
          </div>
        ) : (
          <p className="suelto-texto">
            Arrastra aquí tu currículum o haz clic para seleccionarlo
            <span>Formatos admitidos: .docx y .odt (máx. 10 MB)</span>
          </p>
        )}
      </div>

      {aviso && <p className="aviso" role="alert">{aviso}</p>}

      <button type="submit" className="boton-principal" disabled={!archivo || cargando}>
        {cargando ? 'Procesando…' : 'Extraer datos'}
      </button>
    </form>
  )
}
