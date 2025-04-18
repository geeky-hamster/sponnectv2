const state = {
  loading: false
};

const mutations = {
  SET_LOADING(state, isLoading) {
    state.loading = isLoading;
  }
};

const actions = {
  setLoading({ commit }, isLoading) {
    commit('SET_LOADING', isLoading);
  }
};

const getters = {
  isLoading: state => state.loading
};

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}; 