<template>
  <v-card variant="outlined" class="mt-3">
    <v-card-title class="text-subtitle-1">
      Prediction Trend
    </v-card-title>
    <v-card-text>
      <canvas ref="chartCanvas" width="400" height="200"></canvas>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'

const props = defineProps({
  data: Array
})

const chartCanvas = ref(null)

onMounted(() => {
  if (props.data?.length) {
    renderChart()
  }
})

watch(() => props.data, () => {
  if (props.data?.length) {
    renderChart()
  }
})

const renderChart = () => {
  const canvas = chartCanvas.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  const width = canvas.width
  const height = canvas.height
  
  // Clear canvas
  ctx.clearRect(0, 0, width, height)
  
  if (!props.data?.length) return
  
  // Prepare data
  const counts = props.data.map(d => d.predicted_count)
  const maxCount = Math.max(...counts)
  const minCount = Math.min(...counts)
  
  // Draw chart
  ctx.strokeStyle = '#1976d2'
  ctx.lineWidth = 2
  ctx.beginPath()
  
  props.data.forEach((point, index) => {
    const x = (index / (props.data.length - 1)) * (width - 40) + 20
    const y = height - 40 - ((point.predicted_count - minCount) / (maxCount - minCount)) * (height - 80)
    
    if (index === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  })
  
  ctx.stroke()
  
  // Draw points
  ctx.fillStyle = '#1976d2'
  props.data.forEach((point, index) => {
    const x = (index / (props.data.length - 1)) * (width - 40) + 20
    const y = height - 40 - ((point.predicted_count - minCount) / (maxCount - minCount)) * (height - 80)
    
    ctx.beginPath()
    ctx.arc(x, y, 4, 0, 2 * Math.PI)
    ctx.fill()
  })
}
</script>