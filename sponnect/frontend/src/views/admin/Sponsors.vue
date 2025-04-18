<template>
  <div class="admin-sponsors">
    <h1 class="text-3xl font-bold mb-6">Sponsor Approval</h1>
    
    <!-- Tabs -->
    <div class="bg-white rounded-lg shadow p-4 mb-6">
      <div class="flex border-b">
        <button 
          @click="activeTab = 'pending'" 
          class="py-2 px-4 mr-2"
          :class="{ 'border-b-2 border-blue-500 font-semibold': activeTab === 'pending' }"
        >
          Pending Approval
        </button>
        <button 
          @click="activeTab = 'approved'" 
          class="py-2 px-4 mr-2"
          :class="{ 'border-b-2 border-blue-500 font-semibold': activeTab === 'approved' }"
        >
          Approved
        </button>
        <button 
          @click="activeTab = 'rejected'" 
          class="py-2 px-4"
          :class="{ 'border-b-2 border-blue-500 font-semibold': activeTab === 'rejected' }"
        >
          Rejected
        </button>
      </div>
    </div>
    
    <!-- Sponsors Table -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-gray-500">
        Loading sponsors...
      </div>
      
      <div v-else-if="filteredSponsors.length === 0" class="p-8 text-center text-gray-500">
        No sponsors found in this category.
      </div>
      
      <table v-else class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Company
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Contact
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Website
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Applied
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="sponsor in filteredSponsors" :key="sponsor.id">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <div class="flex-shrink-0 h-10 w-10">
                  <img 
                    :src="sponsor.logo || '/images/default-company.png'" 
                    class="h-10 w-10 rounded-full object-cover"
                    alt="Company logo"
                  >
                </div>
                <div class="ml-4">
                  <div class="text-sm font-medium text-gray-900">{{ sponsor.companyName }}</div>
                  <div class="text-sm text-gray-500">{{ sponsor.industry }}</div>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm text-gray-900">{{ sponsor.fullName }}</div>
              <div class="text-sm text-gray-500">{{ sponsor.email }}</div>
              <div class="text-sm text-gray-500">{{ sponsor.phone }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              <a 
                :href="formatWebsite(sponsor.website)" 
                target="_blank" 
                class="text-blue-600 hover:underline"
              >
                {{ sponsor.website }}
              </a>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ formatDate(sponsor.createdAt) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="[
                'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                sponsor.status === 'approved' ? 'bg-green-100 text-green-800' : 
                sponsor.status === 'rejected' ? 'bg-red-100 text-red-800' : 
                'bg-yellow-100 text-yellow-800'
              ]">
                {{ capitalizeFirst(sponsor.status) }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              <div v-if="sponsor.status === 'pending'">
                <button 
                  @click="approveSponsor(sponsor.id)" 
                  class="text-green-600 hover:text-green-900 mr-3"
                  :disabled="isProcessing"
                >
                  Approve
                </button>
                <button 
                  @click="rejectSponsor(sponsor.id)" 
                  class="text-red-600 hover:text-red-900"
                  :disabled="isProcessing"
                >
                  Reject
                </button>
              </div>
              <div v-else-if="sponsor.status === 'approved'">
                <button 
                  @click="viewDetails(sponsor.id)" 
                  class="text-blue-600 hover:text-blue-900 mr-3"
                >
                  View Profile
                </button>
              </div>
              <div v-else>
                <button 
                  @click="reconsiderSponsor(sponsor.id)" 
                  class="text-blue-600 hover:text-blue-900"
                  :disabled="isProcessing"
                >
                  Reconsider
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Details Modal -->
    <div 
      v-if="showModal" 
      class="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50"
      @click.self="closeModal"
    >
      <div class="bg-white rounded-lg w-full max-w-2xl p-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold">Sponsor Details</h3>
          <button @click="closeModal" class="text-gray-500 hover:text-gray-700">
            <span class="text-2xl">&times;</span>
          </button>
        </div>
        
        <div v-if="selectedSponsor" class="mb-4">
          <div class="flex items-start mb-6">
            <div class="mr-4">
              <img 
                :src="selectedSponsor.logo || '/images/default-company.png'" 
                class="h-24 w-24 rounded object-cover"
                alt="Company logo"
              >
            </div>
            <div>
              <h2 class="text-xl font-bold mb-1">{{ selectedSponsor.companyName }}</h2>
              <p class="text-gray-600 mb-2">{{ selectedSponsor.industry }}</p>
              <a 
                :href="formatWebsite(selectedSponsor.website)" 
                target="_blank" 
                class="text-blue-600 hover:underline"
              >
                {{ selectedSponsor.website }}
              </a>
            </div>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <h3 class="font-semibold mb-2">Contact Information</h3>
              <p class="text-gray-700 mb-1">{{ selectedSponsor.fullName }}</p>
              <p class="text-gray-700 mb-1">{{ selectedSponsor.email }}</p>
              <p class="text-gray-700">{{ selectedSponsor.phone }}</p>
            </div>
            <div>
              <h3 class="font-semibold mb-2">Company Details</h3>
              <p class="text-gray-700 mb-1">Size: {{ selectedSponsor.companySize || 'Not specified' }}</p>
              <p class="text-gray-700 mb-1">Founded: {{ selectedSponsor.foundedYear || 'Not specified' }}</p>
              <p class="text-gray-700">Location: {{ selectedSponsor.location || 'Not specified' }}</p>
            </div>
          </div>
          
          <div class="mb-6">
            <h3 class="font-semibold mb-2">About the Company</h3>
            <p class="text-gray-700">{{ selectedSponsor.description || 'No description provided.' }}</p>
          </div>
          
          <div>
            <h3 class="font-semibold mb-2">Application Details</h3>
            <p class="text-gray-700 mb-1">Applied: {{ formatDate(selectedSponsor.createdAt) }}</p>
            <p class="text-gray-700 mb-1">Status: {{ capitalizeFirst(selectedSponsor.status) }}</p>
            <p v-if="selectedSponsor.status === 'approved'" class="text-gray-700">
              Approved: {{ formatDate(selectedSponsor.approvedAt) }}
            </p>
            <p v-if="selectedSponsor.status === 'rejected'" class="text-gray-700">
              Rejected: {{ formatDate(selectedSponsor.rejectedAt) }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { useStore } from 'vuex';
import { useToast } from 'vue-toastification';

export default {
  name: 'AdminSponsors',
  setup() {
    const store = useStore();
    const toast = useToast();
    
    const sponsors = ref([]);
    const loading = ref(true);
    const isProcessing = ref(false);
    const activeTab = ref('pending');
    
    // Modal state
    const showModal = ref(false);
    const selectedSponsor = ref(null);
    
    // Fetch sponsors on component mount
    onMounted(async () => {
      try {
        const response = await store.dispatch('admin/fetchSponsors');
        sponsors.value = response;
        loading.value = false;
      } catch (error) {
        toast.error('Failed to load sponsors');
        console.error('Error loading sponsors:', error);
        loading.value = false;
      }
    });
    
    // Filter sponsors based on active tab
    const filteredSponsors = computed(() => {
      return sponsors.value.filter(sponsor => sponsor.status === activeTab.value);
    });
    
    // Actions
    const approveSponsor = async (sponsorId) => {
      isProcessing.value = true;
      try {
        await store.dispatch('admin/approveSponsor', sponsorId);
        // Update local state
        const sponsorIndex = sponsors.value.findIndex(s => s.id === sponsorId);
        if (sponsorIndex !== -1) {
          sponsors.value[sponsorIndex].status = 'approved';
          sponsors.value[sponsorIndex].approvedAt = new Date().toISOString();
        }
        toast.success('Sponsor approved successfully');
      } catch (error) {
        toast.error('Failed to approve sponsor');
        console.error('Error approving sponsor:', error);
      } finally {
        isProcessing.value = false;
      }
    };
    
    const rejectSponsor = async (sponsorId) => {
      isProcessing.value = true;
      try {
        await store.dispatch('admin/rejectSponsor', sponsorId);
        // Update local state
        const sponsorIndex = sponsors.value.findIndex(s => s.id === sponsorId);
        if (sponsorIndex !== -1) {
          sponsors.value[sponsorIndex].status = 'rejected';
          sponsors.value[sponsorIndex].rejectedAt = new Date().toISOString();
        }
        toast.success('Sponsor rejected successfully');
      } catch (error) {
        toast.error('Failed to reject sponsor');
        console.error('Error rejecting sponsor:', error);
      } finally {
        isProcessing.value = false;
      }
    };
    
    const reconsiderSponsor = async (sponsorId) => {
      isProcessing.value = true;
      try {
        await store.dispatch('admin/reconsiderSponsor', sponsorId);
        // Update local state
        const sponsorIndex = sponsors.value.findIndex(s => s.id === sponsorId);
        if (sponsorIndex !== -1) {
          sponsors.value[sponsorIndex].status = 'pending';
        }
        toast.success('Sponsor moved back to pending for reconsideration');
      } catch (error) {
        toast.error('Failed to reconsider sponsor');
        console.error('Error reconsidering sponsor:', error);
      } finally {
        isProcessing.value = false;
      }
    };
    
    const viewDetails = (sponsorId) => {
      selectedSponsor.value = sponsors.value.find(s => s.id === sponsorId);
      showModal.value = true;
    };
    
    const closeModal = () => {
      showModal.value = false;
      selectedSponsor.value = null;
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
    
    const formatWebsite = (website) => {
      if (!website) return '#';
      if (website.startsWith('http://') || website.startsWith('https://')) {
        return website;
      }
      return `https://${website}`;
    };
    
    return {
      sponsors,
      filteredSponsors,
      loading,
      isProcessing,
      activeTab,
      showModal,
      selectedSponsor,
      approveSponsor,
      rejectSponsor,
      reconsiderSponsor,
      viewDetails,
      closeModal,
      formatDate,
      capitalizeFirst,
      formatWebsite
    };
  }
};
</script>

<style scoped>
.admin-sponsors {
  @apply py-6 px-4 max-w-7xl mx-auto;
}
</style> 