<template>
    <div class="landing-page">
      <header class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container">
          <a class="navbar-brand" href="#">Sponnect</a>
          <div class="navbar-nav">
            <router-link to="/auth/login" class="nav-link">Login</router-link>
            <router-link to="/auth/register" class="nav-link">Register</router-link>
          </div>
        </div>
      </header>
  
      <main class="container text-center py-5">
        <h1 class="display-4">Welcome to Sponnect</h1>
        <p class="lead">
          Connect brands with authentic influencers for impactful marketing campaigns.
        </p>
        <div class="mt-4">
          <router-link to="/auth/register" class="btn btn-primary btn-lg">Get Started</router-link>
          <router-link to="/auth/login" class="btn btn-outline-secondary btn-lg">Sign In</router-link>
        </div>
      </main>
  
      <section class="features py-5 bg-light">
        <div class="container">
          <div class="row">
            <div class="col-md-4 text-center">
              <i class="fas fa-handshake fa-3x mb-3"></i>
              <h4>Seamless Collaboration</h4>
              <p>From discovery to payment, all in one platform.</p>
            </div>
            <div class="col-md-4 text-center">
              <i class="fas fa-chart-line fa-3x mb-3"></i>
              <h4>Performance Analytics</h4>
              <p>Track campaign metrics and measure ROI in real-time.</p>
            </div>
            <div class="col-md-4 text-center">
              <i class="fas fa-shield-alt fa-3x mb-3"></i>
              <h4>Secure Transactions</h4>
              <p>Protected payments and verified profiles.</p>
            </div>
          </div>
        </div>
      </section>
  
      <footer class="py-4 bg-dark text-white text-center">
        <p>&copy; 2025 Sponnect. All rights reserved.</p>
      </footer>
    </div>
  </template>
  
  <script>
  export default {
    name: "LandingPage",
  };
  </script>
  
  <style scoped>
  .landing-page {
    font-family: Arial, sans-serif;
  }
  
  header {
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .features i {
    color: #3b82f6;
  }
  
  footer {
    font-size: 0.9rem;
  }
  </style>