export default function Highlight({ texto, consulta }) {
  const partes = []
  if (texto == null || texto === '') return null

  const cadena = String(texto)
  const q = (consulta || '').trim()
  if (!q) return cadena

  const minus = cadena.toLowerCase()
  const qMinus = q.toLowerCase()
  let desde = 0
  let clave = 0

  while (desde < cadena.length) {
    const indice = minus.indexOf(qMinus, desde)
    if (indice === -1) {
      partes.push(cadena.slice(desde))
      break
    }
    if (indice > desde) partes.push(cadena.slice(desde, indice))
    partes.push(
      <mark key={clave++}>{cadena.slice(indice, indice + q.length)}</mark>
    )
    desde = indice + q.length
  }

  return partes
}
