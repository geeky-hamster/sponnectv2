<template>
  <div class="admin-campaigns">
    <h1 class="text-3xl font-bold mb-6">Campaign Management</h1>
    
    <!-- Search and Filter -->
    <div class="bg-white rounded-lg shadow p-4 mb-6">
      <div class="flex flex-wrap gap-4">
        <div class="grow">
          <input 
            type="text" 
            v-model="searchTerm" 
            placeholder="Search campaigns..." 
            class="w-full p-2 border rounded"
            @input="filterCampaigns"
          />
        </div>
        <div class="flex gap-2">
          <select v-model="statusFilter" class="p-2 border rounded" @change="filterCampaigns">
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="expired">Expired</option>
            <option value="draft">Draft</option>
            <option value="flagged">Flagged</option>
          </select>
          <select v-model="categoryFilter" class="p-2 border rounded" @change="filterCampaigns">
            <option value="">All Categories</option>
            <option value="fashion">Fashion</option>
            <option value="beauty">Beauty</option>
            <option value="tech">Technology</option>
            <option value="food">Food</option>
            <option value="travel">Travel</option>
            <option value="fitness">Fitness</option>
            <option value="lifestyle">Lifestyle</option>
            <option value="gaming">Gaming</option>
            <option value="other">Other</option>
          </select>
        </div>
      </div>
    </div>
    
    <!-- Campaigns Table -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-gray-500">
        Loading campaigns...
      </div>
      
      <div v-else-if="filteredCampaigns.length === 0" class="p-8 text-center text-gray-500">
        No campaigns found matching your criteria.
      </div>
      
      <table v-else class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Campaign
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Sponsor
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Budget
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Created
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="campaign in filteredCampaigns" :key="campaign.id">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <div class="flex-shrink-0 h-10 w-10">
                  <img 
                    :src="campaign.imageUrl || '/images/default-campaign.png'" 
                    class="h-10 w-10 rounded-full object-cover"
                    alt="Campaign image"
                  >
                </div>
                <div class="ml-4">
                  <div class="text-sm font-medium text-gray-900">{{ campaign.title }}</div>
                  <div class="text-sm text-gray-500">{{ campaign.category }}</div>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm text-gray-900">{{ campaign.sponsor.companyName }}</div>
              <div class="text-sm text-gray-500">{{ campaign.sponsor.fullName }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              ${{ campaign.budget }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="[
                'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                campaign.flagged ? 'bg-red-100 text-red-800' : 
                campaign.status === 'active' ? 'bg-green-100 text-green-800' : 
                campaign.status === 'expired' ? 'bg-gray-100 text-gray-800' : 
                'bg-yellow-100 text-yellow-800'
              ]">
                {{ campaign.flagged ? 'Flagged' : capitalizeFirst(campaign.status) }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ formatDate(campaign.createdAt) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              <button
                @click="viewDetails(campaign.id)"
                class="text-blue-600 hover:text-blue-900 mr-2"
              >
                View
              </button>
              <button 
                v-if="campaign.flagged"
                @click="unflagCampaign(campaign.id)"
                class="text-blue-600 hover:text-blue-900 mr-2"
                :disabled="isProcessing"
              >
                Unflag
              </button>
              <button 
                v-else
                @click="flagCampaign(campaign.id)"
                class="text-red-600 hover:text-red-900 mr-2"
                :disabled="isProcessing"
              >
                Flag
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';

export default {
  name: 'AdminCampaigns',
  setup() {
    const store = useStore();
    const router = useRouter();
    const toast = useToast();
    
    const campaigns = ref([]);
    const filteredCampaigns = ref([]);
    const loading = ref(true);
    const isProcessing = ref(false);
    
    // Filter state
    const searchTerm = ref('');
    const statusFilter = ref('');
    const categoryFilter = ref('');
    
    // Fetch campaigns on component mount
    onMounted(async () => {
      try {
        const response = await store.dispatch('admin/fetchAllCampaigns');
        campaigns.value = response;
        filterCampaigns();
        loading.value = false;
      } catch (error) {
        toast.error('Failed to load campaigns');
        console.error('Error loading campaigns:', error);
        loading.value = false;
      }
    });
    
    // Filter campaigns based on search term and filters
    const filterCampaigns = () => {
      filteredCampaigns.value = campaigns.value.filter(campaign => {
        // Search term filter
        const searchMatch = searchTerm.value === '' || 
          campaign.title.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
          campaign.description.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
          campaign.sponsor.companyName.toLowerCase().includes(searchTerm.value.toLowerCase());
        
        // Status filter
        const statusMatch = statusFilter.value === '' || 
          (statusFilter.value === 'flagged' && campaign.flagged) ||
          (statusFilter.value === campaign.status && !campaign.flagged);
        
        // Category filter
        const categoryMatch = categoryFilter.value === '' || 
          categoryFilter.value === campaign.category.toLowerCase();
        
        return searchMatch && statusMatch && categoryMatch;
      });
    };
    
    // Campaign actions
    const flagCampaign = async (campaignId) => {
      isProcessing.value = true;
      try {
        await store.dispatch('admin/flagCampaign', campaignId);
        // Update local state
        const campaignIndex = campaigns.value.findIndex(c => c.id === campaignId);
        if (campaignIndex !== -1) {
          campaigns.value[campaignIndex].flagged = true;
          filterCampaigns();
        }
        toast.success('Campaign has been flagged');
      } catch (error) {
        toast.error('Failed to flag campaign');
        console.error('Error flagging campaign:', error);
      } finally {
        isProcessing.value = false;
      }
    };
    
    const unflagCampaign = async (campaignId) => {
      isProcessing.value = true;
      try {
        await store.dispatch('admin/unflagCampaign', campaignId);
        // Update local state
        const campaignIndex = campaigns.value.findIndex(c => c.id === campaignId);
        if (campaignIndex !== -1) {
          campaigns.value[campaignIndex].flagged = false;
          filterCampaigns();
        }
        toast.success('Campaign has been unflagged');
      } catch (error) {
        toast.error('Failed to unflag campaign');
        console.error('Error unflagging campaign:', error);
      } finally {
        isProcessing.value = false;
      }
    };
    
    const viewDetails = (campaignId) => {
      router.push({ name: 'SponsorCampaignDetail', params: { id: campaignId } });
    };
    
    // Helper methods
    const formatDate = (dateString) => {
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
      filteredCampaigns,
      loading,
      isProcessing,
      searchTerm,
      statusFilter,
      categoryFilter,
      filterCampaigns,
      flagCampaign,
      unflagCampaign,
      viewDetails,
      formatDate,
      capitalizeFirst
    };
  }
};
</script>

<style scoped>
.admin-campaigns {
  @apply py-6 px-4 max-w-7xl mx-auto;
}
</style> 