<script setup>
import { ref } from 'vue'
const emit = defineEmits(['select', 'clear'])
const message = ref('')
function pick(file) {
  message.value = ''
  if (!file) return
  if (!/\.(docx|odt)$/i.test(file.name)) { message.value = 'Solo se permiten archivos .docx u .odt'; return }
  if (file.size > 5 * 1024 * 1024) { message.value = 'El archivo supera los 5 MB'; return }
  emit('select', file)
}
function drop(event) { pick(event.dataTransfer.files[0]) }
</script>
<template>
  <div class="picker" @dragover.prevent @drop.prevent="drop">
    <input id="file" type="file" accept=".docx,.odt" @change="pick($event.target.files[0])">
    <label for="file">Selecciona o arrastra tu CV</label>
    <p>Formatos admitidos: DOCX y ODT · máximo 5 MB</p>
    <p v-if="message" class="error">{{ message }}</p>
  </div>
</template>
