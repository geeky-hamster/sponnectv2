<template>
  <div class="home-container">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <h1 class="hero-title">Connect Brands with Authentic Influencers</h1>
        <p class="hero-subtitle">
          Sponnect is the premier platform for influencers and brands to collaborate on impactful marketing campaigns
        </p>
        <div class="hero-buttons">
          <router-link to="/auth/register" class="btn-primary">Get Started</router-link>
          <a href="#how-it-works" class="btn-secondary">How it Works</a>
        </div>
      </div>
      <div class="hero-image">
        <img src="/img/hero-image.webp" alt="Sponnect Platform" />
      </div>
    </section>

    <!-- Features Section -->
    <section class="features" id="how-it-works">
      <div class="section-header">
        <h2>How Sponnect Works</h2>
        <p>A streamlined process for successful brand-influencer partnerships</p>
      </div>
      
      <div class="feature-cards">
        <div class="feature-card">
          <div class="feature-icon">
            <i class="fas fa-user-plus"></i>
          </div>
          <h3>Create Your Profile</h3>
          <p>Sign up as a brand or influencer and build your professional profile</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">
            <i class="fas fa-search"></i>
          </div>
          <h3>Find the Perfect Match</h3>
          <p>Brands post campaigns, influencers discover opportunities that align with their audience</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">
            <i class="fas fa-handshake"></i>
          </div>
          <h3>Collaborate Seamlessly</h3>
          <p>Negotiate terms, manage deliverables, and track campaign progress in one place</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">
            <i class="fas fa-chart-line"></i>
          </div>
          <h3>Measure Results</h3>
          <p>Get detailed analytics and insights to evaluate campaign performance</p>
        </div>
      </div>
    </section>

    <!-- Testimonials -->
    <section class="testimonials">
      <div class="section-header">
        <h2>Success Stories</h2>
        <p>Hear from brands and influencers who've achieved results with Sponnect</p>
      </div>
      
      <div class="testimonial-slider">
        <div class="testimonial-card">
          <div class="testimonial-content">
            <p>"Sponnect has completely transformed how we approach influencer marketing. We've been able to find authentic voices that truly resonate with our brand values."</p>
          </div>
          <div class="testimonial-author">
            <img src="/img/testimonial-1.webp" alt="Sarah Johnson" />
            <div>
              <h4>Sarah Johnson</h4>
              <p>Marketing Director, EcoStyle</p>
            </div>
          </div>
        </div>
        
        <div class="testimonial-card">
          <div class="testimonial-content">
            <p>"As an influencer, Sponnect has opened doors to amazing brand partnerships that align perfectly with my content and values. The platform is intuitive and makes collaboration a breeze."</p>
          </div>
          <div class="testimonial-author">
            <img src="/img/testimonial-2.webp" alt="Marcus Chen" />
            <div>
              <h4>Marcus Chen</h4>
              <p>Lifestyle Influencer, 450K Followers</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta">
      <div class="cta-content">
        <h2>Ready to Transform Your Marketing Strategy?</h2>
        <p>Join thousands of brands and influencers already collaborating on Sponnect</p>
        <router-link to="/auth/register" class="btn-primary">Create Your Account</router-link>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'HomeView'
}
</script>

<style scoped>
.home-container {
  width: 100%;
  max-width: 100%;
  overflow-x: hidden;
}

/* Hero Section */
.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4rem 5% 2rem;
  background: linear-gradient(to right, #ffffff, #f0f9ff);
  min-height: 80vh;
}

.hero-content {
  flex: 1;
  max-width: 600px;
  padding-right: 2rem;
}

.hero-title {
  font-size: 3rem;
  font-weight: 800;
  line-height: 1.2;
  color: #1e293b;
  margin-bottom: 1.5rem;
  background: linear-gradient(90deg, #3b82f6, #2563eb);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  font-size: 1.25rem;
  line-height: 1.6;
  color: #64748b;
  margin-bottom: 2rem;
}

.hero-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn-primary {
  display: inline-block;
  padding: 0.875rem 1.5rem;
  background-color: #3b82f6;
  color: white;
  font-weight: 600;
  border-radius: 0.375rem;
  text-decoration: none;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  background-color: #2563eb;
  transform: translateY(-2px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.btn-secondary {
  display: inline-block;
  padding: 0.875rem 1.5rem;
  background-color: transparent;
  color: #3b82f6;
  font-weight: 600;
  border: 1px solid #3b82f6;
  border-radius: 0.375rem;
  text-decoration: none;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background-color: rgba(59, 130, 246, 0.1);
  transform: translateY(-2px);
}

.hero-image {
  flex: 1;
  max-width: 550px;
  display: flex;
  justify-content: center;
}

.hero-image img {
  width: 100%;
  height: auto;
  border-radius: 1rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

/* Features Section */
.features {
  padding: 5rem 5%;
  background-color: #ffffff;
}

.section-header {
  text-align: center;
  max-width: 700px;
  margin: 0 auto 3rem;
}

.section-header h2 {
  font-size: 2.25rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 1rem;
}

.section-header p {
  font-size: 1.125rem;
  color: #64748b;
}

.feature-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-top: 3rem;
}

.feature-card {
  background-color: white;
  padding: 2rem;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  text-align: center;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.feature-icon {
  width: 3.5rem;
  height: 3.5rem;
  background-color: #ebf5ff;
  color: #3b82f6;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  margin: 0 auto 1.5rem;
}

.feature-icon i {
  font-size: 1.5rem;
}

.feature-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 1rem;
}

.feature-card p {
  color: #64748b;
  line-height: 1.5;
}

/* Testimonials */
.testimonials {
  padding: 5rem 5%;
  background-color: #f8fafc;
}

.testimonial-slider {
  display: flex;
  gap: 2rem;
  overflow-x: auto;
  padding: 1rem 0 2rem;
  scroll-snap-type: x mandatory;
  scroll-behavior: smooth;
}

.testimonial-slider::-webkit-scrollbar {
  height: 8px;
}

.testimonial-slider::-webkit-scrollbar-track {
  background: #e2e8f0;
  border-radius: 4px;
}

.testimonial-slider::-webkit-scrollbar-thumb {
  background: #94a3b8;
  border-radius: 4px;
}

.testimonial-card {
  min-width: 380px;
  flex: 0 0 calc(50% - 1rem);
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  padding: 2rem;
  scroll-snap-align: start;
}

.testimonial-content {
  margin-bottom: 1.5rem;
}

.testimonial-content p {
  font-size: 1.125rem;
  color: #334155;
  line-height: 1.6;
  font-style: italic;
}

.testimonial-author {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.testimonial-author img {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  object-fit: cover;
}

.testimonial-author h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.testimonial-author p {
  font-size: 0.875rem;
  color: #64748b;
}

/* CTA Section */
.cta {
  padding: 5rem 5%;
  background: linear-gradient(to right, #3b82f6, #2563eb);
  color: white;
  text-align: center;
}

.cta-content {
  max-width: 700px;
  margin: 0 auto;
}

.cta h2 {
  font-size: 2.25rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.cta p {
  font-size: 1.125rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.cta .btn-primary {
  background-color: white;
  color: #2563eb;
  padding: 1rem 2rem;
  font-size: 1.125rem;
}

.cta .btn-primary:hover {
  background-color: #f8fafc;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2), 0 4px 6px -2px rgba(0, 0, 0, 0.1);
}

/* Responsive Styles */
@media (max-width: 1024px) {
  .hero {
    flex-direction: column;
    text-align: center;
    padding: 3rem 5%;
  }
  
  .hero-content {
    max-width: 100%;
    padding-right: 0;
    margin-bottom: 3rem;
  }
  
  .hero-buttons {
    justify-content: center;
  }
  
  .hero-image {
    max-width: 80%;
  }
  
  .testimonial-card {
    min-width: 300px;
    flex: 0 0 calc(100% - 2rem);
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }
  
  .section-header h2 {
    font-size: 2rem;
  }
  
  .cta h2 {
    font-size: 2rem;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-buttons {
    flex-direction: column;
    gap: 1rem;
  }
  
  .btn-primary, .btn-secondary {
    width: 100%;
  }
  
  .feature-cards {
    grid-template-columns: 1fr;
  }
}
</style> 