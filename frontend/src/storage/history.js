const CLAVE = 'cvstractor.historial'
const MAXIMO = 20

export function cargarHistorial() {
  try {
    const crudo = localStorage.getItem(CLAVE)
    const datos = crudo ? JSON.parse(crudo) : []
    return Array.isArray(datos) ? datos : []
  } catch {
    return []
  }
}

function persistir(entradas) {
  const recortadas = entradas.slice(0, MAXIMO)
  try {
    localStorage.setItem(CLAVE, JSON.stringify(recortadas))
  } catch {
    // Cuota superada: se ignora
  }
  return recortadas
}

export function guardarEntrada(entrada) {
  return persistir([entrada, ...cargarHistorial()])
}

export function eliminarEntrada(id) {
  return persistir(cargarHistorial().filter((e) => e.id !== id))
}

export function vaciarHistorial() {
  persistir([])
  return []
}
