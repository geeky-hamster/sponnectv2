<template>
  <div class="dashboard-container">
    <h1 class="page-title">Dashboard</h1>
    
    <!-- Loading state -->
    <div v-if="loading" class="loading-state">
      <p>Loading dashboard data...</p>
    </div>
    
    <!-- Stats Cards -->
    <div v-else class="stats-grid">
      <div class="stats-card" v-for="(stat, index) in stats" :key="index">
        <div class="stats-icon" :class="stat.color">
          <i :class="stat.icon"></i>
        </div>
        <div class="stats-content">
          <h3 class="stats-value">{{ stat.value }}</h3>
          <p class="stats-label">{{ stat.label }}</p>
        </div>
      </div>
    </div>
    
    <!-- Role-specific content for influencer/sponsor -->
    <div v-if="userRole === 'influencer'" class="role-specific-content">
      <section class="dashboard-section">
        <h2 class="section-title">Active Campaigns for You</h2>
        <p v-if="recommendedCampaigns.length === 0" class="empty-message">
          No active campaigns match your profile yet. Check back soon or explore all available campaigns!
        </p>
        <div v-else class="campaigns-grid">
          <div v-for="campaign in recommendedCampaigns" :key="campaign.id" class="campaign-card">
            <div class="campaign-header">
              <img :src="campaign.sponsorLogo" :alt="campaign.sponsorName" class="sponsor-logo">
              <h3 class="campaign-title">{{ campaign.title }}</h3>
            </div>
            <p class="campaign-description">{{ truncateText(campaign.description, 100) }}</p>
            <div class="campaign-meta">
              <span class="campaign-budget">${{ campaign.budget }}</span>
              <span class="campaign-category">{{ campaign.category }}</span>
            </div>
            <button @click="viewCampaign(campaign.id)" class="view-button">View Campaign</button>
          </div>
        </div>
        <div class="section-footer">
          <router-link to="/influencer/campaigns" class="view-all-link">View All Campaigns</router-link>
        </div>
      </section>
      
      <section class="dashboard-section">
        <h2 class="section-title">Your Recent Ad Requests</h2>
        <p v-if="recentRequests.length === 0" class="empty-message">
          You haven't submitted any ad requests yet. Start applying to campaigns!
        </p>
        <div v-else class="requests-list">
          <div v-for="request in recentRequests" :key="request.id" class="request-item">
            <div class="request-info">
              <h3 class="request-campaign">{{ request.campaignTitle }}</h3>
              <p class="request-sponsor">{{ request.sponsorName }}</p>
            </div>
            <div class="request-meta">
              <span :class="['request-status', getStatusClass(request.status)]">{{ request.status }}</span>
              <span class="request-date">{{ formatDate(request.date) }}</span>
            </div>
            <router-link :to="`/influencer/requests/${request.id}`" class="details-link">View Details</router-link>
          </div>
        </div>
        <div class="section-footer">
          <router-link to="/influencer/requests" class="view-all-link">View All Ad Requests</router-link>
        </div>
      </section>
    </div>
    
    <div v-else-if="userRole === 'sponsor'" class="role-specific-content">
      <section class="dashboard-section">
        <h2 class="section-title">Your Current Campaigns</h2>
        <p v-if="sponsorCampaigns.length === 0" class="empty-message">
          You haven't created any campaigns yet. Start reaching influencers by creating a campaign!
        </p>
        <div v-else class="campaigns-grid">
          <div v-for="campaign in sponsorCampaigns" :key="campaign.id" class="campaign-card">
            <div class="campaign-header">
              <span :class="['campaign-status', getStatusClass(campaign.status)]">{{ campaign.status }}</span>
              <h3 class="campaign-title">{{ campaign.title }}</h3>
            </div>
            <div class="campaign-stats">
              <div class="stat-item">
                <span class="stat-label">Budget</span>
                <span class="stat-value">${{ campaign.budget }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Applications</span>
                <span class="stat-value">{{ campaign.applicationsCount }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Days Left</span>
                <span class="stat-value">{{ campaign.daysLeft }}</span>
              </div>
            </div>
            <div class="campaign-actions">
              <router-link :to="`/sponsor/campaigns/${campaign.id}`" class="view-button">View</router-link>
              <router-link :to="`/sponsor/campaigns/${campaign.id}/edit`" class="edit-button">Edit</router-link>
            </div>
          </div>
        </div>
        <div class="section-footer">
          <router-link to="/sponsor/campaigns/create" class="create-campaign-btn">Create New Campaign</router-link>
        </div>
      </section>
      
      <section class="dashboard-section">
        <h2 class="section-title">Recent Ad Requests</h2>
        <p v-if="recentRequests.length === 0" class="empty-message">
          No new ad requests yet. Create more campaigns to attract influencers!
        </p>
        <div v-else class="requests-list">
          <div v-for="request in recentRequests" :key="request.id" class="request-item">
            <div class="request-info">
              <h3 class="request-campaign">{{ request.campaignTitle }}</h3>
              <p class="request-influencer">{{ request.influencerName }}</p>
            </div>
            <div class="request-meta">
              <span :class="['request-status', getStatusClass(request.status)]">{{ request.status }}</span>
              <span class="request-date">{{ formatDate(request.date) }}</span>
            </div>
            <router-link :to="`/sponsor/requests/${request.id}`" class="details-link">View Details</router-link>
          </div>
        </div>
        <div class="section-footer">
          <router-link to="/sponsor/requests" class="view-all-link">View All Ad Requests</router-link>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

export default {
  name: 'Dashboard',
  
  setup() {
    const store = useStore();
    const router = useRouter();
    
    const loading = ref(true);
    const recommendedCampaigns = ref([]);
    const recentRequests = ref([]);
    const sponsorCampaigns = ref([]);
    
    const userRole = computed(() => {
      const user = store.getters['auth/user'];
      return user?.role?.toLowerCase() || 'influencer';
    });
    
    // Placeholder stats - replace with actual data
    const stats = computed(() => {
      if (userRole.value === 'influencer') {
        return [
          { 
            label: 'Active Applications', 
            value: '5', 
            icon: 'fas fa-paper-plane', 
            color: 'blue' 
          },
          { 
            label: 'Approved Requests', 
            value: '3', 
            icon: 'fas fa-check-circle', 
            color: 'green' 
          },
          { 
            label: 'Completed Campaigns', 
            value: '12', 
            icon: 'fas fa-trophy', 
            color: 'gold' 
          },
          { 
            label: 'Total Earnings', 
            value: '$1,250', 
            icon: 'fas fa-dollar-sign', 
            color: 'purple' 
          }
        ];
      } else {
        return [
          { 
            label: 'Active Campaigns', 
            value: '3', 
            icon: 'fas fa-bullhorn', 
            color: 'blue' 
          },
          { 
            label: 'Total Influencers', 
            value: '8', 
            icon: 'fas fa-users', 
            color: 'green' 
          },
          { 
            label: 'Pending Requests', 
            value: '4', 
            icon: 'fas fa-hourglass-half', 
            color: 'orange' 
          },
          { 
            label: 'Total Budget', 
            value: '$5,500', 
            icon: 'fas fa-dollar-sign', 
            color: 'purple' 
          }
        ];
      }
    });
    
    onMounted(async () => {
      try {
        // Fetch dashboard data based on user role
        if (userRole.value === 'influencer') {
          // Fetch recommended campaigns for influencer
          const campaignsResponse = await store.dispatch('campaigns/getRecommendedCampaigns');
          recommendedCampaigns.value = campaignsResponse || [];
          
          // Fetch recent ad requests for influencer
          const requestsResponse = await store.dispatch('adRequests/getRecentRequests');
          recentRequests.value = requestsResponse || [];
        } else if (userRole.value === 'sponsor') {
          // Fetch sponsor's campaigns
          const campaignsResponse = await store.dispatch('campaigns/getSponsorCampaigns');
          sponsorCampaigns.value = campaignsResponse || [];
          
          // Fetch recent ad requests for sponsor
          const requestsResponse = await store.dispatch('adRequests/getRecentSponsorRequests');
          recentRequests.value = requestsResponse || [];
        }
      } catch (error) {
        console.error('Error loading dashboard data:', error);
      } finally {
        loading.value = false;
      }
    });
    
    const viewCampaign = (campaignId) => {
      router.push(`/influencer/campaigns/${campaignId}`);
    };
    
    const formatDate = (dateString) => {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      });
    };
    
    const truncateText = (text, maxLength) => {
      if (!text) return '';
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    };
    
    const getStatusClass = (status) => {
      status = status.toLowerCase();
      if (status === 'active' || status === 'approved') return 'status-success';
      if (status === 'pending') return 'status-pending';
      if (status === 'rejected' || status === 'expired') return 'status-danger';
      return 'status-neutral';
    };
    
    return {
      loading,
      userRole,
      stats,
      recommendedCampaigns,
      recentRequests,
      sponsorCampaigns,
      viewCampaign,
      formatDate,
      truncateText,
      getStatusClass
    };
  }
};
</script>

<style scoped>
.dashboard-container {
  padding: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 2rem;
  color: #1f2937;
}

.loading-state {
  text-align: center;
  padding: 3rem;
  background: #f9fafb;
  border-radius: 0.5rem;
  color: #6b7280;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2.5rem;
}

.stats-card {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stats-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: white;
}

.stats-icon.blue {
  background-color: #3b82f6;
}

.stats-icon.green {
  background-color: #10b981;
}

.stats-icon.orange {
  background-color: #f59e0b;
}

.stats-icon.red {
  background-color: #ef4444;
}

.stats-icon.purple {
  background-color: #8b5cf6;
}

.stats-icon.gold {
  background-color: #f59e0b;
}

.stats-content {
  flex: 1;
}

.stats-value {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  line-height: 1.2;
  color: #1f2937;
}

.stats-label {
  color: #6b7280;
  margin: 0;
  font-size: 0.875rem;
}

.role-specific-content {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

.dashboard-section {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #1f2937;
}

.empty-message {
  color: #6b7280;
  text-align: center;
  padding: 2rem 0;
}

.campaigns-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.campaign-card {
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.campaign-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.sponsor-logo {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  object-fit: cover;
}

.campaign-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
  color: #1f2937;
}

.campaign-description {
  color: #4b5563;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.campaign-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.campaign-budget {
  font-weight: 600;
  color: #059669;
}

.campaign-category {
  color: #6b7280;
  background: #f3f4f6;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
}

.campaign-status {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.campaign-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 0.25rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.stat-label {
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.stat-value {
  font-weight: 600;
  color: #1f2937;
}

.campaign-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}

.view-button, .edit-button, .details-link {
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  text-align: center;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
}

.view-button {
  background: #3b82f6;
  color: white;
  border: none;
}

.edit-button {
  background: white;
  color: #3b82f6;
  border: 1px solid #3b82f6;
}

.requests-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.request-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
}

.request-info {
  flex: 1;
}

.request-campaign {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.25rem 0;
  color: #1f2937;
}

.request-sponsor, .request-influencer {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

.request-meta {
  margin-right: 1rem;
  text-align: right;
}

.request-status {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 500;
  font-size: 0.875rem;
}

.request-date {
  font-size: 0.75rem;
  color: #6b7280;
}

.status-success {
  color: #059669;
}

.status-pending {
  color: #d97706;
}

.status-danger {
  color: #dc2626;
}

.status-neutral {
  color: #6b7280;
}

.details-link {
  background: #f3f4f6;
  color: #4b5563;
  padding: 0.5rem 1rem;
  text-decoration: none;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.details-link:hover, .view-button:hover, .edit-button:hover {
  opacity: 0.9;
}

.section-footer {
  text-align: center;
  padding-top: 1rem;
}

.view-all-link, .create-campaign-btn {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  background-color: #3b82f6;
  color: white;
  text-decoration: none;
  border-radius: 0.25rem;
  font-weight: 500;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .campaigns-grid {
    grid-template-columns: 1fr;
  }
  
  .request-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
  
  .request-meta {
    display: flex;
    width: 100%;
    justify-content: space-between;
    margin-right: 0;
    text-align: left;
  }
  
  .details-link {
    width: 100%;
    text-align: center;
  }
}
</style> 