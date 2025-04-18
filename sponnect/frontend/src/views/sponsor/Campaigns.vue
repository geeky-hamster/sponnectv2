<template>
  <div class="sponsor-campaigns">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold">Your Campaigns</h1>
      <router-link 
        to="/sponsor/campaigns/create" 
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
      >
        Create Campaign
      </router-link>
    </div>
    
    <!-- Campaign Cards -->
    <div v-if="loading" class="text-center py-12">
      <div class="spinner-border text-primary" role="status">
        <span class="sr-only">Loading...</span>
      </div>
    </div>
    
    <div v-else-if="campaigns.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
      <div class="text-7xl mb-4">🚀</div>
      <h3 class="text-2xl font-semibold mb-2">Create Your First Campaign</h3>
      <p class="text-gray-600 mb-6">
        Get started by creating your first advertising campaign to connect with influencers.
      </p>
      <router-link 
        to="/sponsor/campaigns/create" 
        class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
      >
        Create Campaign
      </router-link>
    </div>
    
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="campaign in campaigns" :key="campaign.id" class="bg-white rounded-lg shadow overflow-hidden transition-all duration-300 hover:shadow-lg">
        <div 
          class="h-48 bg-cover bg-center" 
          :style="{ backgroundImage: `url(${campaign.imageUrl || '/images/default-campaign.png'})` }"
        ></div>
        
        <div class="p-4">
          <div class="flex justify-between items-start mb-2">
            <h3 class="text-xl font-semibold">{{ campaign.title }}</h3>
            <span :class="[
              'px-2 py-1 text-xs font-semibold rounded-full',
              campaign.status === 'active' ? 'bg-green-100 text-green-800' : 
              campaign.status === 'expired' ? 'bg-gray-100 text-gray-800' : 
              'bg-yellow-100 text-yellow-800'
            ]">
              {{ capitalizeFirst(campaign.status) }}
            </span>
          </div>
          
          <p class="text-gray-600 text-sm mb-4 line-clamp-2">{{ campaign.description }}</p>
          
          <div class="flex justify-between text-sm text-gray-500 mb-4">
            <div>Budget: <span class="font-semibold">${{ campaign.budget }}</span></div>
            <div>Category: <span class="font-semibold">{{ campaign.category }}</span></div>
          </div>
          
          <div class="flex justify-between text-sm text-gray-500 mb-4">
            <div>Created: <span class="font-semibold">{{ formatDate(campaign.createdAt) }}</span></div>
            <div>
              <span v-if="campaign.status === 'active'" class="text-gray-500">
                Expires: <span class="font-semibold">{{ formatDate(campaign.expiresAt) }}</span>
              </span>
            </div>
          </div>
          
          <div class="border-t pt-4 mt-2 flex justify-between">
            <router-link 
              :to="`/sponsor/campaigns/${campaign.id}`" 
              class="text-blue-600 hover:text-blue-800"
            >
              View Details
            </router-link>
            
            <div>
              <button 
                v-if="campaign.status !== 'expired'"
                @click="editCampaign(campaign.id)" 
                class="text-gray-600 hover:text-gray-800 mr-2"
              >
                Edit
              </button>
              <button 
                @click="deleteCampaign(campaign.id)" 
                class="text-red-600 hover:text-red-800"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Confirmation Modal -->
    <div 
      v-if="showDeleteModal" 
      class="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50"
      @click.self="cancelDelete"
    >
      <div class="bg-white rounded-lg w-full max-w-md p-6">
        <h3 class="text-lg font-bold mb-4">Confirm Deletion</h3>
        <p class="mb-6">
          Are you sure you want to delete this campaign? This action cannot be undone.
        </p>
        <div class="flex justify-end space-x-4">
          <button 
            @click="cancelDelete" 
            class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100"
          >
            Cancel
          </button>
          <button 
            @click="confirmDelete" 
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            :disabled="isDeleting"
          >
            {{ isDeleting ? 'Deleting...' : 'Delete' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';

export default {
  name: 'SponsorCampaigns',
  setup() {
    const store = useStore();
    const router = useRouter();
    const toast = useToast();
    
    const campaigns = ref([]);
    const loading = ref(true);
    
    // Delete modal state
    const showDeleteModal = ref(false);
    const campaignToDelete = ref(null);
    const isDeleting = ref(false);
    
    // Fetch campaigns on component mount
    onMounted(async () => {
      try {
        const response = await store.dispatch('campaigns/fetchSponsorCampaigns');
        campaigns.value = response;
        loading.value = false;
      } catch (error) {
        toast.error('Failed to load campaigns');
        console.error('Error loading campaigns:', error);
        loading.value = false;
      }
    });
    
    // Actions
    const editCampaign = (campaignId) => {
      router.push({ name: 'SponsorEditCampaign', params: { id: campaignId } });
    };
    
    const deleteCampaign = (campaignId) => {
      campaignToDelete.value = campaignId;
      showDeleteModal.value = true;
    };
    
    const cancelDelete = () => {
      showDeleteModal.value = false;
      campaignToDelete.value = null;
    };
    
    const confirmDelete = async () => {
      if (!campaignToDelete.value) return;
      
      isDeleting.value = true;
      try {
        await store.dispatch('campaigns/deleteCampaign', campaignToDelete.value);
        // Remove from local state
        campaigns.value = campaigns.value.filter(c => c.id !== campaignToDelete.value);
        toast.success('Campaign deleted successfully');
      } catch (error) {
        toast.error('Failed to delete campaign');
        console.error('Error deleting campaign:', error);
      } finally {
        isDeleting.value = false;
        showDeleteModal.value = false;
        campaignToDelete.value = null;
      }
    };
    
    // Helper methods
    const formatDate = (dateString) => {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      }).format(date);
    };
    
    const capitalizeFirst = (str) => {
      return str.charAt(0).toUpperCase() + str.slice(1);
    };
    
    return {
      campaigns,
      loading,
      showDeleteModal,
      isDeleting,
      editCampaign,
      deleteCampaign,
      cancelDelete,
      confirmDelete,
      formatDate,
      capitalizeFirst
    };
  }
};
</script>

<style scoped>
.sponsor-campaigns {
  @apply py-6 px-4 max-w-7xl mx-auto;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style> 