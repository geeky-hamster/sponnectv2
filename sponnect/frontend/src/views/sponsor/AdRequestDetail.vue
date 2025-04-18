<template>
  <div class="request-detail">
    <div class="flex items-center mb-6">
      <router-link 
        to="/sponsor/requests" 
        class="text-gray-600 hover:text-gray-800 mr-4"
      >
        <i class="fas fa-arrow-left"></i> Back to Requests
      </router-link>
      <h1 class="text-3xl font-bold">Ad Request Details</h1>
    </div>
    
    <div v-if="loading" class="text-center py-12">
      <div class="spinner-border text-primary" role="status">
        <span class="sr-only">Loading...</span>
      </div>
    </div>
    
    <div v-else-if="!request" class="bg-white rounded-lg shadow p-6 text-center">
      <h3 class="text-xl font-semibold text-gray-600 mb-2">Request Not Found</h3>
      <p class="text-gray-500 mb-4">The ad request you're looking for doesn't exist or you don't have permission to view it.</p>
      <router-link 
        to="/sponsor/requests" 
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
      >
        Return to Requests
      </router-link>
    </div>
    
    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Request Details -->
      <div class="lg:col-span-2">
        <div class="bg-white rounded-lg shadow">
          <!-- Request Header -->
          <div class="p-6 border-b">
            <div class="flex justify-between items-start">
              <div>
                <h2 class="text-2xl font-semibold mb-1">{{ request.campaign.title }}</h2>
                <p class="text-gray-600">
                  Ad Type: <span class="font-medium">{{ request.adType }}</span>
                </p>
              </div>
              <span :class="[
                'px-3 py-1 text-sm font-semibold rounded-full',
                request.status === 'Accepted' ? 'bg-green-100 text-green-800' : 
                request.status === 'Rejected' ? 'bg-red-100 text-red-800' : 
                request.status === 'Completed' ? 'bg-blue-100 text-blue-800' : 
                request.status === 'Negotiating' ? 'bg-yellow-100 text-yellow-800' : 
                'bg-gray-100 text-gray-800'
              ]">
                {{ request.status }}
              </span>
            </div>
          </div>
          
          <!-- Request Timeline -->
          <div class="p-6 border-b">
            <h3 class="text-lg font-semibold mb-4">Request Timeline</h3>
            <div class="space-y-4">
              <div class="flex">
                <div class="flex-shrink-0 w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                  <i class="fas fa-file-alt text-blue-600"></i>
                </div>
                <div class="ml-4">
                  <div class="text-sm font-medium text-gray-900">Request Created</div>
                  <div class="text-sm text-gray-500">{{ formatDate(request.createdAt) }}</div>
                </div>
              </div>
              
              <template v-if="request.status === 'Accepted' || request.status === 'Completed'">
                <div class="flex">
                  <div class="flex-shrink-0 w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                    <i class="fas fa-check text-green-600"></i>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">Request Accepted</div>
                    <div class="text-sm text-gray-500">{{ formatDate(request.acceptedAt) }}</div>
                  </div>
                </div>
              </template>
              
              <template v-if="request.status === 'Rejected'">
                <div class="flex">
                  <div class="flex-shrink-0 w-10 h-10 rounded-full bg-red-100 flex items-center justify-center">
                    <i class="fas fa-times text-red-600"></i>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">Request Rejected</div>
                    <div class="text-sm text-gray-500">{{ formatDate(request.rejectedAt) }}</div>
                  </div>
                </div>
              </template>
              
              <template v-if="request.status === 'Completed'">
                <div class="flex">
                  <div class="flex-shrink-0 w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                    <i class="fas fa-flag-checkered text-blue-600"></i>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">Request Completed</div>
                    <div class="text-sm text-gray-500">{{ formatDate(request.completedAt) }}</div>
                  </div>
                </div>
              </template>
            </div>
          </div>
          
          <!-- Request Details -->
          <div class="p-6 border-b">
            <h3 class="text-lg font-semibold mb-4">Request Details</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <p class="text-sm text-gray-500 mb-1">Campaign</p>
                <p class="font-medium">{{ request.campaign.title }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500 mb-1">Campaign Category</p>
                <p class="font-medium">{{ request.campaign.category }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500 mb-1">Requested Price</p>
                <p class="font-medium">${{ request.price }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500 mb-1">Ad Type</p>
                <p class="font-medium">{{ request.adType }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500 mb-1">Delivery Timeline</p>
                <p class="font-medium">{{ request.deliveryTimeline || 'Not specified' }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500 mb-1">Requested At</p>
                <p class="font-medium">{{ formatDate(request.createdAt) }}</p>
              </div>
            </div>
            
            <div class="mt-6">
              <p class="text-sm text-gray-500 mb-1">Proposal</p>
              <p class="whitespace-pre-line">{{ request.proposal || 'No proposal provided.' }}</p>
            </div>
          </div>
          
          <!-- Negotiation History -->
          <div v-if="negotiationHistory.length > 0" class="p-6 border-b">
            <h3 class="text-lg font-semibold mb-4">Negotiation History</h3>
            <div class="space-y-4">
              <div v-for="(item, index) in negotiationHistory" :key="index" class="bg-gray-50 p-4 rounded-lg">
                <div class="flex justify-between items-start mb-2">
                  <span class="text-sm font-semibold">
                    {{ item.sender === 'sponsor' ? 'You' : request.influencer.fullName }}
                  </span>
                  <span class="text-xs text-gray-500">{{ formatDate(item.timestamp) }}</span>
                </div>
                <p class="text-sm mb-2">
                  <span v-if="item.priceChange" class="block mb-1">
                    Price: <span :class="item.priceChange > 0 ? 'text-green-600' : 'text-red-600'">
                      ${{ item.price }} ({{ item.priceChange > 0 ? '+' : '' }}{{ item.priceChange }}%)
                    </span>
                  </span>
                  <span v-else class="block mb-1">
                    Price: ${{ item.price }}
                  </span>
                </p>
                <p class="text-sm whitespace-pre-line">{{ item.message }}</p>
              </div>
            </div>
          </div>
          
          <!-- Complete Your Part (When Accepted) -->
          <div v-if="request.status === 'Accepted'" class="p-6 border-b bg-green-50">
            <h3 class="text-lg font-semibold mb-4">Complete Ad Request</h3>
            <p class="text-gray-700 mb-4">
              The influencer has fulfilled their part of the agreement?
              Confirm payment and complete this ad request.
            </p>
            <button 
              @click="showCompleteModal = true"
              class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              :disabled="isProcessing"
            >
              Mark as Completed
            </button>
          </div>
          
          <!-- View Proof (When Completed) -->
          <div v-if="request.status === 'Completed'" class="p-6 border-b bg-blue-50">
            <h3 class="text-lg font-semibold mb-4">Completion Details</h3>
            <div class="mb-4">
              <p class="text-sm text-gray-500 mb-1">Completed At</p>
              <p class="font-medium">{{ formatDate(request.completedAt) }}</p>
            </div>
            <div class="mb-4">
              <p class="text-sm text-gray-500 mb-1">Completion Notes</p>
              <p class="whitespace-pre-line">{{ request.completionDetails || 'No completion notes provided.' }}</p>
            </div>
            
            <template v-if="request.proofUrls && request.proofUrls.length">
              <p class="text-sm text-gray-500 mb-2">Proof of Completion</p>
              <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
                <div v-for="(url, index) in request.proofUrls" :key="index" class="relative">
                  <img 
                    :src="url" 
                    :alt="`Proof ${index+1}`" 
                    class="w-full h-32 object-cover rounded cursor-pointer"
                    @click="openLightbox(url)"
                  />
                </div>
              </div>
            </template>
            
            <div v-if="request.proofLink" class="mt-4">
              <a 
                :href="request.proofLink" 
                target="_blank" 
                class="text-blue-600 hover:underline"
              >
                View External Proof
              </a>
            </div>
          </div>
          
          <!-- Actions -->
          <div v-if="request.status === 'Pending'" class="p-6 flex flex-wrap gap-3">
            <button
              @click="showAcceptModal = true"
              class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              :disabled="isProcessing"
            >
              Accept Request
            </button>
            <button
              @click="showNegotiateModal = true"
              class="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
              :disabled="isProcessing"
            >
              Negotiate
            </button>
            <button
              @click="showRejectModal = true"
              class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              :disabled="isProcessing"
            >
              Reject Request
            </button>
          </div>
          
          <div v-if="request.status === 'Negotiating'" class="p-6 border-t">
            <form @submit.prevent="submitCounter">
              <h3 class="text-lg font-semibold mb-4">Make a Counter Offer</h3>
              <div class="mb-4">
                <label class="block text-gray-700 text-sm font-bold mb-2" for="counterPrice">
                  Your Offer (USD)
                </label>
                <input 
                  id="counterPrice"
                  v-model.number="counterForm.price"
                  type="number"
                  min="0"
                  step="0.01"
                  class="w-full p-2 border rounded"
                  :class="{ 'border-red-500': counterFormErrors.price }"
                  required
                />
                <p v-if="counterFormErrors.price" class="text-red-500 text-xs mt-1">{{ counterFormErrors.price }}</p>
              </div>
              
              <div class="mb-4">
                <label class="block text-gray-700 text-sm font-bold mb-2" for="counterMessage">
                  Message
                </label>
                <textarea 
                  id="counterMessage"
                  v-model="counterForm.message"
                  class="w-full p-2 border rounded"
                  :class="{ 'border-red-500': counterFormErrors.message }"
                  rows="4"
                  placeholder="Explain your counter offer"
                  required
                ></textarea>
                <p v-if="counterFormErrors.message" class="text-red-500 text-xs mt-1">{{ counterFormErrors.message }}</p>
              </div>
              
              <div class="flex justify-end space-x-3">
                <button 
                  type="button" 
                  @click="showAcceptModal = true"
                  class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                  :disabled="isNegotiating"
                >
                  Accept Last Offer
                </button>
                <button 
                  type="submit" 
                  class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  :disabled="isNegotiating"
                >
                  {{ isNegotiating ? 'Sending...' : 'Send Counter Offer' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
      
      <!-- Influencer Info -->
      <div class="lg:col-span-1">
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-lg font-semibold mb-4">Influencer Information</h3>
          <div class="flex items-center mb-4">
            <div class="flex-shrink-0 h-16 w-16">
              <img 
                :src="request.influencer.profileImage || '/images/default-avatar.png'" 
                class="h-16 w-16 rounded-full object-cover"
                alt="Influencer avatar"
              >
            </div>
            <div class="ml-4">
              <div class="text-lg font-medium text-gray-900">{{ request.influencer.fullName }}</div>
              <div class="text-gray-500">@{{ request.influencer.username }}</div>
            </div>
          </div>
          
          <div class="space-y-3">
            <div>
              <p class="text-sm text-gray-500 mb-1">Followers</p>
              <p class="font-medium">{{ formatNumber(request.influencer.followers || 0) }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500 mb-1">Main Platform</p>
              <p class="font-medium">{{ request.influencer.mainPlatform || 'Not specified' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500 mb-1">Niche</p>
              <p class="font-medium">{{ request.influencer.niche || 'Not specified' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500 mb-1">Location</p>
              <p class="font-medium">{{ request.influencer.location || 'Not specified' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500 mb-1">Member Since</p>
              <p class="font-medium">{{ formatDate(request.influencer.createdAt) }}</p>
            </div>
          </div>
          
          <div class="mt-6 pt-6 border-t">
            <h4 class="font-medium mb-3">Completed Collaborations</h4>
            <p class="text-gray-600">{{ request.influencer.completedCollaborations || 0 }} successful collaborations</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Accept Modal -->
    <div 
      v-if="showAcceptModal" 
      class="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50"
      @click.self="showAcceptModal = false"
    >
      <div class="bg-white rounded-lg w-full max-w-md p-6">
        <h3 class="text-lg font-bold mb-4">Accept Ad Request</h3>
        <p class="mb-6">
          Are you sure you want to accept this ad request? You will be agreeing to a price of ${{ request.price }}.
        </p>
        <div class="flex justify-end space-x-4">
          <button 
            @click="showAcceptModal = false" 
            class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100"
            :disabled="isProcessing"
          >
            Cancel
          </button>
          <button 
            @click="acceptRequest" 
            class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            :disabled="isProcessing"
          >
            {{ isProcessing ? 'Processing...' : 'Accept' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- Reject Modal -->
    <div 
      v-if="showRejectModal" 
      class="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50"
      @click.self="showRejectModal = false"
    >
      <div class="bg-white rounded-lg w-full max-w-md p-6">
        <h3 class="text-lg font-bold mb-4">Reject Ad Request</h3>
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2" for="rejectReason">
            Reason for Rejection (Optional)
          </label>
          <textarea 
            id="rejectReason"
            v-model="rejectReason"
            class="w-full p-2 border rounded"
            rows="3"
            placeholder="Provide feedback to the influencer"
          ></textarea>
        </div>
        <div class="flex justify-end space-x-4">
          <button 
            @click="showRejectModal = false" 
            class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100"
            :disabled="isProcessing"
          >
            Cancel
          </button>
          <button 
            @click="rejectRequest" 
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            :disabled="isProcessing"
          >
            {{ isProcessing ? 'Processing...' : 'Reject' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- Negotiate Modal -->
    <div 
      v-if="showNegotiateModal" 
      class="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50"
      @click.self="showNegotiateModal = false"
    >
      <div class="bg-white rounded-lg w-full max-w-md p-6">
        <h3 class="text-lg font-bold mb-4">Negotiate Ad Request</h3>
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2" for="negotiatePrice">
            Your Counter Offer (USD)
          </label>
          <input 
            id="negotiatePrice"
            v-model.number="negotiateForm.price"
            type="number"
            min="0"
            step="0.01"
            class="w-full p-2 border rounded"
            :class="{ 'border-red-500': negotiateFormErrors.price }"
            required
          />
          <p v-if="negotiateFormErrors.price" class="text-red-500 text-xs mt-1">{{ negotiateFormErrors.price }}</p>
        </div>
        
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2" for="negotiateMessage">
            Message
          </label>
          <textarea 
            id="negotiateMessage"
            v-model="negotiateForm.message"
            class="w-full p-2 border rounded"
            :class="{ 'border-red-500': negotiateFormErrors.message }"
            rows="3"
            placeholder="Explain your counter offer"
            required
          ></textarea>
          <p v-if="negotiateFormErrors.message" class="text-red-500 text-xs mt-1">{{ negotiateFormErrors.message }}</p>
        </div>
        
        <div class="flex justify-end space-x-4">
          <button 
            @click="showNegotiateModal = false" 
            class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100"
            :disabled="isProcessing"
          >
            Cancel
          </button>
          <button 
            @click="negotiateRequest" 
            class="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
            :disabled="isProcessing"
          >
            {{ isProcessing ? 'Processing...' : 'Send Counter Offer' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- Complete Modal -->
    <div 
      v-if="showCompleteModal" 
      class="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50"
      @click.self="showCompleteModal = false"
    >
      <div class="bg-white rounded-lg w-full max-w-md p-6">
        <h3 class="text-lg font-bold mb-4">Mark Ad Request as Completed</h3>
        <p class="mb-6">
          Are you sure you want to mark this ad request as completed? This will finalize the collaboration.
        </p>
        <div class="flex justify-end space-x-4">
          <button 
            @click="showCompleteModal = false" 
            class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100"
            :disabled="isProcessing"
          >
            Cancel
          </button>
          <button 
            @click="completeRequest" 
            class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            :disabled="isProcessing"
          >
            {{ isProcessing ? 'Processing...' : 'Mark as Completed' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRouter, useRoute } from 'vue-router';
import { useToast } from 'vue-toastification';

export default {
  name: 'SponsorAdRequestDetail',
  setup() {
    const store = useStore();
    const router = useRouter();
    const route = useRoute();
    const toast = useToast();
    
    const loading = ref(true);
    const request = ref(null);
    const negotiationHistory = ref([]);
    
    // Form states
    const isProcessing = ref(false);
    const isNegotiating = ref(false);
    
    // Modal states
    const showAcceptModal = ref(false);
    const showRejectModal = ref(false);
    const showNegotiateModal = ref(false);
    const showCompleteModal = ref(false);
    
    // Form data
    const rejectReason = ref('');
    
    const negotiateForm = ref({
      price: 0,
      message: ''
    });
    
    const negotiateFormErrors = ref({});
    
    const counterForm = ref({
      price: 0,
      message: ''
    });
    
    const counterFormErrors = ref({});
    
    // Fetch request data on mount
    onMounted(async () => {
      try {
        const requestId = route.params.id;
        
        // Fetch ad request details
        const response = await store.dispatch('adRequests/fetchSponsorRequestDetail', requestId);
        
        if (response) {
          request.value = response;
          
          // Pre-fill counter offer form with the current price
          negotiateForm.value.price = response.price;
          counterForm.value.price = response.price;
          
          // Fetch negotiation history if applicable
          if (response.status === 'Negotiating' || response.status === 'Accepted' || response.status === 'Completed') {
            const historyResponse = await store.dispatch('adRequests/fetchNegotiationHistory', requestId);
            negotiationHistory.value = historyResponse.history || [];
          }
        }
      } catch (error) {
        toast.error('Failed to load request details');
        console.error('Error loading request details:', error);
      } finally {
        loading.value = false;
      }
    });
    
    // Methods
    const validateNegotiateForm = () => {
      const errors = {};
      
      if (!negotiateForm.value.price) {
        errors.price = 'Price is required';
      } else if (negotiateForm.value.price <= 0) {
        errors.price = 'Price must be greater than 0';
      }
      
      if (!negotiateForm.value.message || negotiateForm.value.message.trim() === '') {
        errors.message = 'Message is required';
      }
      
      negotiateFormErrors.value = errors;
      return Object.keys(errors).length === 0;
    };
    
    const validateCounterForm = () => {
      const errors = {};
      
      if (!counterForm.value.price) {
        errors.price = 'Price is required';
      } else if (counterForm.value.price <= 0) {
        errors.price = 'Price must be greater than 0';
      }
      
      if (!counterForm.value.message || counterForm.value.message.trim() === '') {
        errors.message = 'Message is required';
      }
      
      counterFormErrors.value = errors;
      return Object.keys(errors).length === 0;
    };
    
    const acceptRequest = async () => {
      isProcessing.value = true;
      try {
        await store.dispatch('adRequests/sponsorActionRequest', {
          requestId: request.value.id,
          action: 'accept',
          data: {}
        });
        
        toast.success('Ad request accepted!');
        router.push('/sponsor/requests');
      } catch (error) {
        toast.error(error.response?.data?.message || 'Failed to accept request');
        console.error('Error accepting request:', error);
      } finally {
        isProcessing.value = false;
        showAcceptModal.value = false;
      }
    };
    
    const rejectRequest = async () => {
      isProcessing.value = true;
      try {
        await store.dispatch('adRequests/sponsorActionRequest', {
          requestId: request.value.id,
          action: 'reject',
          data: { reason: rejectReason.value }
        });
        
        toast.success('Ad request rejected');
        router.push('/sponsor/requests');
      } catch (error) {
        toast.error(error.response?.data?.message || 'Failed to reject request');
        console.error('Error rejecting request:', error);
      } finally {
        isProcessing.value = false;
        showRejectModal.value = false;
      }
    };
    
    const negotiateRequest = async () => {
      if (!validateNegotiateForm()) {
        return;
      }
      
      isProcessing.value = true;
      try {
        await store.dispatch('adRequests/sponsorActionRequest', {
          requestId: request.value.id,
          action: 'negotiate',
          data: { 
            price: negotiateForm.value.price,
            message: negotiateForm.value.message
          }
        });
        
        toast.success('Counter offer sent!');
        
        // Refresh the request data
        const updatedRequest = await store.dispatch('adRequests/fetchSponsorRequestDetail', request.value.id);
        request.value = updatedRequest;
        
        // Fetch updated negotiation history
        const historyResponse = await store.dispatch('adRequests/fetchNegotiationHistory', request.value.id);
        negotiationHistory.value = historyResponse.history || [];
        
        // Update counter form with the latest price
        counterForm.value.price = negotiateForm.value.price;
      } catch (error) {
        toast.error(error.response?.data?.message || 'Failed to send counter offer');
        console.error('Error negotiating request:', error);
      } finally {
        isProcessing.value = false;
        showNegotiateModal.value = false;
      }
    };
    
    const submitCounter = async () => {
      if (!validateCounterForm()) {
        return;
      }
      
      isNegotiating.value = true;
      try {
        await store.dispatch('adRequests/sponsorActionRequest', {
          requestId: request.value.id,
          action: 'negotiate',
          data: { 
            price: counterForm.value.price,
            message: counterForm.value.message
          }
        });
        
        toast.success('Counter offer sent!');
        
        // Refresh the request data
        const updatedRequest = await store.dispatch('adRequests/fetchSponsorRequestDetail', request.value.id);
        request.value = updatedRequest;
        
        // Fetch updated negotiation history
        const historyResponse = await store.dispatch('adRequests/fetchNegotiationHistory', request.value.id);
        negotiationHistory.value = historyResponse.history || [];
        
        // Reset form
        counterForm.value.message = '';
      } catch (error) {
        toast.error(error.response?.data?.message || 'Failed to send counter offer');
        console.error('Error negotiating request:', error);
      } finally {
        isNegotiating.value = false;
      }
    };
    
    const completeRequest = async () => {
      isProcessing.value = true;
      try {
        await store.dispatch('adRequests/sponsorActionRequest', {
          requestId: request.value.id,
          action: 'complete',
          data: {}
        });
        
        toast.success('Ad request marked as completed!');
        router.push('/sponsor/requests');
      } catch (error) {
        toast.error(error.response?.data?.message || 'Failed to complete request');
        console.error('Error completing request:', error);
      } finally {
        isProcessing.value = false;
        showCompleteModal.value = false;
      }
    };
    
    const openLightbox = (imageUrl) => {
      // In a real application, implement a full-screen lightbox view
      window.open(imageUrl, '_blank');
    };
    
    // Helper methods
    const formatDate = (dateString) => {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric'
      }).format(date);
    };
    
    const formatNumber = (num) => {
      if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
      } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
      }
      return num;
    };
    
    return {
      loading,
      request,
      negotiationHistory,
      isProcessing,
      isNegotiating,
      showAcceptModal,
      showRejectModal,
      showNegotiateModal,
      showCompleteModal,
      rejectReason,
      negotiateForm,
      negotiateFormErrors,
      counterForm,
      counterFormErrors,
      validateNegotiateForm,
      validateCounterForm,
      acceptRequest,
      rejectRequest,
      negotiateRequest,
      submitCounter,
      completeRequest,
      openLightbox,
      formatDate,
      formatNumber
    };
  }
};
</script>

<style scoped>
.request-detail {
  @apply py-6 px-4 max-w-7xl mx-auto;
}
</style> 