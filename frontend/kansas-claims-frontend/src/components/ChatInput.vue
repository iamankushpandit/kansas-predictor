<template>
  <v-card-actions class="pa-6">
    <v-row no-gutters align="center">
      <v-col>
        <v-text-field
          v-model="message"
          placeholder="Ask about Kansas claims predictions..."
          variant="outlined"
          density="comfortable"
          :loading="loading"
          :disabled="loading"
          @keyup.enter="sendMessage"
          hide-details
          class="me-3"
          style="min-height: 56px;"
        />
      </v-col>
      <v-col cols="auto">
        <v-btn
          color="primary"
          :loading="loading"
          :disabled="!message.trim() || loading"
          @click="sendMessage"
          size="large"
          variant="flat"
        >
          <v-icon>mdi-send</v-icon>
        </v-btn>
      </v-col>
    </v-row>
  </v-card-actions>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['send-message'])

const message = ref('')

const sendMessage = () => {
  if (message.value.trim() && !props.loading) {
    emit('send-message', message.value.trim())
    message.value = ''
  }
}
</script>