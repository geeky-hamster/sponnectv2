<template>
  <div class="sponsor-requests">
    <h1 class="text-3xl font-bold mb-6">Ad Requests</h1>
    
    <!-- Filters -->
    <div class="bg-white rounded-lg shadow p-4 mb-6">
      <div class="flex flex-wrap gap-4">
        <div class="grow">
          <input 
            type="text" 
            v-model="searchTerm" 
            placeholder="Search by influencer name, campaign title..." 
            class="w-full p-2 border rounded"
            @input="filterRequests"
          />
        </div>
        <div class="flex gap-2">
          <select v-model="statusFilter" class="p-2 border rounded" @change="filterRequests">
            <option value="">All Status</option>
            <option value="Pending">Pending</option>
            <option value="Accepted">Accepted</option>
            <option value="Rejected">Rejected</option>
            <option value="Completed">Completed</option>
            <option value="Negotiating">Negotiating</option>
          </select>
          <select v-model="campaignFilter" class="p-2 border rounded" @change="filterRequests">
            <option value="">All Campaigns</option>
            <option v-for="campaign in uniqueCampaigns" :key="campaign.id" :value="campaign.id">
              {{ campaign.title }}
            </option>
          </select>
        </div>
      </div>
    </div>
    
    <!-- Ad Requests -->
    <div v-if="loading" class="text-center py-12">
      <div class="spinner-border text-primary" role="status">
        <span class="sr-only">Loading...</span>
      </div>
    </div>
    
    <div v-else-if="filteredRequests.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
      <div class="text-7xl mb-4">📝</div>
      <h3 class="text-2xl font-semibold mb-2">No Ad Requests Found</h3>
      <p class="text-gray-600 mb-6">
        {{ 
          searchTerm || statusFilter || campaignFilter 
            ? 'No ad requests match your current filters. Try adjusting your search criteria.' 
            : 'You don\'t have any ad requests yet. Create campaigns to attract influencers or invite them directly.'
        }}
      </p>
      <router-link 
        to="/sponsor/campaigns" 
        class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
      >
        Manage Campaigns
      </router-link>
    </div>
    
    <div v-else>
      <div class="bg-white rounded-lg shadow overflow-hidden mb-6">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Influencer
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Campaign
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Details
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="request in filteredRequests" :key="request.id">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-10 w-10">
                    <img 
                      :src="request.influencer.profileImage || '/images/default-avatar.png'" 
                      class="h-10 w-10 rounded-full object-cover"
                      alt="Influencer avatar"
                    >
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">{{ request.influencer.fullName }}</div>
                    <div class="text-sm text-gray-500">@{{ request.influencer.username }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ request.campaign.title }}</div>
                <div class="text-sm text-gray-500">{{ request.campaign.category }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ request.adType }}</div>
                <div class="text-sm text-gray-500">${{ request.price }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="[
                  'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                  request.status === 'Accepted' ? 'bg-green-100 text-green-800' : 
                  request.status === 'Rejected' ? 'bg-red-100 text-red-800' : 
                  request.status === 'Completed' ? 'bg-blue-100 text-blue-800' : 
                  request.status === 'Negotiating' ? 'bg-yellow-100 text-yellow-800' : 
                  'bg-gray-100 text-gray-800'
                ]">
                  {{ request.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(request.createdAt) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <router-link 
                  :to="`/sponsor/requests/${request.id}`" 
                  class="text-blue-600 hover:text-blue-900"
                >
                  View Details
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';

export default {
  name: 'SponsorAdRequests',
  setup() {
    const store = useStore();
    const router = useRouter();
    const toast = useToast();
    
    const requests = ref([]);
    const filteredRequests = ref([]);
    const loading = ref(true);
    
    // Filter state
    const searchTerm = ref('');
    const statusFilter = ref('');
    const campaignFilter = ref('');
    
    // Fetch ad requests on component mount
    onMounted(async () => {
      try {
        const response = await store.dispatch('adRequests/fetchSponsorRequests');
        requests.value = response;
        filterRequests();
        loading.value = false;
      } catch (error) {
        toast.error('Failed to load ad requests');
        console.error('Error loading ad requests:', error);
        loading.value = false;
      }
    });
    
    // Get unique campaigns for filtering
    const uniqueCampaigns = computed(() => {
      const campaignMap = {};
      requests.value.forEach(request => {
        if (!campaignMap[request.campaign.id]) {
          campaignMap[request.campaign.id] = request.campaign;
        }
      });
      return Object.values(campaignMap);
    });
    
    // Filter ad requests based on search term and filters
    const filterRequests = () => {
      filteredRequests.value = requests.value.filter(request => {
        // Search term filter
        const searchMatch = searchTerm.value === '' || 
          request.influencer.fullName.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
          request.influencer.username.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
          request.campaign.title.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
          request.adType.toLowerCase().includes(searchTerm.value.toLowerCase());
        
        // Status filter
        const statusMatch = statusFilter.value === '' || request.status === statusFilter.value;
        
        // Campaign filter
        const campaignMatch = campaignFilter.value === '' || request.campaign.id.toString() === campaignFilter.value;
        
        return searchMatch && statusMatch && campaignMatch;
      });
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
    
    return {
      requests,
      filteredRequests,
      loading,
      searchTerm,
      statusFilter,
      campaignFilter,
      uniqueCampaigns,
      filterRequests,
      formatDate
    };
  }
};
</script>

<style scoped>
.sponsor-requests {
  @apply py-6 px-4 max-w-7xl mx-auto;
}
</style> 