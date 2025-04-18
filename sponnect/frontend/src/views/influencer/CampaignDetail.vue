<template>
  <div class="campaign-detail-container">
    <!-- Back button -->
    <div class="mb-6">
      <router-link 
        to="/influencer/campaigns" 
        class="flex items-center text-blue-600 hover:text-blue-800"
      >
        <i class="fas fa-arrow-left mr-2"></i> Back to Campaigns
      </router-link>
    </div>
    
    <!-- Loading state -->
    <div v-if="loading" class="text-center py-12">
      <div class="spinner-border text-primary" role="status">
        <span class="sr-only">Loading...</span>
      </div>
      <p class="mt-4 text-gray-600">Loading campaign details...</p>
    </div>
    
    <!-- Error state -->
    <div v-else-if="error" class="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
      <div class="flex">
        <div class="flex-shrink-0">
          <i class="fas fa-exclamation-circle text-red-400"></i>
        </div>
        <div class="ml-3">
          <p class="text-sm text-red-700">
            {{ error }}
          </p>
          <button 
            @click="fetchCampaign" 
            class="mt-2 text-sm text-red-700 underline"
          >
            Try again
          </button>
        </div>
      </div>
    </div>
    
    <!-- Campaign content -->
    <div v-else-if="campaign" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Left column - Campaign info -->
      <div class="lg:col-span-2">
        <!-- Campaign header -->
        <div class="bg-white rounded-lg shadow overflow-hidden mb-6">
          <div class="relative h-48 md:h-64">
            <img 
              :src="campaign.coverImage || '/images/default-campaign-cover.jpg'" 
              :alt="campaign.title" 
              class="w-full h-full object-cover"
            />
            <div class="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent"></div>
            <div class="absolute bottom-0 left-0 p-6 text-white">
              <h1 class="text-2xl md:text-3xl font-bold mb-2">{{ campaign.title }}</h1>
              <div class="flex items-center">
                <img 
                  :src="campaign.sponsorLogo || '/images/default-logo.png'" 
                  :alt="campaign.sponsorName" 
                  class="w-8 h-8 rounded-full object-cover mr-2"
                />
                <span>{{ campaign.sponsorName }}</span>
              </div>
            </div>
          </div>
          
          <!-- Campaign stats -->
          <div class="p-6 grid grid-cols-2 md:grid-cols-4 gap-4 border-b">
            <div>
              <div class="text-sm text-gray-500">Budget</div>
              <div class="font-bold text-xl text-blue-600">${{ campaign.budget }}</div>
            </div>
            
            <div>
              <div class="text-sm text-gray-500">Category</div>
              <div class="font-medium">{{ campaign.category }}</div>
            </div>
            
            <div>
              <div class="text-sm text-gray-500">Platform</div>
              <div class="font-medium">{{ campaign.platform || 'Any Platform' }}</div>
            </div>
            
            <div>
              <div class="text-sm text-gray-500">Created</div>
              <div class="font-medium">{{ formatDate(campaign.createdAt) }}</div>
            </div>
          </div>
          
          <!-- Description -->
          <div class="p-6">
            <h2 class="text-xl font-bold mb-4">Campaign Description</h2>
            <div class="prose max-w-none">
              {{ campaign.description }}
            </div>
          </div>
        </div>
        
        <!-- Requirements -->
        <div class="bg-white rounded-lg shadow p-6 mb-6">
          <h2 class="text-xl font-bold mb-4">Requirements</h2>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="border border-gray-200 rounded-lg p-4">
              <h3 class="font-medium mb-2 flex items-center">
                <i class="fas fa-bullseye mr-2 text-blue-500"></i>
                Campaign Goals
              </h3>
              <p class="text-gray-700">{{ campaign.goals || 'No specific goals provided.' }}</p>
            </div>
            
            <div class="border border-gray-200 rounded-lg p-4">
              <h3 class="font-medium mb-2 flex items-center">
                <i class="fas fa-users mr-2 text-blue-500"></i>
                Target Audience
              </h3>
              <p class="text-gray-700">{{ campaign.targetAudience || 'No specific target audience provided.' }}</p>
            </div>
            
            <div class="border border-gray-200 rounded-lg p-4">
              <h3 class="font-medium mb-2 flex items-center">
                <i class="fas fa-calendar-alt mr-2 text-blue-500"></i>
                Timeline
              </h3>
              <p class="text-gray-700">
                {{ campaign.timeline || 'No specific timeline provided.' }}
              </p>
            </div>
            
            <div class="border border-gray-200 rounded-lg p-4">
              <h3 class="font-medium mb-2 flex items-center">
                <i class="fas fa-list-ul mr-2 text-blue-500"></i>
                Deliverables
              </h3>
              <p class="text-gray-700">
                {{ campaign.deliverables || 'No specific deliverables provided.' }}
              </p>
            </div>
          </div>
        </div>
        
        <!-- Creative Guidelines -->
        <div class="bg-white rounded-lg shadow p-6 mb-6">
          <h2 class="text-xl font-bold mb-4">Creative Guidelines</h2>
          <div class="prose max-w-none text-gray-700">
            {{ campaign.guidelines || 'No specific creative guidelines provided.' }}
          </div>
        </div>
      </div>
      
      <!-- Right column - Apply/Sidebar -->
      <div>
        <!-- Apply card -->
        <div class="bg-white rounded-lg shadow p-6 mb-6 sticky top-4">
          <h2 class="text-xl font-bold mb-4">Apply for This Campaign</h2>
          
          <div v-if="isLoggedIn && user.role === 'INFLUENCER'">
            <div v-if="hasExistingRequest" class="mb-6 bg-blue-50 p-4 rounded-lg">
              <p class="text-sm text-blue-700">
                You have already submitted a request for this campaign. 
                <router-link 
                  :to="`/influencer/ad-requests/${existingRequestId}`"
                  class="font-medium underline"
                >
                  View your request
                </router-link>
              </p>
            </div>
            
            <form @submit.prevent="submitAdRequest" v-else>
              <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Your Proposal <span class="text-red-500">*</span>
                </label>
                <textarea
                  v-model="adRequest.proposal"
                  rows="5"
                  class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Describe how you would promote this product and why you're a good fit for this campaign..."
                  required
                ></textarea>
                <p class="mt-1 text-sm text-gray-500">
                  Be specific about your content ideas and why your audience would be interested.
                </p>
              </div>
              
              <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Suggested Price <span class="text-red-500">*</span>
                </label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <span class="text-gray-500">$</span>
                  </div>
                  <input
                    v-model.number="adRequest.price"
                    type="number"
                    min="1"
                    step="0.01"
                    class="w-full pl-7 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter your price"
                    required
                  />
                </div>
                <p class="mt-1 text-sm text-gray-500">
                  Suggested budget for this campaign is ${{ campaign.budget }}.
                </p>
              </div>
              
              <div class="mb-6">
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Expected Delivery Date <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="adRequest.deliveryDate"
                  type="date"
                  class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  :min="minDeliveryDate"
                  required
                />
              </div>
              
              <button
                type="submit"
                class="w-full py-3 px-4 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                :disabled="submitting"
              >
                <span v-if="submitting">
                  <i class="fas fa-spinner fa-spin mr-2"></i> Submitting...
                </span>
                <span v-else>
                  Submit Application
                </span>
              </button>
            </form>
          </div>
          
          <div v-else-if="!isLoggedIn" class="text-center">
            <p class="mb-4 text-gray-700">You need to be logged in to apply for this campaign.</p>
            <router-link 
              to="/login?redirect=influencer/campaigns"
              class="block w-full py-3 px-4 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700"
            >
              Log In to Apply
            </router-link>
          </div>
          
          <div v-else class="text-center">
            <p class="mb-4 text-gray-700">Only influencer accounts can apply for campaigns.</p>
          </div>
        </div>
        
        <!-- About the sponsor -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-xl font-bold mb-4">About the Sponsor</h2>
          
          <div class="flex items-center mb-4">
            <img 
              :src="campaign.sponsorLogo || '/images/default-logo.png'" 
              :alt="campaign.sponsorName" 
              class="w-16 h-16 rounded-full object-cover mr-3"
            />
            <div>
              <h3 class="font-bold">{{ campaign.sponsorName }}</h3>
              <p class="text-sm text-gray-500">Joined {{ formatDate(campaign.sponsorJoinDate) }}</p>
            </div>
          </div>
          
          <p class="text-gray-700 mb-4">
            {{ campaign.sponsorDescription || 'No sponsor description available.' }}
          </p>
          
          <div v-if="sponsorStats" class="grid grid-cols-2 gap-4 text-center mb-4 p-3 bg-gray-50 rounded-lg">
            <div>
              <div class="text-sm text-gray-500">Active Campaigns</div>
              <div class="font-bold text-lg">{{ sponsorStats.activeCampaigns }}</div>
            </div>
            <div>
              <div class="text-sm text-gray-500">Completed Projects</div>
              <div class="font-bold text-lg">{{ sponsorStats.completedProjects }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Success Modal -->
  <div 
    v-if="showSuccessModal" 
    class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
  >
    <div class="bg-white rounded-lg shadow-xl w-full max-w-md">
      <div class="p-6 text-center">
        <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <i class="fas fa-check text-2xl text-green-600"></i>
        </div>
        <h3 class="text-xl font-bold mb-2">Application Submitted!</h3>
        <p class="text-gray-600 mb-6">
          Your application for this campaign has been successfully submitted.
          The sponsor will review your proposal and get back to you soon.
        </p>
        <div class="flex flex-col space-y-2">
          <router-link 
            :to="`/influencer/ad-requests/${submittedRequestId}`"
            class="w-full py-2 px-4 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700"
          >
            View Your Request
          </router-link>
          <button 
            @click="showSuccessModal = false"
            class="w-full py-2 px-4 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useStore } from 'vuex';

export default {
  name: 'InfluencerCampaignDetail',
  setup() {
    const store = useStore();
    const route = useRoute();
    const router = useRouter();
    
    // Campaign ID from route
    const campaignId = route.params.id;
    
    // State
    const campaign = ref(null);
    const loading = ref(true);
    const error = ref(null);
    const submitting = ref(false);
    const showSuccessModal = ref(false);
    const submittedRequestId = ref(null);
    const sponsorStats = ref(null);
    const hasExistingRequest = ref(false);
    const existingRequestId = ref(null);
    
    // Ad Request Form
    const adRequest = reactive({
      proposal: '',
      price: '',
      deliveryDate: '',
    });
    
    // Computed
    const isLoggedIn = computed(() => store.getters['auth/isAuthenticated']);
    const user = computed(() => store.getters['auth/user']);
    
    const minDeliveryDate = computed(() => {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      return tomorrow.toISOString().split('T')[0];
    });
    
    // Methods
    const fetchCampaign = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        // Get campaign details
        const response = await store.dispatch('campaigns/fetchCampaignById', campaignId);
        campaign.value = response;
        
        // Pre-fill price if budget exists
        if (campaign.value && campaign.value.budget) {
          adRequest.price = campaign.value.budget;
        }
        
        // Get sponsor stats
        if (campaign.value && campaign.value.sponsorId) {
          sponsorStats.value = await store.dispatch('sponsors/fetchSponsorStats', campaign.value.sponsorId);
        }
        
        // Check if user has an existing request for this campaign
        if (isLoggedIn.value && user.value.role === 'INFLUENCER') {
          const requests = await store.dispatch('adRequests/fetchMyAdRequests');
          const existingRequest = requests.find(req => req.campaignId === campaignId);
          
          if (existingRequest) {
            hasExistingRequest.value = true;
            existingRequestId.value = existingRequest.id;
          }
        }
      } catch (err) {
        console.error('Error fetching campaign:', err);
        error.value = 'Failed to load campaign details. Please try again later.';
      } finally {
        loading.value = false;
      }
    };
    
    const submitAdRequest = async () => {
      submitting.value = true;
      
      try {
        const requestData = {
          campaignId,
          proposal: adRequest.proposal,
          price: adRequest.price,
          deliveryDate: adRequest.deliveryDate,
        };
        
        const response = await store.dispatch('adRequests/createAdRequest', requestData);
        submittedRequestId.value = response.id;
        showSuccessModal.value = true;
        
        // Reset form
        adRequest.proposal = '';
        adRequest.price = '';
        adRequest.deliveryDate = '';
      } catch (err) {
        console.error('Error submitting ad request:', err);
        error.value = 'Failed to submit your application. Please try again later.';
      } finally {
        submitting.value = false;
      }
    };
    
    const formatDate = (dateString) => {
      if (!dateString) return '';
      
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short', 
        day: 'numeric'
      }).format(date);
    };
    
    // Lifecycle hooks
    onMounted(() => {
      fetchCampaign();
    });
    
    return {
      campaign,
      loading,
      error,
      adRequest,
      isLoggedIn,
      user,
      submitting,
      minDeliveryDate,
      showSuccessModal,
      submittedRequestId,
      sponsorStats,
      hasExistingRequest,
      existingRequestId,
      fetchCampaign,
      submitAdRequest,
      formatDate
    };
  }
};
</script>

<style scoped>
.campaign-detail-container {
  @apply py-6 px-4 max-w-7xl mx-auto;
}

.prose {
  @apply text-gray-700 leading-relaxed;
}

.prose p {
  @apply mb-4;
}

.prose ul {
  @apply list-disc pl-5 mb-4;
}

.prose ol {
  @apply list-decimal pl-5 mb-4;
}

.sticky {
  @apply top-4;
}
</style> 