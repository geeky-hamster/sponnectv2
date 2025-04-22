// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import store from '../store';

// Layouts
import MainLayout from '../layouts/MainLayout.vue';
import AuthLayout from '../layouts/AuthLayout.vue';
import LandingPage from "@/views/LandingPage.vue";

// Auth Views
import Login from '../views/auth/Login.vue';
import Register from '../views/auth/Register.vue';
import ForgotPassword from '../views/auth/ForgotPassword.vue';

// Main Views
import Dashboard from '../views/Dashboard.vue';
import Profile from '../views/Profile.vue';

// Sponsor Views
import SponsorCampaigns from '../views/sponsor/Campaigns.vue';
import SponsorCreateCampaign from '../views/sponsor/CreateCampaign.vue';
import SponsorEditCampaign from '../views/sponsor/EditCampaign.vue';
import SponsorAdRequests from '../views/sponsor/AdRequests.vue';
import SponsorAdRequestDetail from '../views/sponsor/AdRequestDetail.vue';

// Influencer Views
import InfluencerCampaigns from '../views/influencer/Campaigns.vue';
import InfluencerAdRequests from '../views/influencer/AdRequests.vue';
import InfluencerAdRequestDetail from '../views/influencer/AdRequestDetail.vue';

// Admin Views
import AdminDashboard from '../views/admin/Dashboard.vue';
import AdminUsers from '../views/admin/Users.vue';
import AdminCampaigns from '../views/admin/Campaigns.vue';
import AdminAdRequests from '../views/admin/AdRequests.vue';
import AdminSponsors from '../views/admin/Sponsors.vue';

// Shared Views
import CampaignDetail from '../views/CampaignDetail.vue';
import NotFound from '../views/NotFound.vue';

const routes = [
  // Landing page
  { path: "/",
    name: "LandingPage", 
    component: LandingPage,
    meta: { title: "Welcome to Sponnect" },
  },

  {
    path: '/app',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      // Dashboard - Role-specific redirect
      {
        path: '',
        name: 'Dashboard',
        component: Dashboard,
        meta: { title: 'Dashboard' }
      },

      
      
      // Profile
      {
        path: 'profile',
        name: 'Profile',
        component: Profile,
        meta: { title: 'My Profile' }
      },
      
      // Sponsor routes
      {
        path: 'sponsor/campaigns',
        name: 'SponsorCampaigns',
        component: SponsorCampaigns,
        meta: { requiresRole: 'sponsor', title: 'Your Campaigns' }
      },
      {
        path: 'sponsor/campaigns/create',
        name: 'SponsorCreateCampaign',
        component: SponsorCreateCampaign,
        meta: { requiresRole: 'sponsor', title: 'Create Campaign' }
      },
      {
        path: 'sponsor/campaigns/:id/edit',
        name: 'SponsorEditCampaign',
        component: SponsorEditCampaign,
        meta: { requiresRole: 'sponsor', title: 'Edit Campaign' }
      },
      {
        path: 'sponsor/campaigns/:id',
        name: 'SponsorCampaignDetail',
        component: CampaignDetail,
        meta: { requiresRole: 'sponsor', title: 'Campaign Details' }
      },
      {
        path: 'sponsor/requests',
        name: 'SponsorAdRequests',
        component: SponsorAdRequests,
        meta: { requiresRole: 'sponsor', title: 'Ad Requests' }
      },
      {
        path: 'sponsor/requests/:id',
        name: 'SponsorAdRequestDetail',
        component: SponsorAdRequestDetail,
        meta: { requiresRole: 'sponsor', title: 'Ad Request Details' }
      },
      
      // Influencer routes
      {
        path: 'influencer/campaigns',
        name: 'InfluencerCampaigns',
        component: InfluencerCampaigns,
        meta: { requiresRole: 'influencer', title: 'Browse Campaigns' }
      },
      {
        path: 'influencer/campaigns/:id',
        name: 'InfluencerCampaignDetail',
        component: CampaignDetail,
        meta: { requiresRole: 'influencer', title: 'Campaign Details' }
      },
      {
        path: 'influencer/requests',
        name: 'InfluencerAdRequests',
        component: InfluencerAdRequests,
        meta: { requiresRole: 'influencer', title: 'Your Ad Requests' }
      },
      {
        path: 'influencer/requests/:id',
        name: 'InfluencerAdRequestDetail',
        component: InfluencerAdRequestDetail,
        meta: { requiresRole: 'influencer', title: 'Ad Request Details' }
      },
      
      // Admin routes
      {
        path: 'admin',
        name: 'AdminDashboard',
        component: AdminDashboard,
        meta: { requiresRole: 'admin', title: 'Admin Dashboard' }
      },
      {
        path: 'admin/users',
        name: 'AdminUsers',
        component: AdminUsers,
        meta: { requiresRole: 'admin', title: 'User Management' }
      },
      {
        path: 'admin/campaigns',
        name: 'AdminCampaigns',
        component: AdminCampaigns,
        meta: { requiresRole: 'admin', title: 'Campaign Management' }
      },
      {
        path: 'admin/requests',
        name: 'AdminAdRequests',
        component: AdminAdRequests,
        meta: { requiresRole: 'admin', title: 'Ad Request Management' }
      },
      {
        path: 'admin/sponsors',
        name: 'AdminSponsors',
        component: AdminSponsors,
        meta: { requiresRole: 'admin', title: 'Sponsor Approval' }
      }
    ]
  },
  
  // Auth routes
  {
    path: '/auth',
    component: AuthLayout,
    meta: { requiresGuest: true },
    children: [
      {
        path: 'login',
        name: 'Login',
        component: Login,
        meta: { title: 'Login' }
      },
      {
        path: 'register',
        name: 'Register',
        component: Register,
        meta: { title: 'Sign Up' }
      },
      {
        path: 'forgot-password',
        name: 'ForgotPassword',
        component: ForgotPassword,
        meta: { title: 'Forgot Password' }
      }
    ]
  },
  
  // Catch-all 404
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: { title: 'Page Not Found' }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
    }
  }
});

// Navigation guards
router.beforeEach((to, from, next) => {
  // Set document title
  document.title = to.meta.title ? `${to.meta.title} | Sponnect` : 'Sponnect';
  
  const isLoggedIn = store.getters['auth/isAuthenticated'];
  
  // Allow access to LandingPage without authentication
  if (to.name === 'LandingPage') {
    next();
    return;
  }

  // Handle auth required routes
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isLoggedIn) {
      next({ name: 'Login', query: { redirect: to.fullPath } });
      return;
    }
    
    // Check role requirements
    if (to.matched.some(record => record.meta.requiresRole)) {
      const requiredRole = to.matched.find(record => record.meta.requiresRole).meta.requiresRole;
      
      // Check if user has the required role
      const hasRole = 
        (requiredRole === 'admin' && store.getters['auth/isAdmin']) ||
        (requiredRole === 'sponsor' && store.getters['auth/isSponsor']) ||
        (requiredRole === 'influencer' && store.getters['auth/isInfluencer']);
        console.log('Navigating to:', to.name);
        console.log('User Role:', store.getters['auth/userRole']);
        console.log('Has Role:', hasRole);
      
      if (!hasRole) {
        const userRole = store.getters['auth/userRole'];
        const fallbackPath = 
          userRole === 'admin' ? '/app/admin' : 
          userRole === 'sponsor' ? '/app/sponsor/dashboard' : 
          userRole === 'influencer' ? '/app/influencer/dashboard' : 
          '/';
        next(fallbackPath);
        return;
      }
    }
  }
  
  // Handle guest-only routes (prevent logged-in users from accessing)
  if (to.matched.some(record => record.meta.requiresGuest) && isLoggedIn) {
    next({ name: 'Dashboard' });
    return;
  }
  
  next();
});

export default router; 