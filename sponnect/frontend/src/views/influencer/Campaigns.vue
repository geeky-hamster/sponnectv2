<template>
  <div class="campaigns-container">
    <h1 class="page-title">Available Campaigns</h1>
    <p class="page-description">Browse campaigns from sponsors that match your profile and apply to the ones you're interested in.</p>
    
    <div class="filter-container">
      <div class="search-box">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Search campaigns..."
          class="search-input"
        />
      </div>
      
      <div class="filter-group">
        <select v-model="categoryFilter" class="filter-select">
          <option value="">All Categories</option>
          <option v-for="category in categories" :key="category" :value="category">
            {{ category }}
          </option>
        </select>
        
        <select v-model="platformFilter" class="filter-select">
          <option value="">All Platforms</option>
          <option v-for="platform in platforms" :key="platform" :value="platform">
            {{ platform }}
          </option>
        </select>

        <select v-model="budgetFilter" class="filter-select">
          <option value="">All Budgets</option>
          <option value="0-500">$0 - $500</option>
          <option value="500-1000">$500 - $1,000</option>
          <option value="1000-5000">$1,000 - $5,000</option>
          <option value="5000+">$5,000+</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <p>Loading campaigns...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="fetchCampaigns" class="retry-button">Retry</button>
    </div>

    <div v-else-if="paginatedCampaigns.length === 0" class="empty-state">
      <p v-if="filteredCampaigns.length === 0 && (searchQuery || categoryFilter || platformFilter || budgetFilter)">
        No campaigns match your current filters. Try adjusting your search criteria.
      </p>
      <p v-else-if="filteredCampaigns.length === 0">
        No campaigns available at the moment. Check back later!
      </p>
      <p v-else>
        No campaigns on this page. Try navigating to a different page.
      </p>
    </div>

    <div v-else class="campaigns-grid">
      <div 
        v-for="campaign in paginatedCampaigns" 
        :key="campaign.id" 
        class="campaign-card"
        :class="{ 'applied': campaignHasBeenAppliedTo(campaign.id) }"
      >
        <div class="campaign-header">
          <div class="sponsor-info">
            <img 
              :src="campaign.sponsor.profileImage || '/img/default-company.png'" 
              alt="Sponsor Logo" 
              class="sponsor-logo"
            />
            <span class="sponsor-name">{{ campaign.sponsor.name }}</span>
          </div>
          <span class="campaign-category">{{ campaign.category }}</span>
        </div>
        
        <h3 class="campaign-title">{{ campaign.title }}</h3>
        <p class="campaign-description">{{ truncateText(campaign.description, 150) }}</p>
        
        <div class="campaign-details">
          <div class="detail-item">
            <span class="detail-icon"><i class="fas fa-dollar-sign"></i></span>
            <span class="detail-text">Budget: ${{ campaign.budget }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-icon"><i class="fab fa-instagram"></i></span>
            <span class="detail-text">Platform: {{ campaign.platform }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-icon"><i class="fas fa-calendar"></i></span>
            <span class="detail-text">Deadline: {{ formatDate(campaign.endDate) }}</span>
          </div>
        </div>
        
        <div class="campaign-footer">
          <button 
            @click="viewCampaignDetails(campaign.id)" 
            class="details-button"
          >
            View Details
          </button>
          <button 
            v-if="!campaignHasBeenAppliedTo(campaign.id)" 
            @click="applyToCampaign(campaign.id)" 
            class="apply-button"
          >
            Apply Now
          </button>
          <span v-else class="applied-badge">
            Applied
          </span>
        </div>
      </div>
    </div>

    <div v-if="filteredCampaigns.length > 0" class="pagination-controls">
      <button 
        @click="prevPage" 
        :disabled="currentPage === 1" 
        class="pagination-button"
        :class="{ disabled: currentPage === 1 }"
      >
        Previous
      </button>
      <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
      <button 
        @click="nextPage" 
        :disabled="currentPage === totalPages" 
        class="pagination-button"
        :class="{ disabled: currentPage === totalPages }"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

export default {
  name: 'InfluencerCampaigns',
  
  setup() {
    const store = useStore();
    const router = useRouter();
    
    const campaigns = ref([]);
    const userAdRequests = ref([]);
    const loading = ref(true);
    const error = ref(null);
    const searchQuery = ref('');
    const categoryFilter = ref('');
    const platformFilter = ref('');
    const budgetFilter = ref('');
    const currentPage = ref(1);
    const itemsPerPage = 9;
    
    // Sample data for filters
    const categories = ref([
      'Fashion', 'Beauty', 'Tech', 'Gaming', 'Fitness', 
      'Food', 'Travel', 'Lifestyle', 'Education', 'Entertainment'
    ]);
    
    const platforms = ref([
      'Instagram', 'YouTube', 'TikTok', 'Twitter', 'Facebook',
      'Twitch', 'LinkedIn', 'Pinterest', 'Snapchat'
    ]);
    
    const fetchCampaigns = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        // Replace with actual API call when implemented
        const response = await store.dispatch('campaigns/getAvailableCampaigns');
        campaigns.value = response;
        
        // Fetch user's ad requests to check which campaigns they've applied to
        const adRequestsResponse = await store.dispatch('adRequests/getMyAdRequests');
        userAdRequests.value = adRequestsResponse;
      } catch (err) {
        error.value = 'Failed to load campaigns. Please try again.';
        console.error(err);
      } finally {
        loading.value = false;
      }
    };
    
    const filteredCampaigns = computed(() => {
      let result = [...campaigns.value];
      
      // Apply search filter
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        result = result.filter(campaign => 
          campaign.title.toLowerCase().includes(query) || 
          campaign.description.toLowerCase().includes(query) ||
          campaign.sponsor.name.toLowerCase().includes(query)
        );
      }
      
      // Apply category filter
      if (categoryFilter.value) {
        result = result.filter(campaign => campaign.category === categoryFilter.value);
      }
      
      // Apply platform filter
      if (platformFilter.value) {
        result = result.filter(campaign => campaign.platform === platformFilter.value);
      }
      
      // Apply budget filter
      if (budgetFilter.value) {
        const [min, max] = budgetFilter.value.split('-');
        if (max === '+') {
          result = result.filter(campaign => campaign.budget >= parseInt(min));
        } else {
          result = result.filter(campaign => 
            campaign.budget >= parseInt(min) && campaign.budget <= parseInt(max)
          );
        }
      }
      
      return result;
    });
    
    const totalPages = computed(() => {
      return Math.ceil(filteredCampaigns.value.length / itemsPerPage);
    });
    
    const paginatedCampaigns = computed(() => {
      const startIndex = (currentPage.value - 1) * itemsPerPage;
      const endIndex = startIndex + itemsPerPage;
      return filteredCampaigns.value.slice(startIndex, endIndex);
    });
    
    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++;
      }
    };
    
    const prevPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--;
      }
    };
    
    const truncateText = (text, maxLength) => {
      if (!text) return '';
      if (text.length <= maxLength) return text;
      return text.substring(0, maxLength) + '...';
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
    
    const viewCampaignDetails = (campaignId) => {
      router.push(`/influencer/campaigns/${campaignId}`);
    };
    
    const applyToCampaign = (campaignId) => {
      router.push(`/influencer/campaigns/${campaignId}/apply`);
    };
    
    const campaignHasBeenAppliedTo = (campaignId) => {
      return userAdRequests.value.some(request => request.campaignId === campaignId);
    };
    
    // Initialize data
    onMounted(() => {
      fetchCampaigns();
    });
    
    return {
      campaigns,
      loading,
      error,
      searchQuery,
      categoryFilter,
      platformFilter,
      budgetFilter,
      categories,
      platforms,
      currentPage,
      totalPages,
      filteredCampaigns,
      paginatedCampaigns,
      nextPage,
      prevPage,
      truncateText,
      formatDate,
      viewCampaignDetails,
      applyToCampaign,
      fetchCampaigns,
      campaignHasBeenAppliedTo
    };
  }
}
</script>

<style scoped>
.campaigns-container {
  padding: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 1.8rem;
  color: #333;
  margin-bottom: 0.5rem;
}

.page-description {
  color: #666;
  margin-bottom: 2rem;
}

.filter-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  margin-bottom: 2rem;
  gap: 1rem;
}

.search-box {
  flex: 1;
  min-width: 250px;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.95rem;
}

.filter-group {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.filter-select {
  padding: 0.75rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  font-size: 0.95rem;
  min-width: 150px;
}

.loading-state, .error-state, .empty-state {
  text-align: center;
  padding: 3rem;
  background: #f9f9f9;
  border-radius: 8px;
  margin: 2rem 0;
}

.retry-button {
  background-color: #4a90e2;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  margin-top: 1rem;
  cursor: pointer;
}

.campaigns-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.campaign-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s, box-shadow 0.2s;
  height: 100%;
}

.campaign-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.campaign-card.applied {
  border: 2px solid #7ed321;
}

.campaign-header {
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f0f0f0;
}

.sponsor-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.sponsor-logo {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  object-fit: cover;
}

.sponsor-name {
  font-size: 0.9rem;
  font-weight: 500;
}

.campaign-category {
  font-size: 0.8rem;
  color: #666;
  background: #f5f5f5;
  padding: 0.25rem 0.5rem;
  border-radius: 20px;
}

.campaign-title {
  padding: 1rem 1rem 0.5rem;
  font-size: 1.2rem;
  color: #333;
}

.campaign-description {
  padding: 0 1rem;
  color: #666;
  line-height: 1.6;
  flex-grow: 1;
}

.campaign-details {
  padding: 1rem;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.detail-icon {
  width: 20px;
  color: #4a90e2;
}

.detail-text {
  font-size: 0.9rem;
  color: #555;
}

.campaign-footer {
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #f0f0f0;
}

.details-button, .apply-button {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  font-size: 0.9rem;
  border: none;
}

.details-button {
  background-color: transparent;
  color: #4a90e2;
  border: 1px solid #4a90e2;
}

.apply-button {
  background-color: #4a90e2;
  color: white;
}

.applied-badge {
  background-color: #7ed321;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 500;
}

.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
  padding: 1rem 0;
}

.pagination-button {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  background-color: white;
  border-radius: 4px;
  cursor: pointer;
}

.pagination-button.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 0.9rem;
  color: #666;
}

@media (max-width: 768px) {
  .filter-container {
    flex-direction: column;
  }
  
  .search-box {
    width: 100%;
  }
  
  .filter-group {
    width: 100%;
  }
  
  .campaign-footer {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .details-button, .apply-button, .applied-badge {
    width: 100%;
    text-align: center;
  }
}
</style> 