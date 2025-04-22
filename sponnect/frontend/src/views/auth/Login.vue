<template>
  <div class="login-container">
    <div class="login-form-container">
      <h1 class="form-title">Welcome Back</h1>
      <p class="form-subtitle">Sign in to your Sponnect account</p>
      
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      
      <form @submit.prevent="login" class="login-form">
        <div class="form-group">
          <label for="email">Username or Email Address</label>
          <input 
            id="email" 
            v-model="username" 
            placeholder="Enter your email address or username"
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
              placeholder="Enter your password"
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
        </div>
        
        <div class="form-options">
          <div class="remember-me">
            <input id="remember" v-model="rememberMe" type="checkbox" />
            <label for="remember">Remember me</label>
          </div>
          <router-link to="/auth/forgot-password" class="forgot-password">
            Forgot password?
          </router-link>
        </div>
        
        <button 
          type="submit" 
          class="login-button" 
          :disabled="isSubmitting"
        >
          <span v-if="!isSubmitting">Sign In</span>
          <span v-else>
            <i class="fas fa-spinner fa-spin"></i> Signing in...
          </span>
        </button>
      </form>
      
      
      <div class="alternative-options">
        <p>
          Don't have an account? <router-link to="/auth/register">Create Account</router-link>
        </p>
      </div>
    </div>
    
    <div class="login-info">
      <div class="info-content">
        <div class="logo-container">
          <img src="@/assets/logo.png" alt="Sponnect Logo" class="logo" />
          <h2>Sponnect</h2>
        </div>
        
        <div class="feature-highlights">
          <h3>The Influencer Marketing Platform</h3>
          <p>Connect brands with authentic influencers for impactful marketing campaigns.</p>
          
          <div class="features">
            <div class="feature">
              <i class="fas fa-handshake"></i>
              <div>
                <h4>Seamless Collaboration</h4>
                <p>From discovery to payment, all in one platform.</p>
              </div>
            </div>
            <div class="feature">
              <i class="fas fa-chart-line"></i>
              <div>
                <h4>Performance Analytics</h4>
                <p>Track campaign metrics and measure ROI in real-time.</p>
              </div>
            </div>
            <div class="feature">
              <i class="fas fa-shield-alt"></i>
              <div>
                <h4>Secure Transactions</h4>
                <p>Protected payments and verified profiles.</p>
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
import { useRouter, useRoute } from 'vue-router'

export default {
  name: 'Login',
  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()
    
    // Form data
    const username = ref('')
    const password = ref('')
    const rememberMe = ref(false)
    
    // UI state
    const showPassword = ref(false)
    const isSubmitting = ref(false)
    const error = ref('')
    
    // Check for redirect message
    if (route.query.message) {
      error.value = route.query.message
    }
    
    // Login function
    const login = async () => {
      if (!username.value || !password.value) return
      
      isSubmitting.value = true
      error.value = ''
      
      try {
        await store.dispatch('auth/login', {
          username: username.value,
          password: password.value,
          remember: rememberMe.value
        })
        
        // Get redirect path or default based on user role
        const userRole = store.getters['auth/userRole'];
        const redirectPath = 
          userRole === 'admin' ? '/app/admin' : 
          userRole === 'sponsor' ? '/app/sponsor/dashboard' : 
          userRole === 'influencer' ? '/app/influencer/dashboard' : '/';
        
        router.push(redirectPath)
      } catch (err) {
        error.value = err.response?.data?.message || 'Login failed. Please check your credentials and try again.'
      } finally {
        isSubmitting.value = false
      }
    }
    
    // Social login function
    const socialLogin = async (provider) => {
      try {
        // Open OAuth popup or redirect
        window.location.href = `${process.env.VUE_APP_API_URL}/auth/${provider}`
      } catch (err) {
        error.value = `${provider} login failed. Please try again.`
      }
    }
    
    return {
      username,
      password,
      rememberMe,
      showPassword,
      isSubmitting,
      error,
      login,
      socialLogin
    }
  }
}
</script>

<style scoped>

.login-container {
  display: flex;
  min-height: 100vh;
}

.login-form-container {
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
  color: #01122e;
  margin-bottom: 0.5rem;
}

.form-subtitle {
  font-size: 1rem;
  color: #001532;
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

.login-form {
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
  color: #001536;
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

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.remember-me input {
  width: 1rem;
  height: 1rem;
}

.forgot-password {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
}

.login-button {
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

.login-button:hover:not(:disabled) {
  background-color: #2563eb;
}

.login-button:disabled {
  background-color: #94a3b8;
  cursor: not-allowed;
}

.login-button i {
  margin-right: 0.5rem;
}

.alternative-login {
  margin-top: 2rem;
}

.divider {
  display: flex;
  align-items: center;
  margin: 1.5rem 0;
}

.divider::before, 
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #e2e8f0;
}

.divider span {
  padding: 0 1rem;
  color: #001532;
  font-size: 0.875rem;
}

.social-login-buttons {
  display: flex;
  gap: 1rem;
}

.social-button {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  background-color: white;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s, border-color 0.2s;
}

.social-button.google:hover {
  background-color: #f8f9fa;
  border-color: #ea4335;
}

.social-button.facebook:hover {
  background-color: #f8f9fa;
  border-color: #1877f2;
}

.social-button i.fa-google {
  color: #ea4335;
}

.social-button i.fa-facebook-f {
  color: #1877f2;
}

.alternative-options {
  margin-top: 2rem;
  text-align: center;
  font-size: 0.9rem;
  color: #001533;
}

.alternative-options a {
  color: #3b82f6;
  font-weight: 500;
  text-decoration: none;
}

/* Right side - Info */
.login-info {
  display: flex;
  flex: 1;
  background-image: url(https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExZnp2aHoxY3NrdjFuaGJ5Yzc4ZDFwZm85amVidDJiZHFtczM4ODF3diZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/PXApia9fVviiWREDRq/giphy.gif) !important;
  background-size: 472px;
  align-items: center;
  justify-content: center;
  color: white;
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

.feature-highlights h3 {
  font-size: 1.75rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.feature-highlights > p {
  font-size: 1.1rem;
  margin-bottom: 2.5rem;
  line-height: 1.6;
  opacity: 0.9;
}

.features {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.feature {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.feature i {
  font-size: 1.5rem;
  color: #a5f3fc;
  margin-top: 0.25rem;
}

.feature h4 {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.feature p {
  font-size: 0.95rem;
  opacity: 0.9;
  line-height: 1.5;
}

/* Responsive styles */
@media (max-width: 1024px) {
  .login-container {
    flex-direction: column-reverse;
  }
  
  .login-form-container {
    max-width: 100%;
  }
  
  .login-info {
    padding: 2rem;
  }
}

@media (max-width: 640px) {
  .login-form-container {
    padding: 2rem 1.5rem;
  }
  
  .social-login-buttons {
    flex-direction: column;
  }
  
  .form-title {
    font-size: 1.75rem;
  }
  
  .feature-highlights h3 {
    font-size: 1.5rem;
  }
}
</style> 