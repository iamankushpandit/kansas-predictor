<template>
  <v-text-field
    v-model="selectedDate"
    type="date"
    label="Target Date"
    variant="outlined"
    density="comfortable"
    prepend-inner-icon="mdi-calendar"
    @update:model-value="$emit('update:model-value', $event)"
  />
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  modelValue: String
})

const emit = defineEmits(['update:model-value'])

const selectedDate = ref(props.modelValue || new Date().toISOString().substr(0, 10))
</script>