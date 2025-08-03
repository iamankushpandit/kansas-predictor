<template>
  <v-card flat class="fill-height">
    <v-card-title class="text-h6 pb-2">
      Quick Filters
    </v-card-title>
    
    <v-card-text>
      <!-- County Selector -->
      <CountySelector 
        v-model="selectedCounty"
        :counties="claimsStore.counties"
        @update:model-value="handleCountyChange"
      />
      
      <!-- Claim Type Selector -->
      <ClaimTypeSelector
        v-model="selectedClaimType" 
        :claim-types="claimsStore.claimTypes"
        @update:model-value="handleClaimTypeChange"
        class="mt-4"
      />
      
      <!-- Date Picker -->
      <DatePicker
        v-model="selectedDate"
        @update:model-value="handleDateChange"
        class="mt-4"
      />
      
      <!-- Quick Actions -->
      <v-divider class="my-4" />
      
      <div class="text-subtitle-2 mb-2">Quick Actions</div>
      
      <v-btn
        block
        variant="outlined"
        size="small"
        @click="predictNextWeek"
        :loading="loading"
        class="mb-2"
      >
        Predict Next Week
      </v-btn>
      
      <v-btn
        block
        variant="outlined"
        size="small"
        @click="showSeasonalTrends"
        :loading="loading"
        class="mb-2"
      >
        Seasonal Trends
      </v-btn>
      
      <v-btn
        block
        variant="outlined"
        size="small"
        @click="countySummary"
        :loading="loading"
      >
        County Summary
      </v-btn>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useClaimsStore } from '@/stores/claims'
import CountySelector from './CountySelector.vue'
import ClaimTypeSelector from './ClaimTypeSelector.vue'
import DatePicker from './DatePicker.vue'

const emit = defineEmits(['send-message'])

const claimsStore = useClaimsStore()
const loading = computed(() => claimsStore.loading)

const selectedCounty = ref(null)
const selectedClaimType = ref(null)
const selectedDate = ref(new Date().toISOString().substr(0, 10))

const handleCountyChange = (county) => {
  claimsStore.setSelectedCounty(county)
}

const handleClaimTypeChange = (claimType) => {
  claimsStore.setSelectedClaimType(claimType)
}

const handleDateChange = (date) => {
  // Handle date change
}

const predictNextWeek = () => {
  if (selectedCounty.value && selectedClaimType.value) {
    emit('send-message', `Predict ${selectedClaimType.value} claims for next week in ${selectedCounty.value} County`)
  }
}

const showSeasonalTrends = () => {
  if (selectedCounty.value && selectedClaimType.value) {
    emit('send-message', `Show seasonal trends for ${selectedClaimType.value} claims in ${selectedCounty.value} County`)
  }
}

const countySummary = () => {
  if (selectedCounty.value) {
    emit('send-message', `Give me a summary of all claims in ${selectedCounty.value} County`)
  }
}
</script>