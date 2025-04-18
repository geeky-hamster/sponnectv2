import axios from 'axios';
import { useToast } from 'vue-toastification';

const state = {
  campaigns: [],
  currentCampaign: null,
  publicCampaigns: []
};

const mutations = {
  SET_CAMPAIGNS(state, campaigns) {
    state.campaigns = campaigns;
  },
  SET_CURRENT_CAMPAIGN(state, campaign) {
    state.currentCampaign = campaign;
  },
  ADD_CAMPAIGN(state, campaign) {
    state.campaigns.unshift(campaign);
  },
  UPDATE_CAMPAIGN(state, updatedCampaign) {
    const index = state.campaigns.findIndex(c => c.id === updatedCampaign.id);
    if (index !== -1) {
      state.campaigns.splice(index, 1, updatedCampaign);
    }
    if (state.currentCampaign && state.currentCampaign.id === updatedCampaign.id) {
      state.currentCampaign = updatedCampaign;
    }
  },
  REMOVE_CAMPAIGN(state, campaignId) {
    state.campaigns = state.campaigns.filter(c => c.id !== campaignId);
    if (state.currentCampaign && state.currentCampaign.id === campaignId) {
      state.currentCampaign = null;
    }
  },
  SET_PUBLIC_CAMPAIGNS(state, campaigns) {
    state.publicCampaigns = campaigns;
  }
};

const actions = {
  // Sponsor actions
  async fetchSponsorCampaigns({ commit, dispatch }) {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      const response = await axios.get('/sponsor/campaigns');
      commit('SET_CAMPAIGNS', response.data);
      dispatch('ui/setLoading', false, { root: true });
      return response.data;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to load campaigns.');
      dispatch('ui/setLoading', false, { root: true });
      return [];
    }
  },
  
  async fetchCampaign({ commit, dispatch }, campaignId) {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      const response = await axios.get(`/sponsor/campaigns/${campaignId}`);
      commit('SET_CURRENT_CAMPAIGN', response.data);
      dispatch('ui/setLoading', false, { root: true });
      return response.data;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to load campaign details.');
      dispatch('ui/setLoading', false, { root: true });
      return null;
    }
  },
  
  async createCampaign({ commit, dispatch }, campaignData) {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      const response = await axios.post('/sponsor/campaigns', campaignData);
      commit('ADD_CAMPAIGN', response.data.campaign);
      toast.success('Campaign created successfully!');
      dispatch('ui/setLoading', false, { root: true });
      return response.data.campaign;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to create campaign.');
      dispatch('ui/setLoading', false, { root: true });
      return false;
    }
  },
  
  async updateCampaign({ commit, dispatch }, { campaignId, campaignData }) {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      const response = await axios.put(`/sponsor/campaigns/${campaignId}`, campaignData);
      commit('UPDATE_CAMPAIGN', response.data.campaign);
      toast.success('Campaign updated successfully!');
      dispatch('ui/setLoading', false, { root: true });
      return response.data.campaign;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to update campaign.');
      dispatch('ui/setLoading', false, { root: true });
      return false;
    }
  },
  
  async deleteCampaign({ commit, dispatch }, campaignId) {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      await axios.delete(`/sponsor/campaigns/${campaignId}`);
      commit('REMOVE_CAMPAIGN', campaignId);
      toast.success('Campaign deleted successfully!');
      dispatch('ui/setLoading', false, { root: true });
      return true;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to delete campaign.');
      dispatch('ui/setLoading', false, { root: true });
      return false;
    }
  },
  
  // Influencer actions
  async searchPublicCampaigns({ commit, dispatch }, searchParams = {}) {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      const response = await axios.get('/search/campaigns', { params: searchParams });
      commit('SET_PUBLIC_CAMPAIGNS', response.data);
      dispatch('ui/setLoading', false, { root: true });
      return response.data;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to search campaigns.');
      dispatch('ui/setLoading', false, { root: true });
      return [];
    }
  },
  
  async applyCampaign({ dispatch }, { campaignId, applicationData }) {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      const response = await axios.post(`/influencer/campaigns/${campaignId}/apply`, applicationData);
      toast.success('Application submitted successfully!');
      dispatch('ui/setLoading', false, { root: true });
      return response.data.ad_request;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to submit application.');
      dispatch('ui/setLoading', false, { root: true });
      return false;
    }
  }
};

const getters = {
  allCampaigns: state => state.campaigns,
  currentCampaign: state => state.currentCampaign,
  publicCampaigns: state => state.publicCampaigns,
  getCampaignById: state => id => state.campaigns.find(campaign => campaign.id === id)
};

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}; 