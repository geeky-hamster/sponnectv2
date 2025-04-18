import axios from 'axios';
import { useToast } from 'vue-toastification';

const state = {
  influencerRequests: [],
  sponsorRequests: [],
  currentRequest: null,
  negotiationHistory: []
};

const mutations = {
  SET_INFLUENCER_REQUESTS(state, requests) {
    state.influencerRequests = requests;
  },
  SET_SPONSOR_REQUESTS(state, requests) {
    state.sponsorRequests = requests;
  },
  SET_CURRENT_REQUEST(state, request) {
    state.currentRequest = request;
  },
  UPDATE_REQUEST(state, updatedRequest) {
    // Update in influencer list
    const infIndex = state.influencerRequests.findIndex(r => r.id === updatedRequest.id);
    if (infIndex !== -1) {
      state.influencerRequests.splice(infIndex, 1, updatedRequest);
    }
    
    // Update in sponsor list
    const sponIndex = state.sponsorRequests.findIndex(r => r.id === updatedRequest.id);
    if (sponIndex !== -1) {
      state.sponsorRequests.splice(sponIndex, 1, updatedRequest);
    }
    
    // Update current request if it's the same one
    if (state.currentRequest && state.currentRequest.id === updatedRequest.id) {
      state.currentRequest = updatedRequest;
    }
  },
  REMOVE_REQUEST(state, requestId) {
    state.influencerRequests = state.influencerRequests.filter(r => r.id !== requestId);
    state.sponsorRequests = state.sponsorRequests.filter(r => r.id !== requestId);
    if (state.currentRequest && state.currentRequest.id === requestId) {
      state.currentRequest = null;
    }
  },
  SET_NEGOTIATION_HISTORY(state, history) {
    state.negotiationHistory = history;
  }
};

const actions = {
  // Influencer actions
  async fetchInfluencerRequests({ commit, dispatch }, statusFilter = '') {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      const params = statusFilter ? { status: statusFilter } : {};
      const response = await axios.get('/influencer/ad_requests', { params });
      commit('SET_INFLUENCER_REQUESTS', response.data);
      dispatch('ui/setLoading', false, { root: true });
      return response.data;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to load ad requests.');
      dispatch('ui/setLoading', false, { root: true });
      return [];
    }
  },
  
  async influencerActionRequest({ commit, dispatch }, { requestId, action, data }) {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      const requestData = { action, ...data };
      const response = await axios.patch(`/influencer/ad_requests/${requestId}`, requestData);
      commit('UPDATE_REQUEST', response.data.ad_request);
      toast.success(response.data.message || 'Action completed successfully!');
      dispatch('ui/setLoading', false, { root: true });
      return response.data.ad_request;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to complete action.');
      dispatch('ui/setLoading', false, { root: true });
      return false;
    }
  },
  
  // Sponsor actions
  async fetchSponsorRequests({ commit, dispatch }, filters = {}) {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      const response = await axios.get('/sponsor/ad_requests', { params: filters });
      commit('SET_SPONSOR_REQUESTS', response.data);
      dispatch('ui/setLoading', false, { root: true });
      return response.data;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to load ad requests.');
      dispatch('ui/setLoading', false, { root: true });
      return [];
    }
  },
  
  async createAdRequest({ commit, dispatch }, { campaignId, requestData }) {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      const response = await axios.post(`/sponsor/campaigns/${campaignId}/ad_requests`, requestData);
      // We don't add this directly to sponsorRequests since they're loaded based on filters
      toast.success('Ad request sent successfully!');
      dispatch('ui/setLoading', false, { root: true });
      return response.data.ad_request;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to send ad request.');
      dispatch('ui/setLoading', false, { root: true });
      return false;
    }
  },
  
  async sponsorActionRequest({ commit, dispatch }, { requestId, action, data }) {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      const requestData = { action, ...data };
      const response = await axios.put(`/sponsor/ad_requests/${requestId}`, requestData);
      commit('UPDATE_REQUEST', response.data.ad_request);
      toast.success(response.data.message || 'Action completed successfully!');
      dispatch('ui/setLoading', false, { root: true });
      return response.data.ad_request;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to complete action.');
      dispatch('ui/setLoading', false, { root: true });
      return false;
    }
  },
  
  async deleteAdRequest({ commit, dispatch }, requestId) {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      await axios.delete(`/sponsor/ad_requests/${requestId}`);
      commit('REMOVE_REQUEST', requestId);
      toast.success('Ad request deleted successfully!');
      dispatch('ui/setLoading', false, { root: true });
      return true;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to delete ad request.');
      dispatch('ui/setLoading', false, { root: true });
      return false;
    }
  },
  
  // Negotiation history
  async fetchNegotiationHistory({ commit, dispatch }, requestId) {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      const response = await axios.get(`/ad_requests/${requestId}/history`);
      commit('SET_NEGOTIATION_HISTORY', response.data.history);
      dispatch('ui/setLoading', false, { root: true });
      return response.data;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to load negotiation history.');
      dispatch('ui/setLoading', false, { root: true });
      return { history: [] };
    }
  }
};

const getters = {
  influencerRequests: state => state.influencerRequests,
  sponsorRequests: state => state.sponsorRequests,
  currentRequest: state => state.currentRequest,
  negotiationHistory: state => state.negotiationHistory,
  getPendingRequests: state => (role) => {
    if (role === 'influencer') {
      return state.influencerRequests.filter(r => r.status === 'Pending');
    } else if (role === 'sponsor') {
      return state.sponsorRequests.filter(r => r.status === 'Pending');
    }
    return [];
  },
  getNegotiatingRequests: state => (role) => {
    if (role === 'influencer') {
      return state.influencerRequests.filter(r => r.status === 'Negotiating');
    } else if (role === 'sponsor') {
      return state.sponsorRequests.filter(r => r.status === 'Negotiating');
    }
    return [];
  }
};

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}; 