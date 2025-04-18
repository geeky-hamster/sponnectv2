<template>
  <div class="auth-layout">
    <div class="auth-container">
      <div class="logo">
        <router-link to="/">
          <h1>Sponnect</h1>
        </router-link>
      </div>
      
      <div class="auth-box">
        <router-view />
      </div>
      
      <div class="auth-footer">
        <p>&copy; {{ currentYear }} Sponnect. All rights reserved.</p>
        <div class="auth-links">
          <router-link to="/terms">Terms of Service</router-link>
          <router-link to="/privacy">Privacy Policy</router-link>
          <router-link to="/help">Help Center</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue';

export default {
  name: 'AuthLayout',
  
  setup() {
    const currentYear = computed(() => new Date().getFullYear());
    
    return {
      currentYear
    };
  }
};
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
  padding: 2rem 1rem;
}

.auth-container {
  width: 100%;
  max-width: 480px;
  text-align: center;
}

.logo {
  margin-bottom: 2rem;
}

.logo a {
  text-decoration: none;
  color: #333;
}

.logo h1 {
  font-size: 2rem;
  margin: 0;
}

.auth-box {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  margin-bottom: 2rem;
}

.auth-footer {
  color: #666;
  font-size: 0.875rem;
}

.auth-links {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-top: 0.5rem;
}

.auth-links a {
  color: #4a90e2;
  text-decoration: none;
}

.auth-links a:hover {
  text-decoration: underline;
}

@media (max-width: 640px) {
  .auth-box {
    padding: 1.5rem;
  }
  
  .auth-links {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style> 