import axios from 'axios';
import { useToast } from 'vue-toastification';

const state = {
  stats: null,
  pendingSponsors: [],
  chartData: {
    userGrowth: null,
    campaignDistribution: null,
    adRequestStatus: null,
    campaignActivity: null,
    conversionRates: null,
    dashboardSummary: null
  }
};

const mutations = {
  SET_STATS(state, res_stats) {
    state.stats = res_stats;
  },
  SET_PENDING_SPONSORS(state, sponsors) {
    state.pendingSponsors = sponsors;
  },
  SET_CHART_DATA(state, { chartType, data }) {
    state.chartData[chartType] = data;
  }
};

const actions = {
  async fetchAdminStats({ commit }) {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      const resp = await axios.get('/api/admin/stats').then(resp => {
      commit('SET_STATS', resp.data)});
      dispatch('ui/setLoading', false, { root: true });
      return resp.data;
    } catch (error) {
      console.error('Error in fetchAdminStats:', error); // Log the error
      toast.error(error.response?.data?.message || 'Failed to load admin statistics.');
      dispatch('ui/setLoading', false, { root: true });
      return null;
    }
  },
  
  async fetchPendingSponsors({ commit, dispatch }) {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      const response = await axios.get('/api/admin/pending_sponsors');
      console.log('Dashboard API Response:', response.data);
      commit('SET_PENDING_SPONSORS', response.data);
      dispatch('ui/setLoading', false, { root: true });
      return response.data;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to load pending sponsors.');
      dispatch('ui/setLoading', false, { root: true });
      return [];
    }
  },
  
  async approveSponsor({ dispatch }, sponsorId) {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      const response = await axios.patch(`/api/admin/sponsors/${sponsorId}/approve`);
      await dispatch('fetchPendingSponsors'); // Refresh list
      toast.success('Sponsor approved successfully!');
      dispatch('ui/setLoading', false, { root: true });
      return true;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to approve sponsor.');
      dispatch('ui/setLoading', false, { root: true });
      return false;
    }
  },
  
  async rejectSponsor({ dispatch }, sponsorId) {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      const response = await axios.patch(`/api/admin/sponsors/${sponsorId}/reject`);
      await dispatch('fetchPendingSponsors'); // Refresh list
      toast.success('Sponsor rejected successfully!');
      dispatch('ui/setLoading', false, { root: true });
      return true;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to reject sponsor.');
      dispatch('ui/setLoading', false, { root: true });
      return false;
    }
  },
  
  async flagUser({ dispatch }, userId) {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      await axios.patch(`/api/admin/users/${userId}/flag`);
      toast.success('User flagged successfully!');
      dispatch('ui/setLoading', false, { root: true });
      return true;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to flag user.');
      dispatch('ui/setLoading', false, { root: true });
      return false;
    }
  },
  
  async unflagUser({ dispatch }, userId) {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      await axios.patch(`/api/admin/users/${userId}/unflag`);
      toast.success('User unflagged successfully!');
      dispatch('ui/setLoading', false, { root: true });
      return true;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to unflag user.');
      dispatch('ui/setLoading', false, { root: true });
      return false;
    }
  },
  
  async flagCampaign({ dispatch }, campaignId) {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      await axios.patch(`/api/admin/campaigns/${campaignId}/flag`);
      toast.success('Campaign flagged successfully!');
      dispatch('ui/setLoading', false, { root: true });
      return true;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to flag campaign.');
      dispatch('ui/setLoading', false, { root: true });
      return false;
    }
  },
  
  async unflagCampaign({ dispatch }, campaignId) {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      await axios.patch(`/api/admin/campaigns/${campaignId}/unflag`);
      toast.success('Campaign unflagged successfully!');
      dispatch('ui/setLoading', false, { root: true });
      return true;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to unflag campaign.');
      dispatch('ui/setLoading', false, { root: true });
      return false;
    }
  },
  
  // Chart data actions
  async fetchUserGrowthChart({ commit, dispatch }) {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      const response = await axios.get('/api/charts/user-growth');
      commit('SET_CHART_DATA', { chartType: 'userGrowth', data: response.data });
      dispatch('ui/setLoading', false, { root: true });
      return response.data;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to load user growth chart data.');
      dispatch('ui/setLoading', false, { root: true });
      return null;
    }
  },
  
  async fetchCampaignDistributionChart({ commit, dispatch }) {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      const response = await axios.get('/api/charts/campaign-distribution');
      commit('SET_CHART_DATA', { chartType: 'campaignDistribution', data: response.data });
      dispatch('ui/setLoading', false, { root: true });
      return response.data;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to load campaign distribution chart data.');
      dispatch('ui/setLoading', false, { root: true });
      return null;
    }
  },
  
  async fetchAdRequestStatusChart({ commit, dispatch }) {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      const response = await axios.get('/api/charts/ad-request-status');
      commit('SET_CHART_DATA', { chartType: 'adRequestStatus', data: response.data });
      dispatch('ui/setLoading', false, { root: true });
      return response.data;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to load ad request status chart data.');
      dispatch('ui/setLoading', false, { root: true });
      return null;
    }
  },
  
  async fetchCampaignActivityChart({ commit, dispatch }) {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      const response = await axios.get('/api/charts/campaign-activity');
      commit('SET_CHART_DATA', { chartType: 'campaignActivity', data: response.data });
      dispatch('ui/setLoading', false, { root: true });
      return response.data;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to load campaign activity chart data.');
      dispatch('ui/setLoading', false, { root: true });
      return null;
    }
  },
  
  async fetchConversionRatesChart({ commit, dispatch }) {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      const response = await axios.get('/api/charts/conversion-rates');
      commit('SET_CHART_DATA', { chartType: 'conversionRates', data: response.data });
      dispatch('ui/setLoading', false, { root: true });
      return response.data;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to load conversion rates chart data.');
      dispatch('ui/setLoading', false, { root: true });
      return null;
    }
  },
  
  async fetchDashboardSummary({ commit, dispatch }) {
    const toast = useToast();
    dispatch('ui/setLoading', true, { root: true });
    try {
      const response = await axios.get('/api/charts/dashboard-summary');
      commit('SET_CHART_DATA', { chartType: 'dashboardSummary', data: response.data });
      dispatch('ui/setLoading', false, { root: true });
      return response.data;
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to load dashboard summary data.');
      dispatch('ui/setLoading', false, { root: true });
      return null;
    }
  }
};

const getters = {
  adminStats: state => {
    console.log('Stats Getter:', state.stats);
    return state.stats || {};
  },
  pendingSponsors: state => {
    console.log('Pending Sponsors:', state.pendingSponsors);
    return state.pendingSponsors || [];
  },
  chartData: state => {
    console.log('Chart Data:', state.chartData);
    return state.chartData || { userGrowth: [], campaignActivity: [] };
  },
};

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}; 