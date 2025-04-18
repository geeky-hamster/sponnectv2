<template>
  <div class="create-campaign">
    <div class="flex items-center mb-6">
      <router-link 
        to="/sponsor/campaigns" 
        class="text-gray-600 hover:text-gray-800 mr-4"
      >
        <i class="fas fa-arrow-left"></i> Back to Campaigns
      </router-link>
      <h1 class="text-3xl font-bold">Create Campaign</h1>
    </div>
    
    <div class="bg-white rounded-lg shadow p-6">
      <form @submit.prevent="submitForm">
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
                :min="today"
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
                :min="form.startDate || today"
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
            {{ isSubmitting ? 'Creating...' : 'Create Campaign' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';

export default {
  name: 'SponsorCreateCampaign',
  setup() {
    const store = useStore();
    const router = useRouter();
    const toast = useToast();
    
    const isSubmitting = ref(false);
    const errors = ref({});
    
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
    
    // Computed properties
    const today = computed(() => {
      const date = new Date();
      return date.toISOString().split('T')[0];
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
          additionalUrls: additionalUrlsArray,
          // Convert to active if start date is today or earlier
          status: new Date(form.value.startDate) <= new Date() ? 'active' : 'draft'
        };
        
        const response = await store.dispatch('campaigns/createCampaign', campaignData);
        
        toast.success('Campaign created successfully!');
        router.push({ name: 'SponsorCampaigns' });
      } catch (error) {
        toast.error(error.response?.data?.message || 'Failed to create campaign');
        console.error('Campaign creation error:', error);
      } finally {
        isSubmitting.value = false;
      }
    };
    
    return {
      form,
      errors,
      isSubmitting,
      today,
      validateForm,
      submitForm
    };
  }
};
</script>

<style scoped>
.create-campaign {
  @apply py-6 px-4 max-w-5xl mx-auto;
}
</style> 