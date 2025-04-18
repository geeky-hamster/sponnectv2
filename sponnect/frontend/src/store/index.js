import { createStore } from 'vuex';
import auth from './modules/auth';
import campaigns from './modules/campaigns';
import adRequests from './modules/adRequests';
import admin from './modules/admin';
import ui from './modules/ui';

export default createStore({
  modules: {
    auth,
    campaigns,
    adRequests,
    admin,
    ui
  }
}); 