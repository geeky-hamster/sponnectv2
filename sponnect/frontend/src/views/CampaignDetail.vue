<template>
  <div class="campaign-detail">
    <div class="page-header">
      <router-link 
        :to="userRole === 'sponsor' ? '/sponsor/campaigns' : '/influencer/campaigns'" 
        class="back-link"
      >
        <i class="fas fa-arrow-left"></i> Back to Campaigns
      </router-link>
      <h1 class="page-title">Campaign Details</h1>
    </div>
    
    <div v-if="loading" class="loading-state">
      <p>Loading campaign details...</p>
    </div>
    
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="fetchCampaign" class="retry-button">Retry</button>
      <router-link 
        :to="userRole === 'sponsor' ? '/sponsor/campaigns' : '/influencer/campaigns'" 
        class="back-link"
      >
        Back to Campaigns
      </router-link>
    </div>
    
    <template v-else>
      <div class="campaign-header">
        <div class="campaign-banner" :style="{ backgroundImage: `url(${campaign.bannerImage || '/img/default-banner.jpg'})` }">
          <div class="banner-overlay"></div>
          <div class="campaign-header-content">
            <div class="campaign-title-wrapper">
              <h2 class="campaign-title">{{ campaign.title }}</h2>
              <span :class="['campaign-status', `status-${campaign.status.toLowerCase()}`]">
                {{ campaign.status }}
              </span>
            </div>
            <div class="campaign-meta">
              <div class="sponsor-info">
                <img 
                  :src="campaign.sponsor?.profileImage || '/img/default-company.png'" 
                  :alt="campaign.sponsor?.name"
                  class="sponsor-logo"
                />
                <span class="sponsor-name">{{ campaign.sponsor?.name }}</span>
              </div>
              <div class="campaign-tags">
                <span class="campaign-category">{{ campaign.category }}</span>
                <span class="campaign-platform" v-if="campaign.platform">
                  {{ campaign.platform }}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="campaign-statistics">
          <div class="stat-item">
            <span class="stat-label">Budget</span>
            <span class="stat-value">${{ formatNumber(campaign.budget) }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Duration</span>
            <span class="stat-value">{{ formatDateRange(campaign.startDate, campaign.endDate) }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Applications</span>
            <span class="stat-value">{{ campaign.applicationsCount || 0 }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Required Followers</span>
            <span class="stat-value">{{ campaign.minFollowers ? formatNumber(campaign.minFollowers) : 'Any' }}</span>
          </div>
        </div>
      </div>
      
      <div class="campaign-content">
        <div class="campaign-main">
          <section class="content-section">
            <h3 class="section-title">Description</h3>
            <div class="section-content">
              <p v-if="!campaign.description" class="empty-content">No description provided.</p>
              <div v-else class="campaign-description">
                {{ campaign.description }}
              </div>
            </div>
          </section>
          
          <section class="content-section">
            <h3 class="section-title">Requirements</h3>
            <div class="section-content">
              <p v-if="!campaign.requirements" class="empty-content">No specific requirements provided.</p>
              <div v-else class="campaign-requirements">
                {{ campaign.requirements }}
              </div>
            </div>
          </section>
          
          <section class="content-section">
            <h3 class="section-title">Target Audience</h3>
            <div class="section-content">
              <p v-if="!campaign.targetAudience" class="empty-content">No target audience specified.</p>
              <div v-else class="target-audience">
                {{ campaign.targetAudience }}
              </div>
            </div>
          </section>
          
          <section class="content-section">
            <h3 class="section-title">Additional Media</h3>
            <div class="section-content">
              <p v-if="!campaign.additionalUrls || campaign.additionalUrls.length === 0" class="empty-content">
                No additional media provided.
              </p>
              <div v-else class="media-links">
                <a 
                  v-for="(url, index) in campaign.additionalUrls" 
                  :key="index"
                  :href="url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="media-link"
                >
                  <i class="fas fa-link"></i> Media {{ index + 1 }}
                </a>
              </div>
            </div>
          </section>
        </div>
        
        <div class="campaign-sidebar">
          <!-- Influencer view -->
          <div v-if="userRole === 'influencer'" class="sidebar-card apply-card">
            <h3 class="card-title">Interested in this campaign?</h3>
            <p class="apply-description">
              Apply to this campaign to express your interest and potentially collaborate with the sponsor.
            </p>
            
            <div v-if="hasApplied" class="already-applied">
              <i class="fas fa-check-circle"></i>
              <p>You have already applied to this campaign</p>
              <router-link :to="`/influencer/requests/${applicationId}`" class="view-application-btn">
                View Your Application
              </router-link>
            </div>
            
            <div v-else-if="campaign.status.toLowerCase() !== 'active'" class="unavailable-campaign">
              <i class="fas fa-exclamation-circle"></i>
              <p>This campaign is not currently accepting applications</p>
            </div>
            
            <button 
              v-else
              @click="applyToCampaign"
              class="apply-button"
            >
              Apply Now
            </button>
          </div>
          
          <!-- Sponsor view -->
          <div v-else-if="userRole === 'sponsor'" class="sidebar-card actions-card">
            <h3 class="card-title">Campaign Actions</h3>
            
            <div class="action-buttons">
              <router-link :to="`/sponsor/campaigns/${campaign.id}/edit`" class="edit-button">
                <i class="fas fa-edit"></i> Edit Campaign
              </router-link>
              
              <button 
                v-if="campaign.status.toLowerCase() === 'active'"
                @click="toggleCampaignStatus('paused')"
                class="pause-button"
              >
                <i class="fas fa-pause"></i> Pause Campaign
              </button>
              
              <button 
                v-else-if="campaign.status.toLowerCase() === 'paused'"
                @click="toggleCampaignStatus('active')"
                class="activate-button"
              >
                <i class="fas fa-play"></i> Activate Campaign
              </button>
              
              <button 
                v-if="['active', 'paused'].includes(campaign.status.toLowerCase())"
                @click="confirmDeleteCampaign"
                class="delete-button"
              >
                <i class="fas fa-trash-alt"></i> Delete Campaign
              </button>
            </div>
          </div>
          
          <div class="sidebar-card sponsor-card">
            <h3 class="card-title">About the Sponsor</h3>
            
            <div v-if="!campaign.sponsor" class="loading-sponsor">
              Loading sponsor information...
            </div>
            
            <div v-else class="sponsor-details">
              <div class="sponsor-header">
                <img 
                  :src="campaign.sponsor.profileImage || '/img/default-company.png'" 
                  :alt="campaign.sponsor.name"
                  class="sponsor-profile-image"
                />
                <div class="sponsor-info-detail">
                  <h4 class="sponsor-detail-name">{{ campaign.sponsor.name }}</h4>
                  <p class="sponsor-member-since" v-if="campaign.sponsor.createdAt">
                    Member since {{ formatDate(campaign.sponsor.createdAt) }}
                  </p>
                </div>
              </div>
              
              <p class="sponsor-bio" v-if="campaign.sponsor.bio">
                {{ campaign.sponsor.bio }}
              </p>
              
              <div class="sponsor-stats" v-if="sponsorStats">
                <div class="sponsor-stat">
                  <span class="sponsor-stat-value">{{ sponsorStats.totalCampaigns }}</span>
                  <span class="sponsor-stat-label">Campaigns</span>
                </div>
                <div class="sponsor-stat">
                  <span class="sponsor-stat-value">{{ sponsorStats.successfulCollaborations }}</span>
                  <span class="sponsor-stat-label">Collaborations</span>
                </div>
                <div class="sponsor-stat">
                  <span class="sponsor-stat-value">{{ sponsorStats.averageRating || 'N/A' }}</span>
                  <span class="sponsor-stat-label">Rating</span>
                </div>
              </div>
              
              <a 
                v-if="campaign.sponsor.website" 
                :href="campaign.sponsor.website"
                target="_blank"
                rel="noopener noreferrer"
                class="sponsor-website-link"
              >
                <i class="fas fa-globe"></i> Visit Website
              </a>
            </div>
          </div>
        </div>
      </div>
    </template>
    
    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay">
      <div class="modal-container">
        <div class="modal-header">
          <h2 class="modal-title">Delete Campaign?</h2>
          <button @click="showDeleteModal = false" class="modal-close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to delete this campaign? This action cannot be undone.</p>
          <p class="warning-text">All associated ad requests will also be canceled.</p>
        </div>
        <div class="modal-footer">
          <button @click="showDeleteModal = false" class="cancel-button">
            Cancel
          </button>
          <button @click="deleteCampaign" class="confirm-delete-button">
            <i class="fas fa-trash-alt"></i> Delete Campaign
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRoute, useRouter } from 'vue-router';

export default {
  name: 'CampaignDetail',
  
  setup() {
    const store = useStore();
    const route = useRoute();
    const router = useRouter();
    
    const campaign = ref({});
    const loading = ref(true);
    const error = ref(null);
    const sponsorStats = ref(null);
    const hasApplied = ref(false);
    const applicationId = ref(null);
    const showDeleteModal = ref(false);
    
    const campaignId = route.params.id;
    
    const userRole = computed(() => {
      const user = store.getters['auth/user'];
      return user?.role?.toLowerCase() || 'influencer';
    });
    
    const fetchCampaign = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        // Get campaign details
        const response = await store.dispatch('campaigns/fetchCampaignById', campaignId);
        campaign.value = response;
        
        // Get sponsor stats if available
        if (campaign.value && campaign.value.sponsor && campaign.value.sponsor.id) {
          sponsorStats.value = await store.dispatch('sponsors/fetchSponsorStats', campaign.value.sponsor.id);
        }
        
        // For influencers, check if they've already applied
        if (userRole.value === 'influencer') {
          const requests = await store.dispatch('adRequests/getMyAdRequests');
          const existingApplication = requests.find(req => req.campaignId === campaignId);
          
          if (existingApplication) {
            hasApplied.value = true;
            applicationId.value = existingApplication.id;
          }
        }
      } catch (err) {
        console.error('Error fetching campaign:', err);
        error.value = 'Failed to load campaign details. Please try again.';
      } finally {
        loading.value = false;
      }
    };
    
    const applyToCampaign = () => {
      router.push(`/influencer/campaigns/${campaignId}/apply`);
    };
    
    const toggleCampaignStatus = async (newStatus) => {
      try {
        await store.dispatch('campaigns/updateCampaignStatus', {
          campaignId,
          status: newStatus
        });
        
        // Update local campaign object
        campaign.value.status = newStatus.charAt(0).toUpperCase() + newStatus.slice(1);
        
        // Show success message
        // toast.success(`Campaign ${newStatus === 'active' ? 'activated' : 'paused'} successfully`);
      } catch (err) {
        console.error('Error updating campaign status:', err);
        // toast.error('Failed to update campaign status');
      }
    };
    
    const confirmDeleteCampaign = () => {
      showDeleteModal.value = true;
    };
    
    const deleteCampaign = async () => {
      try {
        await store.dispatch('campaigns/deleteCampaign', campaignId);
        showDeleteModal.value = false;
        
        // Show success message and redirect
        // toast.success('Campaign deleted successfully');
        router.push('/sponsor/campaigns');
      } catch (err) {
        console.error('Error deleting campaign:', err);
        // toast.error('Failed to delete campaign');
      }
    };
    
    const formatNumber = (num) => {
      if (!num && num !== 0) return 'N/A';
      return new Intl.NumberFormat().format(num);
    };
    
    const formatDate = (dateString) => {
      if (!dateString) return 'N/A';
      
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    };
    
    const formatDateRange = (startDate, endDate) => {
      if (!startDate || !endDate) return 'N/A';
      
      const start = new Date(startDate);
      const end = new Date(endDate);
      
      const startStr = start.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric'
      });
      
      const endStr = end.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      });
      
      return `${startStr} - ${endStr}`;
    };
    
    // Initialize data
    onMounted(() => {
      fetchCampaign();
    });
    
    return {
      campaign,
      loading,
      error,
      sponsorStats,
      campaignId,
      userRole,
      hasApplied,
      applicationId,
      showDeleteModal,
      fetchCampaign,
      applyToCampaign,
      toggleCampaignStatus,
      confirmDeleteCampaign,
      deleteCampaign,
      formatNumber,
      formatDate,
      formatDateRange
    };
  }
};
</script>

<style scoped>
.campaign-detail {
  padding: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.back-link {
  color: #4b5563;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.loading-state, .error-state {
  text-align: center;
  padding: 3rem;
  background: #f9fafb;
  border-radius: 0.5rem;
  margin: 2rem 0;
}

.error-state .back-link {
  display: inline-block;
  margin-top: 1rem;
}

.retry-button {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  margin-top: 1rem;
  cursor: pointer;
}

.campaign-header {
  margin-bottom: 2rem;
}

.campaign-banner {
  height: 250px;
  border-radius: 0.5rem;
  background-size: cover;
  background-position: center;
  position: relative;
  overflow: hidden;
  margin-bottom: 1rem;
}

.banner-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.2) 100%);
}

.campaign-header-content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 2rem;
  color: white;
}

.campaign-title-wrapper {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.campaign-title {
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
  margin-right: 1rem;
}

.campaign-status {
  padding: 0.25rem 0.75rem;
  border-radius: 2rem;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.status-active {
  background-color: #10b981;
  color: white;
}

.status-paused {
  background-color: #f59e0b;
  color: white;
}

.status-expired {
  background-color: #6b7280;
  color: white;
}

.status-draft {
  background-color: #6b7280;
  color: white;
}

.campaign-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sponsor-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sponsor-logo {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  object-fit: cover;
  background-color: white;
}

.campaign-tags {
  display: flex;
  gap: 0.5rem;
}

.campaign-category, .campaign-platform {
  background-color: rgba(255, 255, 255, 0.2);
  padding: 0.25rem 0.75rem;
  border-radius: 2rem;
  font-size: 0.75rem;
}

.campaign-statistics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  padding: 1.5rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

.campaign-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
}

.content-section {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-top: 0;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.empty-content {
  color: #6b7280;
  font-style: italic;
}

.campaign-description, .campaign-requirements, .target-audience {
  line-height: 1.6;
  color: #4b5563;
}

.media-links {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.media-link {
  display: inline-block;
  padding: 0.5rem 1rem;
  background-color: #f3f4f6;
  color: #4b5563;
  text-decoration: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.media-link:hover {
  background-color: #e5e7eb;
}

.sidebar-card {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin-top: 0;
  margin-bottom: 1rem;
}

.apply-description {
  color: #4b5563;
  margin-bottom: 1.5rem;
}

.already-applied, .unavailable-campaign {
  text-align: center;
  padding: 1.5rem;
  background-color: #f3f4f6;
  border-radius: 0.375rem;
  margin-bottom: 1rem;
}

.already-applied i, .unavailable-campaign i {
  font-size: 2rem;
  margin-bottom: 0.75rem;
}

.already-applied i {
  color: #10b981;
}

.unavailable-campaign i {
  color: #f59e0b;
}

.already-applied p, .unavailable-campaign p {
  margin-bottom: 1rem;
  color: #4b5563;
}

.view-application-btn {
  display: inline-block;
  padding: 0.5rem 1rem;
  background-color: #3b82f6;
  color: white;
  text-decoration: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.apply-button {
  width: 100%;
  padding: 0.75rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  font-size: 1rem;
  cursor: pointer;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.edit-button, .pause-button, .activate-button, .delete-button {
  padding: 0.75rem;
  border-radius: 0.375rem;
  font-weight: 500;
  text-align: center;
  cursor: pointer;
  text-decoration: none;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.edit-button {
  background-color: #3b82f6;
  color: white;
  border: none;
}

.pause-button {
  background-color: #f59e0b;
  color: white;
  border: none;
}

.activate-button {
  background-color: #10b981;
  color: white;
  border: none;
}

.delete-button {
  background-color: white;
  color: #ef4444;
  border: 1px solid #ef4444;
}

.sponsor-details {
  display: flex;
  flex-direction: column;
}

.sponsor-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.sponsor-profile-image {
  width: 4rem;
  height: 4rem;
  border-radius: 50%;
  object-fit: cover;
}

.sponsor-detail-name {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 0.25rem 0;
}

.sponsor-member-since {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0;
}

.sponsor-bio {
  margin-bottom: 1.5rem;
  color: #4b5563;
  line-height: 1.6;
}

.sponsor-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  text-align: center;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: #f9fafb;
  border-radius: 0.375rem;
}

.sponsor-stat {
  display: flex;
  flex-direction: column;
}

.sponsor-stat-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

.sponsor-stat-label {
  font-size: 0.75rem;
  color: #6b7280;
}

.sponsor-website-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background-color: #f3f4f6;
  color: #4b5563;
  text-decoration: none;
  border-radius: 0.375rem;
  font-weight: 500;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

.modal-container {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  padding: 1.5rem;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
}

.modal-close-btn {
  background: none;
  border: none;
  font-size: 1.25rem;
  color: #6b7280;
  cursor: pointer;
}

.modal-body {
  margin-bottom: 1.5rem;
}

.warning-text {
  color: #ef4444;
  font-weight: 500;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.cancel-button, .confirm-delete-button {
  padding: 0.75rem 1rem;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
}

.cancel-button {
  background-color: white;
  color: #6b7280;
  border: 1px solid #d1d5db;
}

.confirm-delete-button {
  background-color: #ef4444;
  color: white;
  border: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

@media (max-width: 768px) {
  .campaign-content {
    grid-template-columns: 1fr;
  }
  
  .campaign-title {
    font-size: 1.5rem;
  }
  
  .campaign-banner {
    height: 200px;
  }
}
</style> 