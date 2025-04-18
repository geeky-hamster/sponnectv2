<template>
  <div class="not-found-page">
    <div class="not-found-content">
      <div class="error-code">404</div>
      <h1 class="title">Page Not Found</h1>
      <p class="message">
        Oops! The page you are looking for doesn't exist or has been moved.
      </p>
      <div class="actions">
        <button @click="goBack" class="back-button">
          <i class="fas fa-arrow-left"></i> Go Back
        </button>
        <router-link to="/" class="home-button">
          Go to Dashboard
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router';

export default {
  name: 'NotFound',
  
  setup() {
    const router = useRouter();
    
    const goBack = () => {
      router.go(-1);
    };
    
    return {
      goBack
    };
  }
};
</script>

<style scoped>
.not-found-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: #f9fafb;
  padding: 2rem;
}

.not-found-content {
  max-width: 500px;
  text-align: center;
  background-color: white;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 3rem 2rem;
}

.error-code {
  font-size: 6rem;
  font-weight: 800;
  color: #3b82f6;
  line-height: 1;
  margin-bottom: 1rem;
}

.title {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 1rem;
}

.message {
  color: #6b7280;
  font-size: 1.125rem;
  margin-bottom: 2rem;
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.back-button, .home-button {
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
  font-size: 1rem;
  cursor: pointer;
  text-align: center;
  text-decoration: none;
}

.back-button {
  background-color: #f3f4f6;
  color: #4b5563;
  border: none;
}

.home-button {
  background-color: #3b82f6;
  color: white;
  border: none;
}

.back-button:hover {
  background-color: #e5e7eb;
}

.home-button:hover {
  background-color: #2563eb;
}

@media (min-width: 640px) {
  .actions {
    flex-direction: row;
    justify-content: center;
  }
}
</style> 