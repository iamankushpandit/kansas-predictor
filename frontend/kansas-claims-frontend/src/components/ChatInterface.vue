<style scoped>
.chat-app {
  background: #f8f9fa;
  min-height: 100vh;
}

.chat-main {
  padding-top: 64px !important; /* Account for header height */
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 64px);
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 0;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  min-height: 0;
}

.input-area {
  border-top: 1px solid #e0e0e0;
  background: white;
  padding: 16px;
  flex-shrink: 0;
}
</style><template>
  <v-app class="chat-app">
    <!-- Header -->
    <ChatHeader />
    
    <!-- Main Chat Area -->
    <v-main class="chat-main">
      <v-container fluid class="chat-container pa-0 fill-height">
        <!-- Messages -->
        <div class="messages-area">
          <ChatMessages :messages="messages" />
        </div>
        
        <!-- Input -->
        <div class="input-area">
          <v-text-field
            v-model="testMessage"
            placeholder="Type a message..."
            @keyup.enter="handleTestSend"
            variant="outlined"
            append-inner-icon="mdi-send"
            @click:append-inner="handleTestSend"
          />
        </div>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useClaimsStore } from '@/stores/claims'
import ChatHeader from '@/components/ChatHeader.vue'
import ChatMessages from '@/components/ChatMessages.vue'
import ChatInput from '@/components/ChatInput.vue'

const claimsStore = useClaimsStore()
const messages = ref([])
const loading = ref(false)
const testMessage = ref('')

const handleTestSend = () => {
  if (testMessage.value.trim()) {
    handleSendMessage(testMessage.value.trim())
    testMessage.value = ''
  }
}

onMounted(async () => {
  await claimsStore.loadInitialData()
  
  // Welcome message with usage info
  const welcomeMessage = {
    id: 1,
    type: 'bot',
    content: '',
    fullContent: "## TESTING - FILE UPDATED SUCCESSFULLY\n\n**This message should show typing animation and markdown formatting**\n\nIf you see this message with proper formatting, the changes are working!",
    timestamp: new Date(),
    animating: true
  }
  
  messages.value.push(welcomeMessage)
  await animateTyping(welcomeMessage)
})

const handleSendMessage = async (message) => {
  // Add user message
  messages.value.push({
    id: Date.now(),
    type: 'user',
    content: message,
    timestamp: new Date()
  })
  
  // Add typing indicator
  const typingId = Date.now() + 1
  messages.value.push({
    id: typingId,
    type: 'bot',
    content: '',
    typing: true,
    timestamp: new Date()
  })
  
  loading.value = true
  
  try {
    const response = await claimsStore.sendChatMessage(message)
    
    // Remove typing indicator
    const typingIndex = messages.value.findIndex(m => m.id === typingId)
    if (typingIndex !== -1) {
      messages.value.splice(typingIndex, 1)
    }
    
    // Add bot response with typing animation
    const botMessage = {
      id: Date.now() + 2,
      type: 'bot',
      content: '',
      fullContent: response.response,
      context: response.context,
      usage: response.usage,
      timestamp: new Date(),
      animating: true
    }
    
    messages.value.push(botMessage)
    
    // Animate typing
    await animateTyping(botMessage)
    
  } catch (error) {
    // Remove typing indicator
    const typingIndex = messages.value.findIndex(m => m.id === typingId)
    if (typingIndex !== -1) {
      messages.value.splice(typingIndex, 1)
    }
    
    messages.value.push({
      id: Date.now() + 2,
      type: 'bot',
      content: 'Sorry, I encountered an error processing your request.',
      error: true,
      timestamp: new Date()
    })
  } finally {
    loading.value = false
  }
}

const animateTyping = async (message) => {
  const fullText = message.fullContent
  const usageText = message.usage ? `Groq API Usage: ${message.usage.groq_requests_used}/${message.usage.groq_requests_limit} requests used today\n\n` : ''
  const completeText = usageText + fullText
  
  // Faster typing animation - 2-3 characters at a time
  const chunkSize = Math.random() > 0.7 ? 3 : 2
  
  for (let i = 0; i <= completeText.length; i += chunkSize) {
    message.content = completeText.substring(0, i)
    await new Promise(resolve => setTimeout(resolve, 15)) // 15ms delay per chunk
  }
  
  // Ensure we have the complete text
  message.content = completeText
  message.animating = false
}
</script>

<style scoped>
.chat-area {
  background: #f5f5f5;
}

.sidebar {
  background: white;
  border-right: 1px solid #e0e0e0;
}
</style>