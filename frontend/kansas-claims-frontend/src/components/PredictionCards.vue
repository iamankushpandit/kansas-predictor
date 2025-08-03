<template>
  <div class="prediction-cards">
    <v-row>
      <v-col
        v-for="prediction in predictions.slice(0, 3)"
        :key="prediction.date"
        cols="12"
        sm="4"
      >
        <v-card variant="outlined" class="prediction-card">
          <v-card-text class="text-center">
            <div class="text-h4 text-primary mb-2">
              {{ prediction.predicted_count }}
            </div>
            <div class="text-subtitle-2 mb-1">Claims</div>
            <div class="text-h6 text-success">
              ${{ formatCurrency(prediction.predicted_cost) }}
            </div>
            <div class="text-caption text-medium-emphasis">
              {{ formatDate(prediction.date) }}
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
const props = defineProps({
  predictions: Array
})

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    notation: 'compact',
    maximumFractionDigits: 1
  }).format(amount)
}

const formatDate = (dateString) => {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric'
  }).format(new Date(dateString))
}
</script>

<style scoped>
.prediction-card {
  transition: transform 0.2s;
}

.prediction-card:hover {
  transform: translateY(-2px);
}
</style>