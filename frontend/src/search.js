export function textoDe(valor) {
  if (valor == null) return ''
  if (typeof valor === 'string') return valor
  if (typeof valor === 'number' || typeof valor === 'boolean') return String(valor)
  if (Array.isArray(valor)) return valor.map(textoDe).join(' ')
  if (typeof valor === 'object') return Object.values(valor).map(textoDe).join(' ')
  return ''
}

export function contiene(datos, consulta) {
  const q = consulta.trim().toLowerCase()
  if (!q) return true
  return textoDe(datos).toLowerCase().includes(q)
}
