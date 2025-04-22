<template>
  <div class="register-container">
    <div class="register-form-container">
      <h1 class="form-title">Create Your Account</h1>
      <p class="form-subtitle">Join Sponnect to connect with brands and influencers</p>
      
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      
      <form @submit.prevent="register" class="register-form">
        <div class="form-group">
          <label for="account-type">I am a:</label>
          <div class="account-type-selector">
            <div 
              class="account-type-option" 
              :class="{ active: accountType === 'brand' }"
              @click="accountType = 'sponsor'"
            >
              <i class="fas fa-briefcase"></i>
              <span>Brand</span>
            </div>
            <div 
              class="account-type-option" 
              :class="{ active: accountType === 'influencer' }"
              @click="accountType = 'influencer'"
            >
              <i class="fas fa-user"></i>
              <span>Influencer</span>
            </div>
          </div>
        </div>
        
        <div class="form-group">
          <label for="name">Full Name</label>
          <input 
            id="name" 
            v-model="name" 
            type="text" 
            placeholder="Enter your full name"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="email">Email Address</label>
          <input 
            id="email" 
            v-model="email" 
            type="email" 
            placeholder="Enter your email address"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="password">Password</label>
          <div class="password-input-container">
            <input 
              id="password" 
              v-model="password" 
              :type="showPassword ? 'text' : 'password'" 
              placeholder="Create a password"
              required
            />
            <button 
              type="button" 
              class="toggle-password" 
              @click="showPassword = !showPassword"
            >
              <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
            </button>
          </div>
          <div class="password-strength" v-if="password">
            <div 
              class="strength-indicator" 
              :class="passwordStrength"
            ></div>
            <span>{{ passwordStrengthText }}</span>
          </div>
        </div>
        
        <div class="form-group">
          <label for="confirmPassword">Confirm Password</label>
          <div class="password-input-container">
            <input 
              id="confirmPassword" 
              v-model="confirmPassword" 
              :type="showConfirmPassword ? 'text' : 'password'" 
              placeholder="Confirm your password"
              required
            />
            <button 
              type="button" 
              class="toggle-password" 
              @click="showConfirmPassword = !showConfirmPassword"
            >
              <i :class="showConfirmPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
            </button>
          </div>
          <div class="password-match" v-if="confirmPassword">
            <i :class="passwordsMatch ? 'fas fa-check' : 'fas fa-times'"></i>
            <span>{{ passwordsMatch ? 'Passwords match' : 'Passwords do not match' }}</span>
          </div>
        </div>
        
        <div class="form-group checkbox-group">
          <input id="terms" v-model="termsAccepted" type="checkbox" required />
          <label for="terms">
            I agree to the <router-link to="/terms">Terms of Service</router-link> and <router-link to="/privacy">Privacy Policy</router-link>
          </label>
        </div>
        
        <button 
          type="submit" 
          class="register-button" 
          :disabled="isSubmitting || !formValid"
        >
          <span v-if="!isSubmitting">Create Account</span>
          <span v-else>
            <i class="fas fa-spinner fa-spin"></i> Creating Account...
          </span>
        </button>
      </form>
      
      <div class="alternative-options">
        <p>
          Already have an account? <router-link to="/auth/login">Log In</router-link>
        </p>
      </div>
    </div>
    
    <div class="register-info">
      <div class="info-content">
        <h2>Join the Sponnect Community</h2>
        <div class="benefits">
          <div class="benefit">
            <i class="fas fa-check-circle"></i>
            <span>{{ accountType === 'brand' ? 'Find the perfect influencers for your campaigns' : 'Discover brand collaboration opportunities' }}</span>
          </div>
          <div class="benefit">
            <i class="fas fa-check-circle"></i>
            <span>{{ accountType === 'brand' ? 'Track campaign performance and ROI' : 'Showcase your content and grow your audience' }}</span>
          </div>
          <div class="benefit">
            <i class="fas fa-check-circle"></i>
            <span>{{ accountType === 'brand' ? 'Streamlined communication and campaign management' : 'Secure payments and professional contracts' }}</span>
          </div>
        </div>
        <div class="testimonial">
          <p>"{{ accountType === 'brand' ? 'Sponnect has transformed how we manage influencer relationships. Highly recommended for any marketing team.' : 'Since joining Sponnect, I\'ve doubled my brand collaborations and increased my revenue significantly.' }}"</p>
          <div class="testimonial-author">
            <img :src="accountType === 'brand' ? '/img/brand-testimonial.webp' : '/img/influencer-testimonial.webp'" :alt="accountType === 'brand' ? 'Marketing Director' : 'Content Creator'" />
            <div>
              <h4>{{ accountType === 'brand' ? 'John Davis' : 'Emma Rodriguez' }}</h4>
              <p>{{ accountType === 'brand' ? 'Marketing Director, FashionBrand' : 'Lifestyle Creator, 300K+ Followers' }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'Register',
  setup() {
    const store = useStore()
    const router = useRouter()
    
    // Form data
    const accountType = ref('influencer')
    const name = ref('')
    const email = ref('')
    const password = ref('')
    const confirmPassword = ref('')
    const termsAccepted = ref(false)
    
    // UI state
    const showPassword = ref(false)
    const showConfirmPassword = ref(false)
    const isSubmitting = ref(false)
    const error = ref('')
    
    // Password strength calculation
    const passwordStrength = computed(() => {
      if (!password.value) return ''
      
      const hasUpperCase = /[A-Z]/.test(password.value)
      const hasLowerCase = /[a-z]/.test(password.value)
      const hasNumbers = /\d/.test(password.value)
      const hasSpecialChars = /[!@#$%^&*(),.?":{}|<>]/.test(password.value)
      const isLongEnough = password.value.length >= 8
      
      const score = [hasUpperCase, hasLowerCase, hasNumbers, hasSpecialChars, isLongEnough]
        .filter(Boolean).length
      
      if (score <= 2) return 'weak'
      if (score <= 4) return 'medium'
      return 'strong'
    })
    
    const passwordStrengthText = computed(() => {
      if (!password.value) return ''
      
      switch (passwordStrength.value) {
        case 'weak': return 'Weak - Add more variety'
        case 'medium': return 'Medium - Getting better'
        case 'strong': return 'Strong - Great password!'
        default: return ''
      }
    })
    
    const passwordsMatch = computed(() => {
      return password.value && confirmPassword.value && password.value === confirmPassword.value
    })
    
    const formValid = computed(() => {
      return name.value.trim() !== '' &&
        email.value.trim() !== '' &&
        password.value.length >= 8 &&
        passwordsMatch.value &&
        termsAccepted.value
    })
    
    // Reset error message when form values change
    watch([name, email, password, confirmPassword], () => {
      error.value = ''
    })
    
    // Register function
    const register = async () => {
      if (!formValid.value) return
      
      isSubmitting.value = true
      error.value = ''
      
      try {
        await store.dispatch('auth/register', {
          username: name.value,
          email: email.value,
          password: password.value,
          role: accountType.value,
        })
        
        // If successful, redirect to onboarding
        router.push(`/auth/login?redirect=/`)
      } catch (err) {
        error.value = err.response?.data?.message || 'Registration failed. Please try again.'
      } finally {
        isSubmitting.value = false
      }
    }
    
    return {
      accountType,
      name,
      email,
      password,
      confirmPassword,
      termsAccepted,
      showPassword,
      showConfirmPassword,
      isSubmitting,
      error,
      passwordStrength,
      passwordStrengthText,
      passwordsMatch,
      formValid,
      register
    }
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  min-height: 100vh;
  background-color: #f8fafc;
}

.register-form-container {
  flex: 1;
  padding: 3rem;
  max-width: 600px;
  background-color: white;
  display: flex;
  flex-direction: column;
}

.form-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.5rem;
}

.form-subtitle {
  font-size: 1rem;
  color: #64748b;
  margin-bottom: 2rem;
}

.error-message {
  background-color: #fee2e2;
  color: #ef4444;
  padding: 1rem;
  border-radius: 0.375rem;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #1e293b;
}

.form-group input[type="text"],
.form-group input[type="email"],
.form-group input[type="password"] {
  padding: 0.75rem 1rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.375rem;
  font-size: 1rem;
  width: 100%;
  transition: border-color 0.2s;
}

.form-group input:focus {
  border-color: #3b82f6;
  outline: none;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.25);
}

.account-type-selector {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
}

.account-type-option {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1.25rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
}

.account-type-option:hover {
  border-color: #3b82f6;
}

.account-type-option.active {
  border-color: #3b82f6;
  background-color: rgba(59, 130, 246, 0.05);
}

.account-type-option i {
  font-size: 1.5rem;
  color: #3b82f6;
  margin-bottom: 0.5rem;
}

.account-type-option span {
  font-weight: 500;
  color: #1e293b;
}

.password-input-container {
  position: relative;
}

.toggle-password {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  color: #64748b;
  padding: 0;
  font-size: 1rem;
}

.password-strength {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
  font-size: 0.75rem;
}

.strength-indicator {
  height: 4px;
  width: 100px;
  border-radius: 2px;
  background-color: #e2e8f0;
  position: relative;
  overflow: hidden;
}

.strength-indicator::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  border-radius: 2px;
}

.strength-indicator.weak::before {
  background-color: #ef4444;
  width: 33%;
}

.strength-indicator.medium::before {
  background-color: #f59e0b;
  width: 66%;
}

.strength-indicator.strong::before {
  background-color: #10b981;
  width: 100%;
}

.password-match {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
  font-size: 0.75rem;
}

.password-match .fa-check {
  color: #10b981;
}

.password-match .fa-times {
  color: #ef4444;
}

.checkbox-group {
  flex-direction: row;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.checkbox-group input {
  width: 1rem;
  height: 1rem;
}

.checkbox-group label {
  font-size: 0.875rem;
  color: #334155;
}

.checkbox-group a {
  color: #3b82f6;
  text-decoration: none;
}

.register-button {
  margin-top: 1rem;
  padding: 0.875rem;
  background-color: #3b82f6;
  color: white;
  font-weight: 600;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.2s;
}

.register-button:hover:not(:disabled) {
  background-color: #2563eb;
}

.register-button:disabled {
  background-color: #94a3b8;
  cursor: not-allowed;
}

.register-button i {
  margin-right: 0.5rem;
}

.alternative-options {
  margin-top: 2rem;
  text-align: center;
  font-size: 0.9rem;
  color: #64748b;
}

.alternative-options a {
  color: #3b82f6;
  font-weight: 500;
  text-decoration: none;
}

/* Right side - Info */
.register-info {
  display: flex;
  flex: 1;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  align-items: center;
  justify-content: center;
  color: white;
  padding: 3rem;
}

.info-content {
  max-width: 500px;
}

.info-content h2 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 2rem;
}

.benefits {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  margin-bottom: 3rem;
}

.benefit {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.benefit i {
  font-size: 1.25rem;
  color: #a5f3fc;
}

.benefit span {
  font-size: 1.1rem;
}

.testimonial {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-top: 2rem;
}

.testimonial p {
  font-style: italic;
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.testimonial-author {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.testimonial-author img {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid white;
}

.testimonial-author h4 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.testimonial-author p {
  font-size: 0.875rem;
  margin: 0;
  opacity: 0.8;
}

/* Responsive styles */
@media (max-width: 1024px) {
  .register-container {
    flex-direction: column-reverse;
  }
  
  .register-form-container {
    max-width: 100%;
  }
  
  .register-info {
    padding: 2rem;
  }
}

@media (max-width: 640px) {
  .register-form-container {
    padding: 2rem 1.5rem;
  }
  
  .account-type-selector {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .form-title {
    font-size: 1.75rem;
  }
  
  .info-content h2 {
    font-size: 1.75rem;
  }
}
</style> 