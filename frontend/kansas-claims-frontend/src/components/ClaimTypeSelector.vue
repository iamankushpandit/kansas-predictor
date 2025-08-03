<template>
  <v-select
    v-model="selectedClaimType"
    :items="formattedClaimTypes"
    label="Select Claim Type"
    variant="outlined"
    density="comfortable"
    prepend-inner-icon="mdi-medical-bag"
    @update:model-value="$emit('update:model-value', $event)"
  />
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  claimTypes: Array,
  modelValue: String
})

const emit = defineEmits(['update:model-value'])

const selectedClaimType = ref(props.modelValue)

const formattedClaimTypes = computed(() => {
  return props.claimTypes?.map(type => ({
    title: formatClaimType(type),
    value: type
  })) || []
})

const formatClaimType = (type) => {
  return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}
</script>