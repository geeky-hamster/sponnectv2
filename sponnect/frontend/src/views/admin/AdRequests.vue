<template>
  <div class="admin-requests">
    <h1 class="text-3xl font-bold mb-6">Ad Request Management</h1>
    
    <!-- Search and Filter -->
    <div class="bg-white rounded-lg shadow p-4 mb-6">
      <div class="flex flex-wrap gap-4">
        <div class="grow">
          <input 
            type="text" 
            v-model="searchTerm" 
            placeholder="Search ad requests..." 
            class="w-full p-2 border rounded"
            @input="filterRequests"
          />
        </div>
        <div class="flex gap-2">
          <select v-model="statusFilter" class="p-2 border rounded" @change="filterRequests">
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="accepted">Accepted</option>
            <option value="rejected">Rejected</option>
            <option value="completed">Completed</option>
            <option value="negotiating">Negotiating</option>
          </select>
          <select v-model="sortOrder" class="p-2 border rounded" @change="filterRequests">
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
            <option value="budget-high">Budget (High to Low)</option>
            <option value="budget-low">Budget (Low to High)</option>
          </select>
        </div>
      </div>
    </div>
    
    <!-- Ad Requests Table -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-gray-500">
        Loading ad requests...
      </div>
      
      <div v-else-if="filteredRequests.length === 0" class="p-8 text-center text-gray-500">
        No ad requests found matching your criteria.
      </div>
      
      <table v-else class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Ad Request
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Campaign
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Parties
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
          <tr v-for="request in filteredRequests" :key="request.id">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm font-medium text-gray-900">#{{ request.id }}</div>
              <div class="text-sm text-gray-500">{{ request.adType }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm font-medium text-gray-900">{{ request.campaign.title }}</div>
              <div class="text-sm text-gray-500">{{ request.campaign.category }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm text-gray-900">{{ request.sponsor.companyName }}</div>
              <div class="text-sm text-gray-500">{{ request.influencer.fullName }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              ${{ request.price }}
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
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
              <button 
                @click="viewDetails(request.id)" 
                class="text-blue-600 hover:text-blue-900 mr-2"
              >
                View
              </button>
              <button 
                v-if="request.status === 'Completed'"
                @click="viewProof(request.id)" 
                class="text-indigo-600 hover:text-indigo-900"
              >
                View Proof
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Proof Modal -->
    <div 
      v-if="showProofModal" 
      class="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50"
      @click.self="closeProofModal"
    >
      <div class="bg-white rounded-lg w-full max-w-2xl p-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold">Completion Proof</h3>
          <button @click="closeProofModal" class="text-gray-500 hover:text-gray-700">
            <span class="text-2xl">&times;</span>
          </button>
        </div>
        
        <div v-if="selectedRequest" class="mb-4">
          <div class="mb-4">
            <p class="text-sm text-gray-500 mb-1">Request ID: #{{ selectedRequest.id }}</p>
            <p class="text-sm text-gray-500 mb-1">Campaign: {{ selectedRequest.campaign.title }}</p>
            <p class="text-sm text-gray-500">Completed: {{ formatDate(selectedRequest.completedAt) }}</p>
          </div>
          
          <div class="mb-4">
            <h4 class="font-medium mb-2">Proof of Completion</h4>
            <p class="text-gray-700 mb-2">{{ selectedRequest.completionDetails }}</p>
            
            <div v-if="selectedRequest.proofUrls && selectedRequest.proofUrls.length">
              <div class="grid grid-cols-2 gap-2">
                <div v-for="(url, index) in selectedRequest.proofUrls" :key="index" class="mb-2">
                  <img 
                    :src="url" 
                    alt="Proof image" 
                    class="w-full rounded border border-gray-200 cursor-pointer"
                    @click="openLightbox(url)"
                  >
                </div>
              </div>
            </div>
            
            <div v-if="selectedRequest.proofLink" class="mt-2">
              <a :href="selectedRequest.proofLink" target="_blank" class="text-blue-600 hover:underline">
                View external proof (opens in new tab)
              </a>
            </div>
          </div>
        </div>
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
  name: 'AdminAdRequests',
  setup() {
    const store = useStore();
    const router = useRouter();
    const toast = useToast();
    
    const requests = ref([]);
    const filteredRequests = ref([]);
    const loading = ref(true);
    const isProcessing = ref(false);
    
    // Filter state
    const searchTerm = ref('');
    const statusFilter = ref('');
    const sortOrder = ref('newest');
    
    // Modal state
    const showProofModal = ref(false);
    const selectedRequest = ref(null);
    
    // Fetch ad requests on component mount
    onMounted(async () => {
      try {
        const response = await store.dispatch('admin/fetchAllAdRequests');
        requests.value = response;
        filterRequests();
        loading.value = false;
      } catch (error) {
        toast.error('Failed to load ad requests');
        console.error('Error loading ad requests:', error);
        loading.value = false;
      }
    });
    
    // Filter and sort ad requests based on search term and filters
    const filterRequests = () => {
      let filtered = requests.value.filter(request => {
        // Search term filter
        const searchMatch = searchTerm.value === '' || 
          request.campaign.title.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
          request.sponsor.companyName.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
          request.influencer.fullName.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
          String(request.id).includes(searchTerm.value);
        
        // Status filter
        const statusMatch = statusFilter.value === '' || 
          request.status.toLowerCase() === statusFilter.value.toLowerCase();
        
        return searchMatch && statusMatch;
      });
      
      // Sort filtered results
      filtered = sortRequests(filtered);
      
      filteredRequests.value = filtered;
    };
    
    // Sort requests based on sort order
    const sortRequests = (requests) => {
      switch (sortOrder.value) {
        case 'newest':
          return [...requests].sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
        case 'oldest':
          return [...requests].sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
        case 'budget-high':
          return [...requests].sort((a, b) => b.price - a.price);
        case 'budget-low':
          return [...requests].sort((a, b) => a.price - b.price);
        default:
          return requests;
      }
    };
    
    // View request details
    const viewDetails = (requestId) => {
      // For admin, we'll use the sponsor's view since it's more complete
      router.push({ name: 'SponsorAdRequestDetail', params: { id: requestId } });
    };
    
    // View completion proof
    const viewProof = async (requestId) => {
      isProcessing.value = true;
      try {
        // Fetch request details if not already in state
        const request = requests.value.find(r => r.id === requestId);
        if (request && request.status === 'Completed') {
          selectedRequest.value = request;
          showProofModal.value = true;
        } else {
          toast.error('Proof is only available for completed requests');
        }
      } catch (error) {
        toast.error('Failed to load proof details');
        console.error('Error loading proof details:', error);
      } finally {
        isProcessing.value = false;
      }
    };
    
    const closeProofModal = () => {
      showProofModal.value = false;
      selectedRequest.value = null;
    };
    
    const openLightbox = (imageUrl) => {
      // In a real app, implement a full-screen lightbox for the image
      window.open(imageUrl, '_blank');
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
    
    return {
      requests,
      filteredRequests,
      loading,
      isProcessing,
      searchTerm,
      statusFilter,
      sortOrder,
      showProofModal,
      selectedRequest,
      filterRequests,
      viewDetails,
      viewProof,
      closeProofModal,
      openLightbox,
      formatDate
    };
  }
};
</script>

<style scoped>
.admin-requests {
  @apply py-6 px-4 max-w-7xl mx-auto;
}
</style> 