<script setup>
defineProps({ modelValue: String })
defineEmits(['update:modelValue'])
</script>
<template>
  <div class="toggle">
    <button :class="{ active: modelValue === 'grouped' }" @click="$emit('update:modelValue', 'grouped')">Agrupado</button>
    <button :class="{ active: modelValue === 'full' }" @click="$emit('update:modelValue', 'full')">Plano</button>
  </div>
</template>
