import axios from 'axios';
import { useToast } from 'vue-toastification';

// Initial state
const state = {
  token: localStorage.getItem('token') || '',
  currentUser: null,
  status: '',
};

// Mutations
const mutations = {
  AUTH_REQUEST(state) {
    state.status = 'loading';
  },
  AUTH_SUCCESS(state, token) {
    state.status = 'success';
    state.token = token;
  },
  AUTH_ERROR(state) {
    state.status = 'error';
    state.token = '';
  },
  SET_USER(state, user) {
    state.currentUser = user;
  },
  LOGOUT(state) {
    state.status = '';
    state.token = '';
    state.currentUser = null;
  }
};

// Actions
const actions = {
  async register({ commit, dispatch }, userData) {
    const toast = useToast();
    commit('AUTH_REQUEST');
    dispatch('ui/setLoading', true, { root: true });
    try {
      const response = await axios.post('/register', userData);
      toast.success(response.data.message || 'Registration successful!');
      dispatch('ui/setLoading', false, { root: true });
      return true;
    } catch (error) {
      commit('AUTH_ERROR');
      toast.error(error.response?.data?.message || 'Registration failed.');
      dispatch('ui/setLoading', false, { root: true });
      return false;
    }
  },
  
  async login({ commit, dispatch }, credentials) {
    const toast = useToast();
    commit('AUTH_REQUEST');
    dispatch('ui/setLoading', true, { root: true });
    try {
      const response = await axios.post('/login', credentials);
      const token = response.data.access_token;
      localStorage.setItem('token', token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      commit('AUTH_SUCCESS', token);
      await dispatch('fetchProfile');
      toast.success('Login successful!');
      dispatch('ui/setLoading', false, { root: true });
      return true;
    } catch (error) {
      commit('AUTH_ERROR');
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
      toast.error(error.response?.data?.message || 'Login failed.');
      dispatch('ui/setLoading', false, { root: true });
      return false;
    }
  },
  
  async fetchProfile({ commit, dispatch }) {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      const response = await axios.get('/profile');
      commit('SET_USER', response.data);
      dispatch('ui/setLoading', false, { root: true });
      return response.data;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to load profile.');
      dispatch('ui/setLoading', false, { root: true });
      throw error;
    }
  },
  
  async updateProfile({ commit, dispatch }, profileData) {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      const response = await axios.put('/profile', profileData);
      commit('SET_USER', response.data.profile);
      toast.success('Profile updated successfully!');
      dispatch('ui/setLoading', false, { root: true });
      return response.data.profile;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to update profile.');
      dispatch('ui/setLoading', false, { root: true });
      return false;
    }
  },
  
  logout({ commit }) {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    commit('LOGOUT');
    // No toast on normal logout
  },
  
  logoutAndRedirect({ commit }) {
    commit('LOGOUT');
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    // No toast on auto-logout
  }
};

// Getters
const getters = {
  isAuthenticated: state => !!state.token,
  currentUser: state => state.currentUser,
  authStatus: state => state.status,
  isAdmin: state => state.currentUser && state.currentUser.role === 'admin',
  isSponsor: state => state.currentUser && state.currentUser.role === 'sponsor',
  isInfluencer: state => state.currentUser && state.currentUser.role === 'influencer',
};

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}; 