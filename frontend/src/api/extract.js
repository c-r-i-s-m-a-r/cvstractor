export async function extraerCv(archivo) {
  const datos = new FormData()
  datos.append('cv', archivo)

  let respuesta
  try {
    respuesta = await fetch('/api/extract', { method: 'POST', body: datos })
  } catch {
    throw new Error('No se pudo conectar con el servidor. ¿Está el backend activo en el puerto 3000?')
  }

  let cuerpo = null
  try {
    cuerpo = await respuesta.json()
  } catch {
    // Respuesta sin JSON válido
  }

  if (!respuesta.ok) {
    throw new Error((cuerpo && cuerpo.error) || `Error del servidor (${respuesta.status})`)
  }

  return cuerpo
}
