export default function HistoryList({ entradas, onAbrir, onEliminar, consulta }) {
  if (entradas.length === 0) {
    return (
      <p className="historial-vacio">
        {consulta
          ? 'Ningún CV del historial coincide con la búsqueda.'
          : 'Aún no hay CVs procesados.'}
      </p>
    )
  }

  return (
    <ul className="historial-lista">
      {entradas.map((entrada) => (
        <li key={entrada.id} className="historial-item">
          <button
            type="button"
            className="historial-abrir"
            onClick={() => onAbrir(entrada)}
            title="Ver resultado"
          >
            <span className="historial-nombre">{entrada.nombre}</span>
            <span className="historial-fecha">
              {new Date(entrada.fecha).toLocaleString('es-ES', {
                dateStyle: 'short',
                timeStyle: 'short',
              })}
            </span>
          </button>
          <button
            type="button"
            className="historial-eliminar"
            onClick={() => onEliminar(entrada.id)}
            aria-label={`Eliminar ${entrada.nombre}`}
            title="Eliminar"
          >
            ×
          </button>
        </li>
      ))}
    </ul>
  )
}
