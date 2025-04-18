<template>
  <div class="main-layout">
    <header class="main-header">
      <div class="container">
        <div class="header-content">
          <div class="logo">
            <router-link to="/">
              <h1>Sponnect</h1>
            </router-link>
          </div>
          <nav class="main-nav">
            <ul>
              <li><router-link to="/dashboard">Dashboard</router-link></li>
              <li><router-link to="/campaigns">Campaigns</router-link></li>
              <li><router-link to="/ad-requests">Ad Requests</router-link></li>
              <li><router-link to="/profile">Profile</router-link></li>
            </ul>
          </nav>
          <div class="user-menu">
            <button class="user-menu-button" @click="toggleUserMenu">
              <span class="avatar">{{ userInitials }}</span>
              <span class="username">{{ userName }}</span>
            </button>
            <div class="dropdown-menu" v-if="showUserMenu">
              <ul>
                <li><router-link to="/profile">My Profile</router-link></li>
                <li><router-link to="/settings">Settings</router-link></li>
                <li><button @click="logout">Log Out</button></li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </header>
    <main class="main-content">
      <router-view />
    </main>
    <footer class="main-footer">
      <div class="container">
        <p>&copy; {{ currentYear }} Sponnect. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

export default {
  name: 'MainLayout',
  
  setup() {
    const store = useStore();
    const router = useRouter();
    const showUserMenu = ref(false);
    
    const user = computed(() => store.getters['auth/user'] || {});
    
    const userName = computed(() => {
      return user.value.fullName || user.value.username || 'User';
    });
    
    const userInitials = computed(() => {
      if (!user.value.fullName) return 'U';
      
      const names = user.value.fullName.split(' ');
      if (names.length === 1) return names[0][0];
      return names[0][0] + names[names.length - 1][0];
    });
    
    const currentYear = computed(() => new Date().getFullYear());
    
    const toggleUserMenu = () => {
      showUserMenu.value = !showUserMenu.value;
    };
    
    const logout = async () => {
      await store.dispatch('auth/logout');
      router.push('/login');
    };
    
    return {
      showUserMenu,
      userName,
      userInitials,
      currentYear,
      toggleUserMenu,
      logout
    };
  }
};
</script>

<style scoped>
.main-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-header {
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 1rem 0;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo a {
  text-decoration: none;
  color: #333;
}

.logo h1 {
  font-size: 1.5rem;
  margin: 0;
}

.main-nav ul {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
}

.main-nav li {
  margin-left: 1.5rem;
}

.main-nav a {
  text-decoration: none;
  color: #333;
  font-weight: 500;
}

.main-nav a.router-link-active {
  color: #4a90e2;
}

.user-menu {
  position: relative;
}

.user-menu-button {
  display: flex;
  align-items: center;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #4a90e2;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 0.5rem;
  font-weight: bold;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  border-radius: 4px;
  min-width: 180px;
  z-index: 10;
  margin-top: 0.5rem;
}

.dropdown-menu ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.dropdown-menu li {
  padding: 0;
}

.dropdown-menu a, 
.dropdown-menu button {
  display: block;
  padding: 0.75rem 1rem;
  color: #333;
  text-decoration: none;
  width: 100%;
  text-align: left;
  background: none;
  border: none;
  cursor: pointer;
}

.dropdown-menu a:hover, 
.dropdown-menu button:hover {
  background-color: #f5f5f5;
}

.main-content {
  flex: 1;
  padding: 2rem 0;
}

.main-footer {
  background-color: #f5f5f5;
  padding: 1.5rem 0;
  text-align: center;
  color: #666;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}
</style> 