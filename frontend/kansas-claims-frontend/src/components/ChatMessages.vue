<template>
  <v-container class="messages-container" ref="messagesContainer" style="overflow-y: auto; max-height: 400px;">
    <div
      v-for="message in messages"
      :key="message.id"
      class="message-wrapper"
      :class="{ 'user-message': message.type === 'user' }"
    >
      <ChatMessage
        :message="message"
        :is-user="message.type === 'user'"
      />
    </div>
  </v-container>
</template>

<script setup>
import { ref, watch, nextTick, onMounted, onUpdated } from 'vue'
import ChatMessage from './ChatMessage.vue'

const props = defineProps({
  messages: {
    type: Array,
    default: () => []
  }
})

const messagesContainer = ref(null)

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    const container = messagesContainer.value
    // Use scrollIntoView for better reliability
    const lastMessage = container.querySelector('.message-wrapper:last-child')
    if (lastMessage) {
      lastMessage.scrollIntoView({ behavior: 'smooth', block: 'end' })
    } else {
      // Fallback to scrollTop method
      container.scrollTop = container.scrollHeight
    }
  }
}

// Watch for new messages
watch(
  () => props.messages.length,
  scrollToBottom,
  { flush: 'post' } // Ensure DOM updates are complete
)

// Also watch for message content changes (for streaming responses)
watch(
  () => props.messages,
  scrollToBottom,
  { deep: true, flush: 'post' }
)

// Scroll on mount if there are existing messages
onMounted(() => {
  if (props.messages.length > 0) {
    scrollToBottom()
  }
})

// Additional scroll trigger after component updates
onUpdated(() => {
  scrollToBottom()
})
</script>

<style scoped>
.messages-container {
  max-height: 100%;
  overflow-y: auto;
  padding: 16px;
  scroll-behavior: smooth; /* Add smooth scrolling */
}

.message-wrapper {
  margin-bottom: 16px;
}

.user-message {
  display: flex;
  justify-content: flex-end;
}

/* Ensure the container has proper scrolling context */
.messages-container {
  position: relative;
}
</style>