import { defineStore } from 'pinia'
import axios from 'axios'

const API_BASE = 'http://localhost:3001'

export const useClaimsStore = defineStore('claims', {
  state: () => ({
    counties: [],
    claimTypes: [],
    selectedCounty: null,
    selectedClaimType: null,
    predictions: [],
    loading: false,
    error: null
  }),

  actions: {
    async loadInitialData() {
      try {
        this.loading = true
        
        const [countiesRes, claimTypesRes] = await Promise.all([
          axios.get(`${API_BASE}/counties`),
          axios.get(`${API_BASE}/claim-types`)
        ])
        
        this.counties = countiesRes.data.counties
        this.claimTypes = claimTypesRes.data.claim_types
        
        // Set defaults
        this.selectedCounty = this.counties[0] || null
        this.selectedClaimType = this.claimTypes[0] || null
        
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    async sendChatMessage(message) {
      try {
        const response = await axios.post(`${API_BASE}/chat`, {
          message: message
        })
        
        return response.data
      } catch (error) {
        throw new Error(error.response?.data?.detail || 'Chat service unavailable')
      }
    },

    async getPrediction(county, claimType, targetDate) {
      try {
        this.loading = true
        
        const response = await axios.post(`${API_BASE}/predict`, {
          county,
          claim_type: claimType,
          target_date: targetDate
        })
        
        return response.data
      } catch (error) {
        throw new Error(error.response?.data?.detail || 'Prediction failed')
      } finally {
        this.loading = false
      }
    },

    async getPredictionRange(county, claimType, days = 30) {
      try {
        this.loading = true
        
        const response = await axios.get(
          `${API_BASE}/predict-range/${county}/${claimType}?days=${days}`
        )
        
        this.predictions = response.data.predictions
        return response.data.predictions
      } catch (error) {
        throw new Error(error.response?.data?.detail || 'Range prediction failed')
      } finally {
        this.loading = false
      }
    },

    async getCountySummary(county) {
      try {
        const response = await axios.get(`${API_BASE}/summary/${county}`)
        return response.data
      } catch (error) {
        throw new Error(error.response?.data?.detail || 'Summary unavailable')
      }
    },

    async getSeasonalInsights(county, claimType) {
      try {
        const response = await axios.get(
          `${API_BASE}/insights/${county}/${claimType}`
        )
        return response.data
      } catch (error) {
        throw new Error(error.response?.data?.detail || 'Insights unavailable')
      }
    },

    setSelectedCounty(county) {
      this.selectedCounty = county
    },

    setSelectedClaimType(claimType) {
      this.selectedClaimType = claimType
    },

    clearError() {
      this.error = null
    }
  }
})