<script setup>
import { computed, ref } from 'vue'
const props = defineProps({ data: Object })
const copied = ref(false)
const formatted = computed(() => JSON.stringify(props.data, null, 2))
const sections = computed(() => {
  const result = {}
  for (const item of props.data.elementos || []) {
    const key = item.seccion === 'cabecera' ? 'Información principal' : item.seccion
    if (!result[key]) result[key] = []
    result[key].push(item)
  }
  return result
})
const labels = { email: 'Correo', telefono: 'Teléfono', ubicacion: 'Ubicación', linkedin: 'LinkedIn', github: 'GitHub', web: 'Sitio web', dni_nie: 'Documento' }
function label(value) { return labels[value] || value.replaceAll('.', ' · ').replaceAll('_', ' ') }
function present(value) { return value !== null && value !== undefined && value !== '' }
async function copy() {
  await navigator.clipboard.writeText(formatted.value)
  copied.value = true
  setTimeout(() => copied.value = false, 1500)
}
function download() {
  const url = URL.createObjectURL(new Blob([formatted.value], { type: 'application/json' }))
  const link = document.createElement('a')
  link.href = url
  link.download = 'cv-result.json'
  link.click()
  URL.revokeObjectURL(url)
}
</script>
<template>
  <section class="result">
    <div class="result-head"><div><span class="eyebrow">EXTRACCIÓN COMPLETADA</span><h2>{{ data.archivo }}</h2></div><div><button @click="copy">{{ copied ? 'Copiado' : 'Copiar datos' }}</button><button @click="download">Descargar</button></div></div>
    <div v-if="data.modo === 'agrupado'" class="visual-grid">
      <article class="profile-panel"><div class="avatar">{{ (data.personal.nombre || '?').slice(0, 1) }}</div><div><h3>{{ data.personal.nombre || 'Nombre no detectado' }}</h3><p>{{ data.personal.puesto || 'Puesto no detectado' }}</p></div></article>
      <article v-if="data.personal.resumen" class="data-panel wide"><h3>Perfil profesional</h3><p>{{ data.personal.resumen }}</p></article>
      <article class="data-panel"><h3>Contacto</h3><dl><template v-for="(value, key) in data.personal" :key="key"><div v-if="present(value) && !['nombre', 'puesto', 'resumen'].includes(key)"><dt>{{ label(key) }}</dt><dd>{{ value }}</dd></div></template></dl></article>
      <article class="data-panel"><h3>Habilidades</h3><div v-if="data.habilidades.lista.length" class="chips"><span v-for="item in data.habilidades.lista" :key="item">{{ item }}</span></div><p v-else class="empty">No se detectaron habilidades.</p><h4>Idiomas</h4><div v-for="item in data.habilidades.idiomas" :key="item.idioma" class="row"><strong>{{ item.idioma }}</strong><span>{{ item.nivel || 'No indicado' }}</span></div></article>
      <article class="data-panel wide"><h3>Experiencia laboral</h3><div v-if="data.laboral.experiencia.length" class="timeline"><div v-for="item in data.laboral.experiencia" :key="item.puesto + item.empresa" class="timeline-item"><h4>{{ item.puesto || 'Puesto no indicado' }}</h4><p class="organization">{{ item.empresa || 'Empresa no indicada' }}<span v-if="item.ubicacion"> · {{ item.ubicacion }}</span></p><small v-if="item.fecha_inicio || item.fecha_fin">{{ item.fecha_inicio || '?' }} — {{ item.fecha_fin || 'Actualidad' }}</small><p v-if="item.descripcion">{{ item.descripcion }}</p></div></div><p v-else class="empty">No se detectó experiencia laboral.</p></article>
      <article class="data-panel wide"><h3>Formación académica</h3><div v-if="data.academico.formacion.length" class="records"><div v-for="item in data.academico.formacion" :key="item.titulo"><strong>{{ item.titulo }}</strong><span>{{ item.institucion || 'Institución no indicada' }}</span><small>{{ item.fecha_inicio || '?' }} — {{ item.fecha_fin || '?' }}</small></div></div><p v-else class="empty">No se detectó formación académica.</p></article>
      <article v-if="data.academico.certificaciones.length" class="data-panel wide"><h3>Cursos y certificaciones</h3><div class="records"><div v-for="item in data.academico.certificaciones" :key="item.nombre"><strong>{{ item.nombre }}</strong><span>{{ item.entidad || 'Entidad no indicada' }}</span><small>{{ item.fecha || 'Fecha no indicada' }}</small></div></div></article>
    </div>
    <div v-else class="full-view"><div class="summary"><span>{{ data.documento.formato.toUpperCase() }}</span><span>{{ data.documento.lineas }} líneas</span><span>{{ data.elementos.length }} datos</span></div><article v-for="(items, name) in sections" :key="name" class="data-panel wide"><h3>{{ name }}</h3><dl class="full-details"><div v-for="item in items" :key="item.campo + item.valor + item.posicion"><dt>{{ label(item.campo) }}</dt><dd>{{ item.valor }}</dd></div></dl></article></div>
  </section>
</template>
