<template>
  <div class="ad-requests-container">
    <h1 class="page-title">My Ad Requests</h1>
    <p class="page-description">Track and manage your campaign applications and ongoing ad collaborations.</p>
    
    <div class="filter-container">
      <div class="tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.value"
          @click="currentTab = tab.value"
          class="tab-button"
          :class="{ active: currentTab === tab.value }"
        >
          {{ tab.label }}
          <span v-if="getRequestCountByStatus(tab.value) > 0" class="tab-count">
            {{ getRequestCountByStatus(tab.value) }}
          </span>
        </button>
      </div>
      
      <div class="search-box">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Search requests..."
          class="search-input"
        />
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <p>Loading your ad requests...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="fetchAdRequests" class="retry-button">Retry</button>
    </div>

    <div v-else-if="filteredRequests.length === 0" class="empty-state">
      <div v-if="searchQuery">
        <p>No requests match your search criteria.</p>
        <button @click="searchQuery = ''" class="clear-button">Clear Search</button>
      </div>
      <div v-else>
        <p v-if="currentTab === 'all'">You haven't applied to any campaigns yet.</p>
        <p v-else-if="currentTab === 'pending'">You don't have any pending requests.</p>
        <p v-else-if="currentTab === 'approved'">You don't have any approved requests.</p>
        <p v-else-if="currentTab === 'active'">You don't have any active collaborations.</p>
        <p v-else-if="currentTab === 'completed'">You don't have any completed collaborations.</p>
        <p v-else-if="currentTab === 'rejected'">You don't have any rejected requests.</p>
        <p v-else-if="currentTab === 'canceled'">You don't have any canceled requests.</p>
        
        <div v-if="currentTab === 'all' || currentTab === 'pending'">
          <router-link to="/influencer/campaigns" class="browse-link">
            Browse Available Campaigns
          </router-link>
        </div>
      </div>
    </div>

    <div v-else class="requests-table-container">
      <table class="requests-table">
        <thead>
          <tr>
            <th>Campaign</th>
            <th>Sponsor</th>
            <th>Submitted</th>
            <th>Status</th>
            <th>Budget</th>
            <th>Due Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="request in paginatedRequests" 
            :key="request.id"
            :class="getRequestRowClass(request.status)"
          >
            <td class="campaign-cell">
              <div class="campaign-info">
                <img 
                  v-if="request.campaign.thumbnailUrl" 
                  :src="request.campaign.thumbnailUrl" 
                  :alt="request.campaign.title"
                  class="campaign-thumbnail"
                />
                <div v-else class="campaign-thumbnail placeholder">
                  <i class="fas fa-image"></i>
                </div>
                <span class="campaign-title">{{ request.campaign.title }}</span>
              </div>
            </td>
            <td>
              <div class="sponsor-info">
                <img 
                  :src="request.sponsor.profileImage || '/img/default-company.png'" 
                  alt="Sponsor Logo" 
                  class="sponsor-logo"
                />
                <span>{{ request.sponsor.name }}</span>
              </div>
            </td>
            <td>{{ formatDate(request.createdAt) }}</td>
            <td>
              <span class="status-badge" :class="getStatusClass(request.status)">
                {{ formatStatus(request.status) }}
              </span>
            </td>
            <td>${{ request.budget }}</td>
            <td>
              <span :class="{ 'overdue': isOverdue(request.dueDate) }">
                {{ formatDate(request.dueDate) }}
              </span>
            </td>
            <td>
              <div class="action-buttons">
                <button 
                  @click="viewRequestDetails(request.id)" 
                  class="action-button view-button"
                  title="View Details"
                >
                  <i class="fas fa-eye"></i>
                </button>
                
                <button 
                  v-if="request.status === 'approved'"
                  @click="startWork(request.id)" 
                  class="action-button start-button"
                  title="Start Work"
                >
                  <i class="fas fa-play"></i>
                </button>
                
                <button 
                  v-if="request.status === 'active'"
                  @click="submitWork(request.id)" 
                  class="action-button submit-button"
                  title="Submit Work"
                >
                  <i class="fas fa-check"></i>
                </button>
                
                <button 
                  v-if="canBeCanceled(request.status)"
                  @click="cancelRequest(request.id)" 
                  class="action-button cancel-button"
                  title="Cancel Request"
                >
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="filteredRequests.length > 0" class="pagination-controls">
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
  name: 'InfluencerAdRequests',
  
  setup() {
    const store = useStore();
    const router = useRouter();
    
    const adRequests = ref([]);
    const loading = ref(true);
    const error = ref(null);
    const searchQuery = ref('');
    const currentTab = ref('all');
    const currentPage = ref(1);
    const itemsPerPage = 10;
    
    const tabs = [
      { label: 'All Requests', value: 'all' },
      { label: 'Pending', value: 'pending' },
      { label: 'Approved', value: 'approved' },
      { label: 'Active', value: 'active' },
      { label: 'Completed', value: 'completed' },
      { label: 'Rejected', value: 'rejected' },
      { label: 'Canceled', value: 'canceled' }
    ];
    
    const fetchAdRequests = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        // Replace with actual API call when implemented
        const response = await store.dispatch('adRequests/getMyAdRequests');
        adRequests.value = response;
      } catch (err) {
        error.value = 'Failed to load ad requests. Please try again.';
        console.error(err);
      } finally {
        loading.value = false;
      }
    };
    
    const filteredRequests = computed(() => {
      let result = [...adRequests.value];
      
      // Apply tab filter
      if (currentTab.value !== 'all') {
        result = result.filter(request => request.status === currentTab.value);
      }
      
      // Apply search filter
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        result = result.filter(request => 
          request.campaign.title.toLowerCase().includes(query) || 
          request.sponsor.name.toLowerCase().includes(query)
        );
      }
      
      // Sort by date (newest first)
      result.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
      
      return result;
    });
    
    const totalPages = computed(() => {
      return Math.ceil(filteredRequests.value.length / itemsPerPage);
    });
    
    const paginatedRequests = computed(() => {
      const startIndex = (currentPage.value - 1) * itemsPerPage;
      const endIndex = startIndex + itemsPerPage;
      return filteredRequests.value.slice(startIndex, endIndex);
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
    
    const formatDate = (dateString) => {
      if (!dateString) return 'N/A';
      
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    };
    
    const formatStatus = (status) => {
      if (!status) return 'Unknown';
      
      const statusMap = {
        'pending': 'Pending',
        'approved': 'Approved',
        'active': 'In Progress',
        'completed': 'Completed',
        'rejected': 'Rejected',
        'canceled': 'Canceled'
      };
      
      return statusMap[status] || status;
    };
    
    const getStatusClass = (status) => {
      return `status-${status}`;
    };
    
    const getRequestRowClass = (status) => {
      return `row-status-${status}`;
    };
    
    const isOverdue = (dueDate) => {
      if (!dueDate) return false;
      
      const now = new Date();
      const due = new Date(dueDate);
      return due < now;
    };
    
    const canBeCanceled = (status) => {
      return ['pending', 'approved'].includes(status);
    };
    
    const getRequestCountByStatus = (status) => {
      if (status === 'all') {
        return adRequests.value.length;
      }
      
      return adRequests.value.filter(request => request.status === status).length;
    };
    
    const viewRequestDetails = (requestId) => {
      router.push(`/influencer/ad-requests/${requestId}`);
    };
    
    const startWork = async (requestId) => {
      try {
        await store.dispatch('adRequests/startWork', requestId);
        fetchAdRequests();
      } catch (err) {
        console.error('Failed to start work:', err);
      }
    };
    
    const submitWork = (requestId) => {
      router.push(`/influencer/ad-requests/${requestId}/submit`);
    };
    
    const cancelRequest = async (requestId) => {
      if (!confirm('Are you sure you want to cancel this request? This action cannot be undone.')) {
        return;
      }
      
      try {
        await store.dispatch('adRequests/cancelRequest', requestId);
        fetchAdRequests();
      } catch (err) {
        console.error('Failed to cancel request:', err);
      }
    };
    
    // Initialize data
    onMounted(() => {
      fetchAdRequests();
    });
    
    return {
      adRequests,
      loading,
      error,
      searchQuery,
      currentTab,
      tabs,
      currentPage,
      totalPages,
      filteredRequests,
      paginatedRequests,
      nextPage,
      prevPage,
      formatDate,
      formatStatus,
      getStatusClass,
      getRequestRowClass,
      isOverdue,
      canBeCanceled,
      getRequestCountByStatus,
      viewRequestDetails,
      startWork,
      submitWork,
      cancelRequest,
      fetchAdRequests
    };
  }
}
</script>

<style scoped>
.ad-requests-container {
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

.tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tab-button {
  padding: 0.5rem 1rem;
  border: none;
  background-color: #f5f5f5;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  position: relative;
}

.tab-button.active {
  background-color: #4a90e2;
  color: white;
}

.tab-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background-color: #ff6b6b;
  color: white;
  border-radius: 50%;
  min-width: 1.25rem;
  height: 1.25rem;
  font-size: 0.75rem;
  margin-left: 0.5rem;
  padding: 0 0.25rem;
}

.tab-button.active .tab-count {
  background-color: white;
  color: #4a90e2;
}

.search-box {
  flex: 1;
  max-width: 300px;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.95rem;
}

.loading-state, .error-state, .empty-state {
  text-align: center;
  padding: 3rem;
  background: #f9f9f9;
  border-radius: 8px;
  margin: 2rem 0;
}

.retry-button, .clear-button {
  background-color: #4a90e2;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  margin-top: 1rem;
  cursor: pointer;
}

.browse-link {
  display: inline-block;
  background-color: #4a90e2;
  color: white;
  text-decoration: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  margin-top: 1.5rem;
  font-weight: 500;
}

.requests-table-container {
  overflow-x: auto;
}

.requests-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 2rem;
}

.requests-table th {
  background-color: #f5f5f5;
  color: #333;
  font-weight: 600;
  text-align: left;
  padding: 1rem;
  border-bottom: 2px solid #ddd;
}

.requests-table td {
  padding: 1rem;
  border-bottom: 1px solid #eee;
}

.campaign-cell {
  min-width: 200px;
}

.campaign-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.campaign-thumbnail {
  width: 50px;
  height: 50px;
  border-radius: 4px;
  object-fit: cover;
}

.campaign-thumbnail.placeholder {
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #aaa;
}

.campaign-title {
  font-weight: 500;
}

.sponsor-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sponsor-logo {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
}

.status-badge {
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  display: inline-block;
}

.status-pending {
  background-color: #f0ad4e;
  color: white;
}

.status-approved {
  background-color: #5bc0de;
  color: white;
}

.status-active {
  background-color: #5cb85c;
  color: white;
}

.status-completed {
  background-color: #7ed321;
  color: white;
}

.status-rejected {
  background-color: #d9534f;
  color: white;
}

.status-canceled {
  background-color: #777;
  color: white;
}

.row-status-active {
  background-color: rgba(92, 184, 92, 0.05);
}

.row-status-approved {
  background-color: rgba(91, 192, 222, 0.05);
}

.row-status-completed {
  background-color: rgba(126, 211, 33, 0.05);
}

.overdue {
  color: #d9534f;
  font-weight: 500;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.action-button {
  width: 2rem;
  height: 2rem;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.view-button {
  background-color: #f5f5f5;
  color: #555;
}

.start-button {
  background-color: #5bc0de;
  color: white;
}

.submit-button {
  background-color: #5cb85c;
  color: white;
}

.cancel-button {
  background-color: #d9534f;
  color: white;
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

@media (max-width: 900px) {
  .requests-table {
    font-size: 0.85rem;
  }
  
  .requests-table th,
  .requests-table td {
    padding: 0.75rem 0.5rem;
  }
  
  .campaign-thumbnail {
    width: 40px;
    height: 40px;
  }
}

@media (max-width: 768px) {
  .filter-container {
    flex-direction: column;
  }
  
  .tabs {
    width: 100%;
    overflow-x: auto;
    white-space: nowrap;
    padding-bottom: 0.5rem;
  }
  
  .search-box {
    width: 100%;
    max-width: none;
  }
}
</style> 