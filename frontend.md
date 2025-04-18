# AI Agent Task: Generate Sponnect Vue.js Frontend (Layout, Modals, Toasts)

## Objective

Update the `sponnect` Vue.js frontend plan (in `sponnect/frontend`) to include a unified layout structure with a persistent Navbar, a distinct landing page, Bootstrap 5 modals, and `vue-toastification` notifications. Continue using Vue 3, Vuex, Vue Router, and rely solely on Bootstrap 5 for styling.

---

## Step 1: Project Setup & Dependencies (Update)

1.  **Navigate & Scaffold (if not done already):**
    ```
    # cd ../frontend # If in sponnect/backend
    # npm create vite@latest . --template vue # If starting fresh
    ```

2.  **Install/Update Dependencies:**
    ```
    npm install
    npm install vue-router@4 vuex@4 axios bootstrap@5
    npm install vue-toastification@next # Install toastification for Vue 3
    ```

3.  **Configure `main.js` (Update):**
    ```
    // src/main.js
    import { createApp } from 'vue';
    import App from './App.vue';
    import router from './router';
    import store from './store';
    import axios from 'axios';

    // Import Bootstrap CSS & JS
    import 'bootstrap/dist/css/bootstrap.min.css';
    import 'bootstrap/dist/js/bootstrap.bundle.min.js';

    // Import Vue Toastification CSS & Plugin
    import Toast, { POSITION } from 'vue-toastification';
    import "vue-toastification/dist/index.css"; // Default CSS

    // Configure Axios (baseURL, interceptors as before)
    axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'; // Use env variable

    axios.interceptors.request.use(config => {
      const token = store.state.auth.token;
      if (token) config.headers.Authorization = `Bearer ${token}`;
      return config;
    });

    axios.interceptors.response.use(response => response, error => {
      if (error.response && error.response.status === 401) {
        store.dispatch('auth/logoutAndRedirect'); // Updated action name
      }
      // Do not automatically show generic toast here, let actions handle it
      return Promise.reject(error);
    });

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
    };

    const app = createApp(App);
    app.use(router);
    app.use(store);
    app.use(Toast, toastOptions); // Use Toast plugin with options
    app.mount('#app');
    ```
    *Note: Set `VITE_API_BASE_URL` in a `.env` file in the `sponnect/frontend` directory.*

---

## Step 2: Vuex Store Setup (Update)

1.  **Module Structure:** Keep modules: `auth.js`, `campaigns.js`, `adRequests.js`, `admin.js`, `ui.js`.

2.  **Update Actions to Use Toastification:**
    *   Modify **all actions** that perform API calls (in `auth`, `campaigns`, `adRequests`, `admin` modules).
    *   Import `useToast` from `vue-toastification` at the top of each module file where needed.
    *   Instantiate the toast: `const toast = useToast();` (call this inside the action function scope).
    *   On successful API calls (within `.then()` or after `await`): Call `toast.success("Operation successful!")`.
    *   On failed API calls (within `.catch()`): Call `toast.error(error.response?.data?.message || "An error occurred.")`.
    *   **Example (auth.js login action):**
        ```
        // src/store/modules/auth.js
        import axios from 'axios';
        import { useToast } from 'vue-toastification'; // Import useToast

        // ... other imports, state, mutations, getters ...

        const actions = {
          async login({ commit, dispatch }, credentials) {
            const toast = useToast(); // Instantiate toast inside action
            commit('AUTH_REQUEST');
            dispatch('ui/setLoading', true, { root: true }); // Use ui module for loading
            try {
              const response = await axios.post('/login', credentials);
              const token = response.data.access_token;
              localStorage.setItem('token', token);
              axios.defaults.headers.common['Authorization'] = `Bearer ${token}`; // Update axios header immediately
              commit('AUTH_SUCCESS', token);
              await dispatch('fetchProfile'); // Fetch profile after successful login
              toast.success('Login successful!'); // Success toast
              dispatch('ui/setLoading', false, { root: true });
              return true; // Indicate success
            } catch (error) {
              commit('AUTH_ERROR');
              localStorage.removeItem('token');
              delete axios.defaults.headers.common['Authorization'];
              toast.error(error.response?.data?.message || 'Login failed.'); // Error toast
              dispatch('ui/setLoading', false, { root: true });
              return false; // Indicate failure
            }
          },
          // Add new action for handling logout + redirect
          logoutAndRedirect({ commit }) {
            commit('LOGOUT');
            localStorage.removeItem('token');
            delete axios.defaults.headers.common['Authorization'];
            // No need for toast on auto-logout due to 401
            // Redirect handled by router or component
          },
          // ... other actions (register, fetchProfile, logout) updated similarly with useToast ...
        };
        // ... export ...
        ```

3.  **UI Module (`src/store/modules/ui.js`) - Simplify:**
    *   **State:** `loading: false`. (Remove `error` and `successMessage`).
    *   **Mutations:** `SET_LOADING`. (Remove error/success mutations).
    *   **Actions:** `setLoading(context, isLoading)`. (Remove error/success actions).
    *   **Getters:** `isLoading: state => state.loading`.

---

## Step 3: Routing Setup (Update for Layouts)

1.  **Update `src/router/index.js`:** Implement nested routing for layouts.
    ```
    // src/router/index.js
    import { createRouter, createWebHistory } from 'vue-router';
    import store from '../store';

    // Layouts
    const MainLayout = () => import('../layouts/MainLayout.vue');
    const AuthLayout = () => import('../layouts/AuthLayout.vue'); // Simple centered layout for auth pages

    // Views (Lazy load)
    const LandingPage = () => import('../views/LandingPage.vue');
    const HomeRedirect = () => import('../views/HomeRedirect.vue'); // Component to redirect based on role
    const Login = () => import('../views/Login.vue');
    const Register = () => import('../views/Register.vue');
    // ... import other views (AdminDashboard, CampaignList, ProfileSettings etc.) ...
    const NotFound = () => import('../views/NotFound.vue');
    const Unauthorized = () => import('../views/Unauthorized.vue');

    const routes = [
      // Public Landing Page
      { path: '/', name: 'LandingPage', component: LandingPage, meta: { guestOnly: true } }, // Separate layout/view

      // Auth Layout Routes
      {
        path: '/auth',
        component: AuthLayout, // Use the AuthLayout component
        children: [
          { path: 'login', name: 'Login', component: Login, meta: { guestOnly: true } },
          { path: 'register', name: 'Register', component: Register, meta: { guestOnly: true } },
        ]
      },

      // Main Application Layout Routes
      {
        path: '/app', // Base path for authenticated users
        component: MainLayout, // Use the MainLayout component (with Navbar)
        meta: { requiresAuth: true }, // All children require auth
        children: [
          { path: '', name: 'HomeRedirect', component: HomeRedirect }, // Redirects to specific dashboard

          // Admin Routes
          { path: 'admin/dashboard', name: 'AdminDashboard', component: () => import('../views/admin/AdminDashboard.vue'), meta: { roles: ['admin'] } },

          // Sponsor Routes (adjust paths to be relative to /app)
          { path: 'sponsor/dashboard', name: 'SponsorDashboard', component: () => import('../views/sponsor/SponsorDashboard.vue'), meta: { roles: ['sponsor', 'admin'] } },
          { path: 'sponsor/campaigns', name: 'CampaignList', component: () => import('../views/sponsor/CampaignList.vue'), meta: { roles: ['sponsor', 'admin'] } },
          { path: 'sponsor/campaigns/new', name: 'CampaignCreate', component: () => import('../views/sponsor/CampaignCreate.vue'), meta: { roles: ['sponsor', 'admin'] } },
          { path: 'sponsor/campaigns/:id', name: 'CampaignDetails', component: () => import('../views/sponsor/CampaignDetails.vue'), props: true, meta: { roles: ['sponsor', 'admin'] } },
          { path: 'sponsor/campaigns/:id/edit', name: 'CampaignEdit', component: () => import('../views/sponsor/CampaignEdit.vue'), props: true, meta: { roles: ['sponsor', 'admin'] } },
          { path: 'sponsor/search/influencers', name: 'SearchInfluencers', component: () => import('../views/sponsor/SearchInfluencers.vue'), meta: { roles: ['sponsor', 'admin'] } },

          // Influencer Routes (adjust paths relative to /app)
          { path: 'influencer/dashboard', name: 'InfluencerDashboard', component: () => import('../views/influencer/InfluencerDashboard.vue'), meta: { roles: ['influencer', 'admin'] } },
          { path: 'influencer/profile', name: 'ProfileSettings', component: () => import('../views/influencer/ProfileSettings.vue'), meta: { roles: ['influencer', 'admin'] } },
          { path: 'influencer/ad-requests', name: 'AdRequestList', component: () => import('../views/influencer/AdRequestList.vue'), meta: { roles: ['influencer', 'admin'] } },
          { path: 'influencer/search/campaigns', name: 'SearchCampaigns', component: () => import('../views/influencer/SearchCampaigns.vue'), meta: { roles: ['influencer', 'admin'] } },

          // Common authenticated routes can go here if needed
        ]
      },

      // Utility Routes
      { path: '/unauthorized', name: 'Unauthorized', component: Unauthorized },
      { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound },
    ];

    const router = createRouter({ history: createWebHistory(), routes });

    // Navigation Guard (Update redirect paths and guestOnly logic)
    router.beforeEach(async (to, from, next) => {
      const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
      const guestOnly = to.matched.some(record => record.meta.guestOnly);
      const allowedRoles = to.meta.roles;

      const isAuthenticated = store.getters['auth/isAuthenticated'];
      let currentUser = store.getters['auth/currentUser'];

      if (isAuthenticated && !currentUser && to.name !== 'Login') { // Prevent infinite loop on login fail
          try {
              await store.dispatch('auth/fetchProfile');
              currentUser = store.getters['auth/currentUser'];
          } catch (error) {
              await store.dispatch('auth/logoutAndRedirect'); // Use updated action
              // Redirect to login only if the target route requires auth
              return requiresAuth ? next({ name: 'Login', query: { redirect: to.fullPath } }) : next();
          }
      }

      const userRole = currentUser?.role;

      if (requiresAuth) {
          if (!isAuthenticated) {
              return next({ name: 'Login', query: { redirect: to.fullPath } }); // Redirect to login under /auth
          }
          if (allowedRoles && !allowedRoles.includes(userRole) && userRole !== 'admin') { // Admin bypasses specific role check
              return next('/unauthorized');
          }
          return next(); // Authenticated and authorized
      } else if (guestOnly && isAuthenticated) {
          // Already logged in, redirect from Landing/Login/Register to main app home
          return next('/app'); // Redirect to the base authenticated route
      } else {
          return next(); // Public route or guest accessing guestOnly route
      }
    });

    export default router;
    ```

---

## Step 4: Layout Components (`src/layouts`)

1.  **`MainLayout.vue`:**
    *   Include `Navbar.vue`.
    *   Main content area using `<div class="container-fluid py-3">` or similar Bootstrap container.
    *   Place `<router-view />` inside the main content area to render nested child routes.
    *   Possibly include a footer if desired (using Bootstrap footer classes).
    *   Include `LoadingSpinner.vue` conditionally based on `ui/isLoading`.
    ```
    <template>
      <div>
        <Navbar />
        <main role="main" class="container-fluid py-4">
          <LoadingSpinner v-if="isLoading" />
          <router-view v-else />
        </main>
        <!-- Optional Footer -->
        <footer class="footer mt-auto py-3 bg-light">
          <div class="container text-center">
            <span class="text-muted">Sponnect &copy; {{ new Date().getFullYear() }}</span>
          </div>
        </footer>
      </div>
    </template>

    <script setup>
    import Navbar from '../components/layout/Navbar.vue';
    import LoadingSpinner from '../components/shared/LoadingSpinner.vue';
    import { computed } from 'vue';
    import { useStore } from 'vuex';

    const store = useStore();
    const isLoading = computed(() => store.getters['ui/isLoading']);
    </script>

    <style scoped>
    /* Minimal styles if needed, rely on Bootstrap */
    main { min-height: calc(100vh - 120px); /* Adjust based on navbar/footer height */ }
    </style>
    ```

2.  **`AuthLayout.vue`:**
    *   Simple centered layout for login/register forms.
    *   Use Bootstrap grid (`container`, `row`, `col-md-6`, `offset-md-3`, etc.) to center content.
    *   Place `<router-view />` inside the centered column.
    ```
    <template>
      <div class="container vh-100 d-flex justify-content-center align-items-center">
        <div class="row w-100">
          <div class="col-md-6 col-lg-4 mx-auto">
             <h2 class="text-center mb-4">Sponnect</h2>
             <router-view />
          </div>
        </div>
      </div>
    </template>

    <script setup>
    // No specific script needed for basic layout
    </script>
    ```

3.  **`Navbar.vue` (`src/components/layout/Navbar.vue`):**
    *   Use Bootstrap `navbar` classes (`navbar`, `navbar-expand-lg`, `navbar-dark`, `bg-dark`).
    *   Brand link (`navbar-brand`).
    *   Toggler button for mobile (`navbar-toggler`).
    *   Collapsible content (`collapse`, `navbar-collapse`).
    *   Nav items (`navbar-nav`, `nav-item`, `nav-link`).
    *   Conditionally show links based on Vuex getters `isAuthenticated`, `isAdmin`, `isSponsor`, `isInfluencer`.
    *   If authenticated, show user dropdown (`nav-item dropdown`) with links to Profile/Settings and a Logout button that dispatches `auth/logoutAndRedirect`.
    *   If not authenticated, show Login and Register links (`/auth/login`, `/auth/register`).

---

## Step 5: Core Components & Views (Updates & Additions)

1.  **`LandingPage.vue` (`src/views/LandingPage.vue`):**
    *   A visually appealing public page.
    *   Use Bootstrap grid, jumbotron/hero section (`container`, `py-5`, `text-center`), cards, buttons.
    *   Explain the platform's purpose.
    *   Include clear "Login" and "Register" buttons linking to `/auth/login` and `/auth/register`.

2.  **`HomeRedirect.vue` (`src/views/HomeRedirect.vue`):**
    *   A simple component that checks the user's role from Vuex store (`auth/currentUser`) and programmatically redirects using `router.push` or `router.replace` to the appropriate dashboard (`/app/admin/dashboard`, `/app/sponsor/dashboard`, `/app/influencer/dashboard`). Use `onMounted` or `beforeMount` hook.

3.  **Shared Components (`src/components/shared`):**
    *   `LoadingSpinner.vue`: (As before) Display conditionally.
    *   `ConfirmModal.vue`: (New/Refined)
        *   Props: `id` (for modal targeting), `title`, `message`.
        *   Emit: `@confirm`.
        *   Structure using Bootstrap modal HTML (`modal`, `modal-dialog`, `modal-content`, `modal-header`, `modal-body`, `modal-footer`). Use `ref` to get modal instance and control programmatically via `bootstrap.Modal`.
    *   `BaseModal.vue`: (Optional) A more generic modal wrapper component.

4.  **Modals Integration:**
    *   **Negotiation:** In `AdRequestDetails.vue` (Influencer) and `SponsorAdRequestDetail.vue` (Sponsor - *this view might be needed*), add a button to trigger `NegotiationModal.vue`.
    *   **Application:** In `SearchCampaigns.vue`, the 'Apply' button triggers `ApplyModal.vue`.
    *   **Confirmation:** In `CampaignList.vue`, the 'Delete' button triggers `ConfirmModal.vue`.

5.  **Component Updates:**
    *   Remove direct error/success message display logic from components; rely on `vue-toastification`.
    *   Ensure forms use Bootstrap classes correctly for a modern look.
    *   Buttons should use appropriate Bootstrap classes (`btn`, `btn-primary`, `btn-danger`, `btn-sm`, etc.).
    *   Tables should use `table`, `table-striped`, `table-hover`, etc.

---

## Step 6: Notifications (Vue Toastification Usage)

*   As outlined in Step 2, import `useToast` and call `toast.success()` / `toast.error()` within the `.then()` / `.catch()` blocks of API calls inside Vuex actions. This provides immediate feedback to the user for operations.

---

## Final Notes for AI Agent

*   Implement the nested routing structure with `MainLayout.vue` and `AuthLayout.vue`.
*   Ensure `Navbar.vue` is correctly placed and displays links/actions based on authentication state and user role.
*   Create the `LandingPage.vue` as the public entry point.
*   Integrate `vue-toastification` setup in `main.js` and usage within Vuex actions for feedback. Simplify the `ui` Vuex module.
*   Implement reusable modal components (`ConfirmModal.vue`) and specific modals (`NegotiationModal.vue`, `ApplyModal.vue`) using Bootstrap 5 modal structure and JavaScript API if needed.
*   Strictly adhere to using Bootstrap 5 classes for all styling; avoid custom CSS.
*   Connect all user interactions (button clicks, form submissions) to the appropriate Vuex actions.

---
