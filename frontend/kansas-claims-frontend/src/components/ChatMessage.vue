<template>
  <div class="message-container" :class="{ 'user-message': isUser }">
    <v-card
      :class="[
        'message-card',
        isUser ? 'user-card' : 'bot-card'
      ]"
      :color="isUser ? 'primary' : 'white'"
      elevation="0"
      variant="flat"
    >
      <!-- Avatar for bot messages -->
      <div v-if="!isUser" class="d-flex align-start pa-3 pb-0">
        <v-avatar size="32" class="me-3 mt-1" color="primary">
          <v-icon color="white" size="20">mdi-robot</v-icon>
        </v-avatar>
        <div class="flex-grow-1">
          <div class="text-caption text-medium-emphasis mb-2">AI Assistant</div>
        </div>
      </div>
      
      <v-card-text :class="isUser ? 'pa-4' : 'pa-3 pt-0'">
        <!-- Message Content with formatting -->
        <div :class="{ 'text-white': isUser }" class="message-text">
          <div v-if="message.animating" class="typing-text">{{ message.content }}</div>
          <div v-else v-html="formatMessage(message.content)"></div>
        </div>
        
        <!-- Show predictions if available -->
        <div v-if="message.context?.predictions" class="mt-4">
          <PredictionCards :predictions="message.context.predictions" />
        </div>
        
        <!-- Show charts if predictions available -->
        <div v-if="message.context?.predictions && message.context.predictions.length > 1" class="mt-4">
          <PredictionChart :data="message.context.predictions" />
        </div>
      </v-card-text>
      
      <!-- Timestamp -->
      <v-card-actions class="pa-3 pt-0">
        <v-spacer />
        <small :class="{ 'text-white': isUser }" class="text-caption opacity-70">
          {{ formatTime(message.timestamp) }}
        </small>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import PredictionCards from './PredictionCards.vue'
import PredictionChart from './PredictionChart.vue'

const props = defineProps({
  message: {
    type: Object,
    required: true
  },
  isUser: {
    type: Boolean,
    default: false
  }
})

const formatTime = (timestamp) => {
  return new Intl.DateTimeFormat('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  }).format(new Date(timestamp))
}

const formatMessage = (content) => {
  let formatted = content
  
  // Format headers
  formatted = formatted.replace(/^## (.+)$/gm, '<h3 class="text-primary mb-3 mt-2">$1</h3>')
  formatted = formatted.replace(/^### (.+)$/gm, '<h4 class="text-secondary mb-2 mt-3">$1</h4>')
  
  // Format bold text
  formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong class="text-primary">$1</strong>')
  
  // Format bullet points
  formatted = formatted.replace(/^\* (.+)$/gm, '<div class="ml-4 my-1">• $1</div>')
  
  // Format numbered lists
  formatted = formatted.replace(/^(\d+\.) (.+)$/gm, '<div class="ml-4 my-1">$1 $2</div>')
  
  // Add line breaks
  formatted = formatted.replace(/\n\n/g, '<br><br>')
  formatted = formatted.replace(/\n/g, '<br>')
  
  // Highlight currency
  formatted = formatted.replace(/(\$[\d,]+(?:\.\d{2})?)/g, '<span class="text-success font-weight-bold">$1</span>')
  
  return formatted
}
</script>

<style scoped>
.message-container {
  max-width: 75%;
  margin-bottom: 16px;
}

.user-message {
  margin-left: auto;
}

.message-card {
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border: 1px solid rgba(0,0,0,0.05);
}

.user-card {
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
  border-bottom-right-radius: 4px;
}

.bot-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-bottom-left-radius: 4px;
  border: 1px solid #e3f2fd;
}

.message-text {
  word-wrap: break-word;
  line-height: 1.6;
  font-size: 0.95rem;
}

.message-text ::v-deep(strong) {
  color: #1976d2;
  font-weight: 600;
}

.message-text ::v-deep(.text-primary) {
  color: #1976d2 !important;
}

.message-text ::v-deep(.text-success) {
  color: #4caf50 !important;
}

.typing-text {
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.6;
}
</style>