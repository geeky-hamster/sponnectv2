import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from 'axios'

// Import Bootstrap CSS & JS
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

// Import Vue Toastification CSS & Plugin
import Toast, { POSITION } from 'vue-toastification'
import "vue-toastification/dist/index.css" // Default CSS

// Configure Axios (baseURL, interceptors)
axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

axios.interceptors.request.use(config => {
  const token = store.state.auth.token
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

axios.interceptors.response.use(response => response, error => {
  if (error.response && error.response.status === 401) {
    store.dispatch('auth/logoutAndRedirect')
  }
  // Do not automatically show generic toast here, let actions handle it
  return Promise.reject(error)
})

// Configure Vue Toastification Defaults
const toastOptions = {
    position: POSITION.TOP_RIGHT,
    timeout: 5000, // Milliseconds
    closeOnClick: true,
    pauseOnFocusLoss: true,
    pauseOnHover: true,
    draggable: true,
    draggablePercent: 0.6,
    showCloseButtonOnHover: false,
    hideProgressBar: false,
    closeButton: "button",
    icon: true,
    rtl: false,
    transition: "Vue-Toastification__bounce", // Or other built-in transitions
    maxToasts: 10,
    newestOnTop: true
}

const app = createApp(App)
app.use(router)
app.use(store)
app.use(Toast, toastOptions) // Use Toast plugin with options
app.mount('#app')
