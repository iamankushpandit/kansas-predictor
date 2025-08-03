<template>
  <v-select
    v-model="selectedCounty"
    :items="counties"
    label="Select County"
    variant="outlined"
    density="comfortable"
    prepend-inner-icon="mdi-map-marker"
    @update:model-value="$emit('update:model-value', $event)"
  />
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  counties: Array,
  modelValue: String
})

const emit = defineEmits(['update:model-value'])

const selectedCounty = ref(props.modelValue)
</script>