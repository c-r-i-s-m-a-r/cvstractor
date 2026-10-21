<script setup>
import { computed, ref } from 'vue'
const props = defineProps({ data: Object })
const copied = ref(false)
const formatted = computed(() => JSON.stringify(props.data, null, 2))
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
    <div class="result-head"><h2>Resultado</h2><div><button @click="copy">{{ copied ? 'Copiado' : 'Copiar JSON' }}</button><button @click="download">Descargar</button></div></div>
    <pre><code>{{ formatted }}</code></pre>
  </section>
</template>
