<template>
  <div class="reset-password-container">
    <div class="form-container">
      <h1 class="form-title">Create New Password</h1>
      <p class="form-subtitle">Please create a new password for your Sponnect account</p>
      
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      
      <div v-if="successMessage" class="success-message">
        <p>{{ successMessage }}</p>
        <div class="success-action">
          <router-link to="/auth/login" class="login-button">
            Go to Login
          </router-link>
        </div>
      </div>
      
      <form v-if="!successMessage" @submit.prevent="resetPassword" class="reset-form">
        <div class="form-group">
          <label for="password">New Password</label>
          <div class="password-input-container">
            <input 
              id="password" 
              v-model="password" 
              :type="showPassword ? 'text' : 'password'" 
              placeholder="Create a new password"
              required
              :disabled="isSubmitting"
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
            <div class="strength-meter">
              <div 
                class="strength-bar" 
                :style="{ width: `${passwordStrength.score * 25}%` }"
                :class="passwordStrengthClass"
              ></div>
            </div>
            <span class="strength-text" :class="passwordStrengthClass">
              {{ passwordStrength.message }}
            </span>
          </div>
          
          <div class="password-requirements">
            <p>Your password should contain:</p>
            <ul>
              <li :class="{ valid: password.length >= 8 }">
                <i :class="password.length >= 8 ? 'fas fa-check' : 'fas fa-times'"></i>
                At least 8 characters
              </li>
              <li :class="{ valid: /[A-Z]/.test(password) }">
                <i :class="/[A-Z]/.test(password) ? 'fas fa-check' : 'fas fa-times'"></i>
                At least one uppercase letter
              </li>
              <li :class="{ valid: /[a-z]/.test(password) }">
                <i :class="/[a-z]/.test(password) ? 'fas fa-check' : 'fas fa-times'"></i>
                At least one lowercase letter
              </li>
              <li :class="{ valid: /[0-9]/.test(password) }">
                <i :class="/[0-9]/.test(password) ? 'fas fa-check' : 'fas fa-times'"></i>
                At least one number
              </li>
              <li :class="{ valid: /[^A-Za-z0-9]/.test(password) }">
                <i :class="/[^A-Za-z0-9]/.test(password) ? 'fas fa-check' : 'fas fa-times'"></i>
                At least one special character
              </li>
            </ul>
          </div>
        </div>
        
        <div class="form-group">
          <label for="confirmPassword">Confirm Password</label>
          <div class="password-input-container">
            <input 
              id="confirmPassword" 
              v-model="confirmPassword" 
              :type="showConfirmPassword ? 'text' : 'password'" 
              placeholder="Confirm your new password"
              required
              :disabled="isSubmitting"
            />
            <button 
              type="button" 
              class="toggle-password" 
              @click="showConfirmPassword = !showConfirmPassword"
            >
              <i :class="showConfirmPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
            </button>
          </div>
          
          <div v-if="confirmPassword && password !== confirmPassword" class="password-match-error">
            <i class="fas fa-exclamation-circle"></i>
            Passwords do not match
          </div>
        </div>
        
        <button 
          type="submit" 
          class="submit-button" 
          :disabled="isSubmitting || !isFormValid"
        >
          <span v-if="!isSubmitting">Reset Password</span>
          <span v-else>
            <i class="fas fa-spinner fa-spin"></i> Processing...
          </span>
        </button>
      </form>
      
      <div class="alternative-options" v-if="!successMessage">
        <p>
          <router-link to="/auth/login">
            <i class="fas fa-arrow-left"></i> Back to Login
          </router-link>
        </p>
      </div>
    </div>
    
    <div class="info-container">
      <div class="info-content">
        <div class="logo-container">
          <img src="@/assets/vue.svg" alt="Sponnect Logo" class="logo" />
          <h2>Sponnect</h2>
        </div>
        
        <div class="security-section">
          <h3>Secure Your Account</h3>
          <p>Creating a strong password is an important step to protect your account and personal information.</p>
          
          <div class="security-tips">
            <div class="security-tip">
              <i class="fas fa-lock"></i>
              <div>
                <h4>Use a Unique Password</h4>
                <p>Avoid using the same password for multiple accounts to prevent unauthorized access.</p>
              </div>
            </div>
            
            <div class="security-tip">
              <i class="fas fa-shield-alt"></i>
              <div>
                <h4>Mix Characters</h4>
                <p>Combine letters, numbers, and special characters to create a strong password.</p>
              </div>
            </div>
            
            <div class="security-tip">
              <i class="fas fa-key"></i>
              <div>
                <h4>Consider a Password Manager</h4>
                <p>Use a trusted password manager to securely store and generate complex passwords.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'

export default {
  name: 'ResetPassword',
  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()
    
    // Get token from route params
    const token = route.params.token || route.query.token
    
    // Form data
    const password = ref('')
    const confirmPassword = ref('')
    
    // UI state
    const showPassword = ref(false)
    const showConfirmPassword = ref(false)
    const isSubmitting = ref(false)
    const error = ref('')
    const successMessage = ref('')
    
    // Password strength computation
    const passwordStrength = computed(() => {
      if (!password.value) {
        return { score: 0, message: '' }
      }
      
      let score = 0
      
      // Length check
      if (password.value.length >= 8) score++
      if (password.value.length >= 12) score++
      
      // Character variety checks
      if (/[A-Z]/.test(password.value)) score++
      if (/[a-z]/.test(password.value)) score++
      if (/[0-9]/.test(password.value)) score++
      if (/[^A-Za-z0-9]/.test(password.value)) score++
      
      // Normalize score to be out of 4
      score = Math.min(4, Math.floor(score / 1.5))
      
      const messages = [
        'Very weak',
        'Weak',
        'Fair',
        'Good',
        'Strong'
      ]
      
      return {
        score,
        message: messages[score]
      }
    })
    
    const passwordStrengthClass = computed(() => {
      const classes = ['very-weak', 'weak', 'fair', 'good', 'strong']
      return classes[passwordStrength.value.score]
    })
    
    // Form validation
    const isFormValid = computed(() => {
      return (
        password.value.length >= 8 &&
        /[A-Z]/.test(password.value) &&
        /[a-z]/.test(password.value) &&
        /[0-9]/.test(password.value) &&
        /[^A-Za-z0-9]/.test(password.value) &&
        password.value === confirmPassword.value
      )
    })
    
    // Reset password function
    const resetPassword = async () => {
      if (!isFormValid.value) return
      
      isSubmitting.value = true
      error.value = ''
      
      try {
        // Call the API to reset the password
        await store.dispatch('auth/resetPassword', {
          token,
          password: password.value
        })
        
        // Show success message
        successMessage.value = 'Your password has been successfully reset. You can now log in with your new password.'
      } catch (err) {
        error.value = err.response?.data?.message || 
          'Password reset failed. The link may have expired or is invalid. Please request a new password reset link.'
        
        if (error.value.includes('expired') || error.value.includes('invalid')) {
          setTimeout(() => {
            router.push('/auth/forgot-password')
          }, 3000)
        }
      } finally {
        isSubmitting.value = false
      }
    }
    
    // Validate token on page load
    const validateToken = async () => {
      if (!token) {
        error.value = 'Invalid or missing reset token. Please request a new password reset link.'
        setTimeout(() => {
          router.push('/auth/forgot-password')
        }, 3000)
        return
      }
      
      try {
        // Optional: Verify token validity before showing the form
        await store.dispatch('auth/validateResetToken', { token })
      } catch (err) {
        error.value = 'This password reset link has expired or is invalid. Please request a new one.'
        setTimeout(() => {
          router.push('/auth/forgot-password')
        }, 3000)
      }
    }
    
    // Validate token when component is mounted
    validateToken()
    
    return {
      password,
      confirmPassword,
      showPassword,
      showConfirmPassword,
      isSubmitting,
      error,
      successMessage,
      passwordStrength,
      passwordStrengthClass,
      isFormValid,
      resetPassword
    }
  }
}
</script>

<style scoped>
.reset-password-container {
  display: flex;
  min-height: 100vh;
  background-color: #f8fafc;
}

.form-container {
  flex: 1;
  padding: 3rem;
  max-width: 500px;
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
  line-height: 1.5;
}

.error-message {
  background-color: #fee2e2;
  color: #ef4444;
  padding: 1rem;
  border-radius: 0.375rem;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.success-message {
  background-color: #d1fae5;
  color: #059669;
  padding: 1.5rem;
  border-radius: 0.375rem;
  margin-bottom: 1.5rem;
  line-height: 1.5;
  font-size: 1.05rem;
}

.success-action {
  margin-top: 1.5rem;
  text-align: center;
}

.login-button {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  background-color: #059669;
  color: white;
  font-weight: 600;
  border: none;
  border-radius: 0.375rem;
  text-decoration: none;
  transition: background-color 0.2s;
}

.login-button:hover {
  background-color: #047857;
}

.reset-form {
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

.password-input-container {
  position: relative;
}

.password-input-container input {
  padding: 0.75rem 1rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.375rem;
  font-size: 1rem;
  width: 100%;
  transition: border-color 0.2s;
}

.password-input-container input:focus {
  border-color: #3b82f6;
  outline: none;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.25);
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
  margin-top: 0.75rem;
}

.strength-meter {
  height: 6px;
  background-color: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.strength-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s;
}

.strength-bar.very-weak {
  background-color: #ef4444;
}

.strength-bar.weak {
  background-color: #f97316;
}

.strength-bar.fair {
  background-color: #f59e0b;
}

.strength-bar.good {
  background-color: #84cc16;
}

.strength-bar.strong {
  background-color: #10b981;
}

.strength-text {
  font-size: 0.8rem;
  font-weight: 500;
}

.strength-text.very-weak {
  color: #ef4444;
}

.strength-text.weak {
  color: #f97316;
}

.strength-text.fair {
  color: #f59e0b;
}

.strength-text.good {
  color: #84cc16;
}

.strength-text.strong {
  color: #10b981;
}

.password-requirements {
  margin-top: 1rem;
  font-size: 0.85rem;
  background-color: #f8fafc;
  padding: 1rem;
  border-radius: 0.375rem;
  border: 1px solid #e2e8f0;
}

.password-requirements p {
  margin-bottom: 0.5rem;
  color: #475569;
  font-weight: 500;
}

.password-requirements ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.password-requirements li {
  display: flex;
  align-items: center;
  margin-bottom: 0.25rem;
  color: #64748b;
  gap: 0.5rem;
}

.password-requirements li i {
  width: 14px;
}

.password-requirements li.valid {
  color: #10b981;
}

.password-requirements li i.fa-check {
  color: #10b981;
}

.password-requirements li i.fa-times {
  color: #94a3b8;
}

.password-match-error {
  color: #ef4444;
  font-size: 0.85rem;
  margin-top: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.submit-button {
  padding: 0.875rem;
  background-color: #3b82f6;
  color: white;
  font-weight: 600;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.2s;
  margin-top: 1rem;
}

.submit-button:hover:not(:disabled) {
  background-color: #2563eb;
}

.submit-button:disabled {
  background-color: #94a3b8;
  cursor: not-allowed;
}

.alternative-options {
  margin-top: 2rem;
  text-align: center;
}

.alternative-options a {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.95rem;
}

/* Right side info section */
.info-container {
  display: flex;
  flex: 1;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  align-items: center;
  justify-content: center;
  padding: 3rem;
}

.info-content {
  max-width: 500px;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 3rem;
}

.logo {
  width: 3rem;
  height: auto;
}

.logo-container h2 {
  font-size: 2.25rem;
  font-weight: 700;
}

.security-section h3 {
  font-size: 1.75rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.security-section > p {
  font-size: 1.1rem;
  margin-bottom: 2.5rem;
  line-height: 1.6;
  opacity: 0.9;
}

.security-tips {
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
}

.security-tip {
  display: flex;
  gap: 1.25rem;
  align-items: flex-start;
}

.security-tip i {
  font-size: 1.5rem;
  color: #a5f3fc;
  margin-top: 0.25rem;
}

.security-tip h4 {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.security-tip p {
  font-size: 0.95rem;
  opacity: 0.9;
  line-height: 1.5;
}

/* Responsive styles */
@media (max-width: 1024px) {
  .reset-password-container {
    flex-direction: column-reverse;
  }
  
  .form-container {
    max-width: 100%;
  }
  
  .info-container {
    padding: 2rem;
  }
}

@media (max-width: 640px) {
  .form-container {
    padding: 2rem 1.5rem;
  }
  
  .form-title {
    font-size: 1.75rem;
  }
  
  .security-section h3 {
    font-size: 1.5rem;
  }
}
</style> 