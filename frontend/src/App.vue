<script setup>
import { ref } from 'vue'
import FilePicker from './components/FilePicker.vue'
import ModeToggle from './components/ModeToggle.vue'
import JsonViewer from './components/JsonViewer.vue'

const file = ref(null)
const mode = ref('grouped')
const loading = ref(false)
const error = ref('')
const result = ref(null)
function selected(value) { file.value = value; error.value = ''; result.value = null }
async function extract() {
  if (!file.value) return
  loading.value = true
  error.value = ''
  result.value = null
  const body = new FormData()
  body.append('file', file.value)
  try {
    const endpoint = mode.value === 'grouped' ? 'grouped' : 'full'
    const response = await fetch('/api/extract/' + endpoint, { method: 'POST', body })
    const payload = await response.json()
    if (!response.ok) throw new Error(payload.detail || 'No se pudo procesar el documento')
    result.value = payload
  } catch (exception) {
    error.value = exception.message
  } finally {
    loading.value = false
  }
}
</script>
<template>
  <main>
    <section class="card">
      <header><span class="eyebrow">CVSTRACTOR</span><h1>Convierte tu CV en datos útiles.</h1><p>Extrae información de documentos DOCX y ODT mediante reglas de texto.</p></header>
      <FilePicker @select="selected" />
      <div v-if="file" class="file-row"><span>{{ file.name }}</span><small>{{ (file.size / 1024).toFixed(1) }} KB</small><button @click="file = null">Quitar</button></div>
      <div class="mode-row"><span>Modo de extracción</span><ModeToggle v-model="mode" /></div>
      <button class="extract" :disabled="!file || loading" @click="extract">{{ loading ? 'Extrayendo información…' : 'Extraer información' }}</button>
      <p v-if="error" class="error alert">{{ error }}</p>
    </section>
    <JsonViewer v-if="result" :data="result" />
  </main>
</template>
