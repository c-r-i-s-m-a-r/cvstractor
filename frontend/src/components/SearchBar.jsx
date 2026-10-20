export default function SearchBar({ consulta, onCambio }) {
  return (
    <div className="buscador">
      <svg
        className="buscador-icono"
        viewBox="0 0 24 24"
        width="18"
        height="18"
        aria-hidden="true"
      >
        <path
          fill="currentColor"
          d="M15.5 14h-.79l-.28-.27a6.5 6.5 0 1 0-.7.7l.27.28v.79l5 4.99L20.49 19zm-6 0A4.5 4.5 0 1 1 14 9.5 4.5 4.5 0 0 1 9.5 14"
        />
      </svg>
      <input
        type="search"
        placeholder="Buscar palabras clave en los resultados y el historial…"
        value={consulta}
        onChange={(e) => onCambio(e.target.value)}
        aria-label="Buscar palabras clave"
      />
      {consulta && (
        <button type="button" className="limpiar" onClick={() => onCambio('')}>
          ×
        </button>
      )}
    </div>
  )
}
