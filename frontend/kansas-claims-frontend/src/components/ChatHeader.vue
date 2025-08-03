<style scoped>
.header-bar {
  background: white !important;
  border-bottom: 1px solid #e0e0e0;
}
</style><template>
  <v-app-bar 
    color="transparent" 
    flat 
    class="header-bar"
  >
    <div class="d-flex align-center">
      <v-icon class="me-3" size="28" color="primary">mdi-hospital-box</v-icon>
      <div>
        <div class="text-h6 font-weight-bold text-primary">Kansas Claims Predictor</div>
        <div class="text-caption text-medium-emphasis">
          AI-powered health insurance claims forecasting
        </div>
      </div>
    </div>
    
    <v-spacer />
    
    <v-btn
      icon
      variant="text"
      @click="toggleTheme"
      class="me-2"
    >
      <v-icon>{{ isDark ? 'mdi-weather-sunny' : 'mdi-weather-night' }}</v-icon>
    </v-btn>
    
    <v-chip
      :color="isConnected ? 'success' : 'error'"
      size="small"
      variant="flat"
      class="text-white"
    >
      <v-icon start size="16">
        {{ isConnected ? 'mdi-wifi' : 'mdi-wifi-off' }}
      </v-icon>
      {{ isConnected ? 'Connected' : 'Offline' }}
    </v-chip>
  </v-app-bar>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useTheme } from 'vuetify'

const isConnected = ref(true)
const theme = useTheme()
const isDark = ref(theme.global.current.value.dark)

const toggleTheme = () => {
  theme.global.name.value = theme.global.current.value.dark ? 'light' : 'dark'
  isDark.value = !isDark.value
}

// Simple connection check
onMounted(() => {
  const checkConnection = () => {
    isConnected.value = navigator.onLine
  }
  
  window.addEventListener('online', checkConnection)
  window.addEventListener('offline', checkConnection)
  
  checkConnection()
})
</script>