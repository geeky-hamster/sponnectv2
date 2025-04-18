<template>
  <div class="forgot-password-container">
    <div class="form-container">
      <h1 class="form-title">Reset Your Password</h1>
      <p class="form-subtitle">Enter your email address and we'll send you a link to reset your password</p>
      
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      
      <div v-if="successMessage" class="success-message">
        {{ successMessage }}
      </div>
      
      <form @submit.prevent="requestPasswordReset" class="forgot-password-form" v-if="!successMessage">
        <div class="form-group">
          <label for="email">Email Address</label>
          <input 
            id="email" 
            v-model="email" 
            type="email" 
            placeholder="Enter your email address"
            required
            :disabled="isSubmitting"
          />
        </div>
        
        <button 
          type="submit" 
          class="submit-button" 
          :disabled="isSubmitting || !email"
        >
          <span v-if="!isSubmitting">Send Reset Link</span>
          <span v-else>
            <i class="fas fa-spinner fa-spin"></i> Sending...
          </span>
        </button>
      </form>
      
      <div class="alternative-options">
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
        
        <div class="help-section">
          <h3>Trouble Logging In?</h3>
          <p>Don't worry, we'll help you regain access to your account. After entering your email, you'll receive a secure link to reset your password.</p>
          
          <div class="instructions">
            <div class="instruction-step">
              <div class="step-number">1</div>
              <div class="step-text">
                <h4>Enter Your Email</h4>
                <p>Provide the email address associated with your Sponnect account.</p>
              </div>
            </div>
            
            <div class="instruction-step">
              <div class="step-number">2</div>
              <div class="step-text">
                <h4>Check Your Inbox</h4>
                <p>We'll send a secure password reset link to your email.</p>
              </div>
            </div>
            
            <div class="instruction-step">
              <div class="step-number">3</div>
              <div class="step-text">
                <h4>Create New Password</h4>
                <p>Follow the link to create a new, strong password for your account.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'ForgotPassword',
  setup() {
    const store = useStore()
    
    const email = ref('')
    const isSubmitting = ref(false)
    const error = ref('')
    const successMessage = ref('')
    
    const requestPasswordReset = async () => {
      if (!email.value) return
      
      isSubmitting.value = true
      error.value = ''
      
      try {
        // Call the API to request a password reset
        await store.dispatch('auth/requestPasswordReset', { email: email.value })
        
        // Show success message
        successMessage.value = `We've sent a password reset link to ${email.value}. Please check your email and follow the instructions to reset your password.`
      } catch (err) {
        error.value = err.response?.data?.message || 'Failed to send reset link. Please try again later.'
      } finally {
        isSubmitting.value = false
      }
    }
    
    return {
      email,
      isSubmitting,
      error,
      successMessage,
      requestPasswordReset
    }
  }
}
</script>

<style scoped>
.forgot-password-container {
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
}

.success-message {
  background-color: #d1fae5;
  color: #059669;
  padding: 1rem;
  border-radius: 0.375rem;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.forgot-password-form {
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

.form-group input {
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

.alternative-options i {
  font-size: 0.875rem;
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

.help-section h3 {
  font-size: 1.75rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.help-section > p {
  font-size: 1.1rem;
  margin-bottom: 2.5rem;
  line-height: 1.6;
  opacity: 0.9;
}

.instructions {
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
}

.instruction-step {
  display: flex;
  gap: 1.25rem;
}

.step-number {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 2.5rem;
  height: 2.5rem;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  font-size: 1.25rem;
  font-weight: 700;
}

.step-text h4 {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.step-text p {
  font-size: 0.95rem;
  opacity: 0.9;
  line-height: 1.5;
}

/* Responsive styles */
@media (max-width: 1024px) {
  .forgot-password-container {
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
  
  .help-section h3 {
    font-size: 1.5rem;
  }
}
</style> 