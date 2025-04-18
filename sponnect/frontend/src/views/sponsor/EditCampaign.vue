<template>
  <div class="edit-campaign">
    <div class="flex items-center mb-6">
      <router-link 
        to="/sponsor/campaigns" 
        class="text-gray-600 hover:text-gray-800 mr-4"
      >
        <i class="fas fa-arrow-left"></i> Back to Campaigns
      </router-link>
      <h1 class="text-3xl font-bold">Edit Campaign</h1>
    </div>
    
    <div v-if="loading" class="text-center py-12">
      <div class="spinner-border text-primary" role="status">
        <span class="sr-only">Loading...</span>
      </div>
    </div>
    
    <div v-else-if="!campaign" class="bg-white rounded-lg shadow p-6 text-center">
      <h3 class="text-xl font-semibold text-gray-600 mb-2">Campaign Not Found</h3>
      <p class="text-gray-500 mb-4">The campaign you're trying to edit doesn't exist or you don't have permission to edit it.</p>
      <router-link 
        to="/sponsor/campaigns" 
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
      >
        Return to Campaigns
      </router-link>
    </div>
    
    <div v-else class="bg-white rounded-lg shadow p-6">
      <form @submit.prevent="submitForm">
        <!-- Campaign Status -->
        <div class="mb-6 p-4 bg-gray-50 rounded-lg">
          <div class="flex justify-between items-center">
            <div>
              <h3 class="text-lg font-semibold">Campaign Status</h3>
              <p class="text-gray-600">Current status: 
                <span :class="[
                  'px-2 py-1 ml-2 text-xs font-semibold rounded-full',
                  form.status === 'active' ? 'bg-green-100 text-green-800' : 
                  form.status === 'expired' ? 'bg-gray-100 text-gray-800' : 
                  'bg-yellow-100 text-yellow-800'
                ]">
                  {{ capitalizeFirst(form.status) }}
                </span>
              </p>
            </div>
            
            <div v-if="form.status !== 'expired'">
              <button 
                type="button"
                @click="toggleStatus"
                class="px-4 py-2 border border-gray-300 rounded-lg"
              >
                {{ form.status === 'active' ? 'Pause Campaign' : 'Activate Campaign' }}
              </button>
            </div>
          </div>
        </div>
        
        <!-- Basic Information -->
        <div class="mb-6">
          <h2 class="text-xl font-semibold mb-4">Basic Information</h2>
          
          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2" for="title">
              Campaign Title *
            </label>
            <input 
              id="title"
              v-model="form.title"
              type="text"
              class="w-full p-2 border rounded"
              :class="{ 'border-red-500': errors.title }"
              placeholder="Enter a catchy title for your campaign"
              required
            />
            <p v-if="errors.title" class="text-red-500 text-xs mt-1">{{ errors.title }}</p>
          </div>
          
          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2" for="description">
              Description *
            </label>
            <textarea 
              id="description"
              v-model="form.description"
              class="w-full p-2 border rounded"
              :class="{ 'border-red-500': errors.description }"
              rows="4"
              placeholder="Describe your campaign in detail"
              required
            ></textarea>
            <p v-if="errors.description" class="text-red-500 text-xs mt-1">{{ errors.description }}</p>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2" for="category">
                Category *
              </label>
              <select 
                id="category"
                v-model="form.category"
                class="w-full p-2 border rounded"
                :class="{ 'border-red-500': errors.category }"
                required
              >
                <option value="" disabled>Select a category</option>
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
              <p v-if="errors.category" class="text-red-500 text-xs mt-1">{{ errors.category }}</p>
            </div>
            
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2" for="budget">
                Budget (USD) *
              </label>
              <input 
                id="budget"
                v-model.number="form.budget"
                type="number"
                min="0"
                step="0.01"
                class="w-full p-2 border rounded"
                :class="{ 'border-red-500': errors.budget }"
                placeholder="Total budget for this campaign"
                required
              />
              <p v-if="errors.budget" class="text-red-500 text-xs mt-1">{{ errors.budget }}</p>
            </div>
          </div>
        </div>
        
        <!-- Campaign Details -->
        <div class="mb-6">
          <h2 class="text-xl font-semibold mb-4">Campaign Details</h2>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2" for="startDate">
                Start Date *
              </label>
              <input 
                id="startDate"
                v-model="form.startDate"
                type="date"
                class="w-full p-2 border rounded"
                :class="{ 'border-red-500': errors.startDate }"
                :min="campaign.createdAt.split('T')[0]"
                required
              />
              <p v-if="errors.startDate" class="text-red-500 text-xs mt-1">{{ errors.startDate }}</p>
            </div>
            
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2" for="endDate">
                End Date *
              </label>
              <input 
                id="endDate"
                v-model="form.endDate"
                type="date"
                class="w-full p-2 border rounded"
                :class="{ 'border-red-500': errors.endDate }"
                :min="form.startDate || campaign.createdAt.split('T')[0]"
                required
              />
              <p v-if="errors.endDate" class="text-red-500 text-xs mt-1">{{ errors.endDate }}</p>
            </div>
          </div>
          
          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2" for="requirements">
              Campaign Requirements
            </label>
            <textarea 
              id="requirements"
              v-model="form.requirements"
              class="w-full p-2 border rounded"
              rows="3"
              placeholder="Specific requirements for influencers (optional)"
            ></textarea>
          </div>
          
          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2" for="targetAudience">
              Target Audience
            </label>
            <input 
              id="targetAudience"
              v-model="form.targetAudience"
              type="text"
              class="w-full p-2 border rounded"
              placeholder="Describe your target audience (optional)"
            />
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2" for="platformFocus">
                Platform Focus
              </label>
              <select 
                id="platformFocus"
                v-model="form.platformFocus"
                class="w-full p-2 border rounded"
              >
                <option value="">All Platforms</option>
                <option value="instagram">Instagram</option>
                <option value="tiktok">TikTok</option>
                <option value="youtube">YouTube</option>
                <option value="twitter">Twitter</option>
                <option value="facebook">Facebook</option>
                <option value="blog">Blog</option>
                <option value="twitch">Twitch</option>
              </select>
            </div>
            
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2" for="minFollowers">
                Minimum Followers
              </label>
              <input 
                id="minFollowers"
                v-model.number="form.minFollowers"
                type="number"
                min="0"
                class="w-full p-2 border rounded"
                placeholder="Minimum follower count (optional)"
              />
            </div>
          </div>
        </div>
        
        <!-- Campaign Media -->
        <div class="mb-6">
          <h2 class="text-xl font-semibold mb-4">Campaign Media</h2>
          
          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2" for="imageUrl">
              Cover Image URL
            </label>
            <input 
              id="imageUrl"
              v-model="form.imageUrl"
              type="url"
              class="w-full p-2 border rounded"
              placeholder="URL to your campaign cover image (optional)"
            />
            <p class="text-gray-500 text-xs mt-1">
              Provide a URL to an image that represents your campaign.
            </p>
          </div>
          
          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2" for="additionalUrls">
              Additional Media URLs
            </label>
            <textarea 
              id="additionalUrls"
              v-model="form.additionalUrls"
              class="w-full p-2 border rounded"
              rows="2"
              placeholder="Add URLs to additional media, one per line (optional)"
            ></textarea>
            <p class="text-gray-500 text-xs mt-1">
              Add other media URLs that might help influencers understand your campaign better.
            </p>
          </div>
        </div>
        
        <div class="flex justify-end space-x-4">
          <router-link 
            to="/sponsor/campaigns" 
            class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100"
          >
            Cancel
          </router-link>
          <button 
            type="submit" 
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            :disabled="isSubmitting"
          >
            {{ isSubmitting ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRouter, useRoute } from 'vue-router';
import { useToast } from 'vue-toastification';

export default {
  name: 'SponsorEditCampaign',
  setup() {
    const store = useStore();
    const router = useRouter();
    const route = useRoute();
    const toast = useToast();
    
    const loading = ref(true);
    const isSubmitting = ref(false);
    const errors = ref({});
    const campaign = ref(null);
    
    // Form data
    const form = ref({
      title: '',
      description: '',
      category: '',
      budget: null,
      startDate: '',
      endDate: '',
      requirements: '',
      targetAudience: '',
      platformFocus: '',
      minFollowers: null,
      imageUrl: '',
      additionalUrls: '',
      status: 'draft'
    });
    
    // Fetch campaign data on mount
    onMounted(async () => {
      try {
        const campaignId = route.params.id;
        const response = await store.dispatch('campaigns/fetchCampaign', campaignId);
        
        if (response) {
          campaign.value = response;
          
          // Initialize form with campaign data
          form.value = {
            ...response,
            // Format dates to YYYY-MM-DD for form inputs
            startDate: response.startDate ? response.startDate.split('T')[0] : '',
            endDate: response.endDate ? response.endDate.split('T')[0] : '',
            // Convert array of URLs to newline-separated string
            additionalUrls: response.additionalUrls ? response.additionalUrls.join('\n') : ''
          };
        }
      } catch (error) {
        toast.error('Failed to load campaign details');
        console.error('Error loading campaign:', error);
      } finally {
        loading.value = false;
      }
    });
    
    // Methods
    const validateForm = () => {
      const newErrors = {};
      
      if (!form.value.title || form.value.title.trim() === '') {
        newErrors.title = 'Title is required';
      } else if (form.value.title.length < 5) {
        newErrors.title = 'Title must be at least 5 characters';
      }
      
      if (!form.value.description || form.value.description.trim() === '') {
        newErrors.description = 'Description is required';
      } else if (form.value.description.length < 20) {
        newErrors.description = 'Description must be at least 20 characters';
      }
      
      if (!form.value.category) {
        newErrors.category = 'Category is required';
      }
      
      if (!form.value.budget) {
        newErrors.budget = 'Budget is required';
      } else if (form.value.budget <= 0) {
        newErrors.budget = 'Budget must be greater than 0';
      }
      
      if (!form.value.startDate) {
        newErrors.startDate = 'Start date is required';
      }
      
      if (!form.value.endDate) {
        newErrors.endDate = 'End date is required';
      } else if (form.value.startDate && form.value.endDate < form.value.startDate) {
        newErrors.endDate = 'End date must be after start date';
      }
      
      errors.value = newErrors;
      return Object.keys(newErrors).length === 0;
    };
    
    const toggleStatus = () => {
      form.value.status = form.value.status === 'active' ? 'draft' : 'active';
    };
    
    const submitForm = async () => {
      if (!validateForm()) {
        toast.error('Please fix the errors in the form');
        window.scrollTo(0, 0);
        return;
      }
      
      isSubmitting.value = true;
      
      try {
        // Process additional URLs if provided
        const additionalUrlsArray = form.value.additionalUrls
          ? form.value.additionalUrls.split('\n').filter(url => url.trim() !== '')
          : [];
        
        // Prepare campaign data
        const campaignData = {
          ...form.value,
          additionalUrls: additionalUrlsArray
        };
        
        const response = await store.dispatch('campaigns/updateCampaign', {
          campaignId: campaign.value.id,
          campaignData: campaignData
        });
        
        toast.success('Campaign updated successfully!');
        router.push({ name: 'SponsorCampaigns' });
      } catch (error) {
        toast.error(error.response?.data?.message || 'Failed to update campaign');
        console.error('Campaign update error:', error);
      } finally {
        isSubmitting.value = false;
      }
    };
    
    const capitalizeFirst = (str) => {
      return str.charAt(0).toUpperCase() + str.slice(1);
    };
    
    return {
      loading,
      campaign,
      form,
      errors,
      isSubmitting,
      validateForm,
      toggleStatus,
      submitForm,
      capitalizeFirst
    };
  }
};
</script>

<style scoped>
.edit-campaign {
  @apply py-6 px-4 max-w-5xl mx-auto;
}
</style> 