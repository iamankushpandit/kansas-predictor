<template>
  <v-app class="fill-height professional-font">
    <!-- Header -->
    <v-app-bar color="white" flat height="64">
      <v-icon class="me-3" color="primary">mdi-hospital-box</v-icon>
      <v-toolbar-title class="text-primary font-weight-bold">
        Kansas Claims Predictor
      </v-toolbar-title>
      <v-spacer />
      <v-btn icon @click="toggleTheme">
        <v-icon>{{ theme.global.current.value.dark ? 'mdi-weather-sunny' : 'mdi-weather-night' }}</v-icon>
      </v-btn>
      <v-chip color="success" size="small" class="text-white">
        <v-icon start size="16">mdi-wifi</v-icon>
        Connected
      </v-chip>
    </v-app-bar>

    <!-- Main Content -->
    <v-main class="chat-main">
      <div class="chat-container">
        <!-- Messages -->
        <div class="messages-area">
          <div v-for="message in messages" :key="message.id" class="mb-4">
            <div class="message-bubble-container" :class="message.type === 'user' ? 'user-bubble' : 'bot-bubble'">
              <v-card 
                :class="message.type === 'user' ? 'ml-auto bg-primary' : 'mr-auto bot-message'"
                :color="message.type === 'user' ? 'primary' : (theme.global.current.value.dark ? 'grey-darken-3' : 'white')"
                width="100%"
                elevation="2"
              >
                <v-card-text :class="message.type === 'user' ? 'text-white pa-6' : 'pa-6'" class="message-content">
                  <div class="d-flex justify-space-between align-start">
                    <div v-html="formatMessage(message.content)" class="message-text flex-grow-1"></div>
                    <v-btn
                      v-if="message.type === 'bot'"
                      icon
                      size="small"
                      :color="speakingMessageId === message.id ? 'error' : 'primary'"
                      @click="toggleSpeech(message.content, message.id)"
                      class="ml-2 flex-shrink-0"
                    >
                      <v-icon size="16">{{ speakingMessageId === message.id ? 'mdi-stop' : 'mdi-volume-high' }}</v-icon>
                    </v-btn>
                  </div>
                </v-card-text>
              </v-card>
            </div>
          </div>
        </div>

        <!-- Input -->
        <div class="input-area">
          <v-divider />
          <div class="pa-4">
            <div v-if="loading" class="mb-4">
              <v-progress-linear color="primary" indeterminate></v-progress-linear>
              <v-progress-linear color="secondary" indeterminate class="mt-1"></v-progress-linear>
              <v-progress-linear color="accent" indeterminate class="mt-1"></v-progress-linear>
              <div class="text-center mt-2 text-caption">Processing your request...</div>
            </div>
            <v-text-field
              v-model="newMessage"
              placeholder="Ask about Kansas claims predictions..."
              variant="outlined"
              :disabled="loading"
              @keyup.enter="sendMessage"
            >
              <template v-slot:append-inner>
                <v-btn
                  icon
                  size="small"
                  :color="isListening ? 'error' : 'primary'"
                  @click="isListening ? stopListening() : startListening()"
                  class="me-2 ai-voice-btn"
                  :class="{ 'listening-pulse': isListening }"
                  elevation="2"
                >
                  <v-icon>{{ isListening ? 'mdi-microphone-off' : 'mdi-microphone' }}</v-icon>
                </v-btn>
                <v-btn
                  icon
                  size="small"
                  color="primary"
                  @click="sendMessage"
                  :disabled="loading"
                >
                  <v-icon>mdi-send</v-icon>
                </v-btn>
              </template>
            </v-text-field>
          </div>
        </div>
      </div>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useTheme } from 'vuetify'
import { useClaimsStore } from '@/stores/claims'
import { marked } from 'marked'
import Typewriter from 'typewriter-effect/dist/core'

const theme = useTheme()
const claimsStore = useClaimsStore()
const messages = ref([{
  id: 1,
  type: 'bot',
  content: "## Welcome to Kansas Claims Predictor\n\n**Hi! I'm your Kansas claims prediction assistant.** I help analyze healthcare claims data across Kansas counties.\n\n### What I can help you with:\n\n* **Volume Predictions** - Predict claim counts for specific counties and dates\n* **Cost Analysis** - Analyze average costs and spending trends\n* **Seasonal Patterns** - Understand seasonal claim variations\n* **Geographic Comparisons** - Compare different counties\n* **Claim Type Analysis** - Emergency, inpatient, outpatient, pharmacy, mental health, preventive\n\n### Example questions you can ask:\n\n* *'Predict emergency claims for Johnson County next week'*\n* *'Show pharmacy costs in Sedgwick County'*\n* *'What are the seasonal trends for mental health claims?'*\n* *'Compare inpatient costs between Johnson and Wyandotte counties'*\n* *'How many preventive claims are expected in Douglas County?'*\n\n**Just type your question below to get started!**"
}])
const newMessage = ref('')
const loading = ref(false)
const isListening = ref(false)
const recognition = ref(null)
const speakingMessageId = ref(null)
const currentUtterance = ref(null)
const wasVoiceInput = ref(false)

const toggleTheme = () => {
  theme.global.name.value === 'dark' ? theme.change('light') : theme.change('dark')
}

const initSpeechRecognition = () => {
  if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    recognition.value = new SpeechRecognition()
    recognition.value.continuous = false
    recognition.value.interimResults = false
    recognition.value.lang = 'en-US'
    
    recognition.value.onstart = () => {
      isListening.value = true
    }
    
    recognition.value.onresult = async (event) => {
      const transcript = event.results[0][0].transcript
      newMessage.value = transcript
      isListening.value = false
      wasVoiceInput.value = true
      
      // Auto-send the message and speak the response
      await sendMessage()
    }
    
    recognition.value.onerror = () => {
      isListening.value = false
    }
    
    recognition.value.onend = () => {
      isListening.value = false
    }
  }
}

const startListening = () => {
  if (recognition.value && !isListening.value) {
    recognition.value.start()
  }
}

const stopListening = () => {
  if (recognition.value && isListening.value) {
    recognition.value.stop()
  }
}

const toggleSpeech = (text, messageId) => {
  if (speakingMessageId.value === messageId) {
    stopSpeech()
  } else {
    speakText(text, messageId)
  }
}

const getBestVoice = () => {
  const voices = speechSynthesis.getVoices()
  const platform = navigator.platform.toLowerCase()
  
  // Platform-specific premium voices
  const voicePreferences = [
    // Windows premium voices
    'Microsoft Zira Desktop',
    'Microsoft David Desktop', 
    'Microsoft Mark',
    'Microsoft Zira',
    // Mac premium voices
    'Samantha',
    'Alex',
    'Victoria',
    'Karen',
    // Google/Chrome voices
    'Google US English',
    'Google UK English Female',
    'Chrome OS US English Female',
    // Fallback to any English voice
    'English'
  ]
  
  for (const preference of voicePreferences) {
    const voice = voices.find(v => v.name.includes(preference) && v.lang.startsWith('en'))
    if (voice) return voice
  }
  
  // Final fallback to first English voice
  return voices.find(v => v.lang.startsWith('en')) || voices[0]
}

const speakText = (text, messageId) => {
  if ('speechSynthesis' in window) {
    speechSynthesis.cancel()
    
    const cleanText = text
      .replace(/<[^>]*>/g, '')
      .replace(/[#*]/g, '')
      .replace(/\n+/g, '. ')
    
    currentUtterance.value = new SpeechSynthesisUtterance(cleanText)
    
    // Use best available voice
    const bestVoice = getBestVoice()
    if (bestVoice) {
      currentUtterance.value.voice = bestVoice
    }
    
    // Optimized settings for natural speech
    currentUtterance.value.rate = 0.8
    currentUtterance.value.pitch = 0.9
    currentUtterance.value.volume = 0.9
    
    currentUtterance.value.onstart = () => {
      speakingMessageId.value = messageId
    }
    
    currentUtterance.value.onend = () => {
      speakingMessageId.value = null
      currentUtterance.value = null
    }
    
    currentUtterance.value.onerror = () => {
      speakingMessageId.value = null
      currentUtterance.value = null
    }
    
    speechSynthesis.speak(currentUtterance.value)
  }
}

const stopSpeech = () => {
  if ('speechSynthesis' in window) {
    speechSynthesis.cancel()
    speakingMessageId.value = null
    currentUtterance.value = null
  }
}

const sendMessage = async () => {
  if (!newMessage.value.trim() || loading.value) return

  messages.value.push({
    id: Date.now(),
    type: 'user',
    content: newMessage.value
  })

  const userMessage = newMessage.value
  newMessage.value = ''
  loading.value = true

  try {
    const response = await claimsStore.sendChatMessage(userMessage)
    const botMessage = {
      id: Date.now() + 1,
      type: 'bot',
      content: response.response || response
    }
    messages.value.push(botMessage)
    
    // Auto-speak the response if it came from voice input
    if (wasVoiceInput.value) {
      setTimeout(() => {
        speakText(botMessage.content, botMessage.id)
      }, 500)
      wasVoiceInput.value = false
    }
  } catch (error) {
    messages.value.push({
      id: Date.now() + 1,
      type: 'bot',
      content: 'Sorry, I encountered an error processing your request.'
    })
  } finally {
    loading.value = false
  }
}

const formatMessage = (content) => {
  let html = marked(content)
  html = html.replace(/(\$[\d,]+(?:\.\d{2})?)/g, '<span class="text-success font-weight-bold">$1</span>')
  
  // Add download button to images
  html = html.replace(/<img([^>]*src="data:image\/png;base64,([^"]+)"[^>]*)>/g, 
    '<div class="chart-container"><img$1><button class="download-chart-btn" onclick="downloadChart(\'$2\')" title="Download Chart"><i class="mdi mdi-download"></i></button></div>')
  
  return html
}

const downloadChart = (base64Data) => {
  const link = document.createElement('a')
  link.href = `data:image/png;base64,${base64Data}`
  link.download = `kansas-claims-chart-${Date.now()}.png`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// Make downloadChart globally available
window.downloadChart = downloadChart





onMounted(() => {
  // Load initial data in background
  claimsStore.loadInitialData()
  // Initialize speech recognition
  initSpeechRecognition()
})
</script>

<style scoped>
.typing-text {
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.2;
}

.message-text {
  line-height: 1.6;
}

.message-text h2, .message-text h3 {
  color: #1976d2;
  margin: 12px 0 8px 0;
}

.message-text ul {
  margin: 8px 0;
  padding-left: 20px;
}

.message-text li {
  margin: 6px 0;
}

.message-text strong {
  color: #1976d2;
}

.message-text p {
  margin: 12px 0;
}

.bot-message .message-text {
  color: inherit;
}

.message-content {
  padding: 24px !important;
}

.professional-font {
  font-family: 'Inter', 'Segoe UI', 'Roboto', -apple-system, BlinkMacSystemFont, sans-serif;
}

.message-text {
  font-family: 'Inter', 'Segoe UI', 'Roboto', -apple-system, BlinkMacSystemFont, sans-serif;
  font-weight: 400;
  letter-spacing: -0.01em;
}

.message-text h2, .message-text h3 {
  font-family: 'Inter', 'Segoe UI', 'Roboto', -apple-system, BlinkMacSystemFont, sans-serif;
  font-weight: 600;
  letter-spacing: -0.02em;
}

.chat-main {
  height: 100vh;
  padding-top: 64px !important;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 64px);
  width: 100%;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  min-height: 0;
}

.input-area {
  flex-shrink: 0;
}

.message-bubble-container {
  position: relative;
}

.user-bubble::after {
  content: '';
  position: absolute;
  bottom: 0;
  right: 15px;
  width: 0;
  height: 0;
  border: 10px solid transparent;
  border-top-color: #1976d2;
  border-bottom: 0;
  margin-bottom: -10px;
}

.bot-bubble::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 15px;
  width: 0;
  height: 0;
  border: 10px solid transparent;
  border-top-color: white;
  border-bottom: 0;
  margin-bottom: -10px;
}

.theme--dark .bot-bubble::after {
  border-top-color: #424242;
}

.chart-container {
  position: relative;
  display: inline-block;
  margin: 16px 0;
}

.chart-container img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.download-chart-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(25, 118, 210, 0.9);
  color: white;
  border: none;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: all 0.3s ease;
  opacity: 0;
}

.chart-container:hover .download-chart-btn {
  opacity: 1;
}

.download-chart-btn:hover {
  background: rgba(25, 118, 210, 1);
  transform: scale(1.1);
}

.ai-voice-btn {
  background: linear-gradient(135deg, #1976d2 0%, #42a5f5 100%) !important;
  border-radius: 50% !important;
  transition: all 0.3s ease !important;
  box-shadow: 0 4px 12px rgba(25, 118, 210, 0.3) !important;
}

.ai-voice-btn:hover {
  transform: scale(1.1) !important;
  box-shadow: 0 6px 16px rgba(25, 118, 210, 0.4) !important;
}

.listening-pulse {
  animation: pulse-glow 1.5s infinite !important;
  background: linear-gradient(135deg, #f44336 0%, #ff5722 100%) !important;
  box-shadow: 0 4px 12px rgba(244, 67, 54, 0.4) !important;
}

@keyframes pulse-glow {
  0% {
    transform: scale(1);
    box-shadow: 0 4px 12px rgba(244, 67, 54, 0.4);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 6px 20px rgba(244, 67, 54, 0.6);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 4px 12px rgba(244, 67, 54, 0.4);
  }
}

.message-text img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 12px 0;
}
</style>