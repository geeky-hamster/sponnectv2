<template>
  <div class="profile-container">
    <div v-if="loading" class="loading-state">
      <p>Loading profile data...</p>
    </div>
    
    <template v-else>
      <div class="profile-header">
        <h1 class="page-title">My Profile</h1>
        <button @click="editMode = !editMode" class="toggle-edit-btn">
          {{ editMode ? 'Cancel' : 'Edit Profile' }}
        </button>
      </div>
      
      <div class="profile-content">
        <div class="profile-sidebar">
          <div class="profile-avatar-container">
            <img 
              :src="profileData.avatar || '/img/default-avatar.png'" 
              alt="Profile Picture" 
              class="profile-avatar" 
            />
            <div v-if="editMode" class="avatar-overlay">
              <label for="avatar-upload" class="avatar-upload-label">
                <i class="fas fa-camera"></i>
                <span>Change Photo</span>
              </label>
              <input 
                id="avatar-upload" 
                type="file" 
                accept="image/*" 
                @change="handleAvatarChange" 
                class="avatar-upload" 
              />
            </div>
          </div>
          
          <div class="profile-meta">
            <h2 class="profile-name">{{ profileData.name }}</h2>
            <p class="profile-role">{{ userRoleDisplay }}</p>
            <p class="profile-joined">
              <i class="fas fa-calendar"></i> 
              Joined {{ formattedJoinDate }}
            </p>
          </div>
        </div>
        
        <div class="profile-details">
          <form v-if="editMode" @submit.prevent="saveProfile" class="profile-form">
            <div class="form-section">
              <h3 class="section-title">Personal Information</h3>
              
              <div class="form-group">
                <label for="name">Full Name</label>
                <input 
                  id="name" 
                  v-model="form.name" 
                  type="text" 
                  placeholder="Your full name"
                  required
                />
              </div>
              
              <div class="form-group">
                <label for="email">Email Address</label>
                <input 
                  id="email" 
                  v-model="form.email" 
                  type="email" 
                  placeholder="Your email address"
                  required
                  disabled
                />
                <p class="field-hint">Email cannot be changed. Contact support for assistance.</p>
              </div>
              
              <div class="form-group">
                <label for="phone">Phone Number</label>
                <input 
                  id="phone" 
                  v-model="form.phone" 
                  type="tel" 
                  placeholder="Your phone number"
                />
              </div>
              
              <div class="form-group">
                <label for="bio">Bio</label>
                <textarea 
                  id="bio" 
                  v-model="form.bio" 
                  placeholder="Tell us about yourself"
                  rows="4"
                ></textarea>
              </div>
            </div>
            
            <div class="form-section">
              <h3 class="section-title">Location</h3>
              
              <div class="form-row">
                <div class="form-group">
                  <label for="country">Country</label>
                  <input 
                    id="country" 
                    v-model="form.country" 
                    type="text" 
                    placeholder="Your country"
                  />
                </div>
                
                <div class="form-group">
                  <label for="city">City</label>
                  <input 
                    id="city" 
                    v-model="form.city" 
                    type="text" 
                    placeholder="Your city"
                  />
                </div>
              </div>
            </div>
            
            <div v-if="userRole === 'influencer'" class="form-section">
              <h3 class="section-title">Influencer Details</h3>
              
              <div class="form-group">
                <label for="categories">Content Categories</label>
                <div class="categories-selection">
                  <div 
                    v-for="category in availableCategories" 
                    :key="category"
                    class="category-chip"
                    :class="{ active: form.categories.includes(category) }"
                    @click="toggleCategory(category)"
                  >
                    {{ category }}
                  </div>
                </div>
              </div>
              
              <div class="form-section">
                <h4 class="subsection-title">Social Media Accounts</h4>
                
                <div v-for="(platform, index) in form.socialMedia" :key="index" class="social-media-item">
                  <div class="form-row">
                    <div class="form-group platform-select">
                      <label :for="`platform-${index}`">Platform</label>
                      <select :id="`platform-${index}`" v-model="platform.platform">
                        <option value="instagram">Instagram</option>
                        <option value="tiktok">TikTok</option>
                        <option value="youtube">YouTube</option>
                        <option value="twitter">Twitter</option>
                        <option value="facebook">Facebook</option>
                      </select>
                    </div>
                    
                    <div class="form-group handle-input">
                      <label :for="`handle-${index}`">Username/Handle</label>
                      <input 
                        :id="`handle-${index}`" 
                        v-model="platform.handle" 
                        type="text" 
                        placeholder="Your username"
                      />
                    </div>
                    
                    <div class="form-group followers-input">
                      <label :for="`followers-${index}`">Followers</label>
                      <input 
                        :id="`followers-${index}`" 
                        v-model.number="platform.followers" 
                        type="number" 
                        placeholder="Follower count"
                      />
                    </div>
                    
                    <button 
                      type="button" 
                      class="remove-platform-btn" 
                      @click="removePlatform(index)"
                      v-if="form.socialMedia.length > 1"
                    >
                      <i class="fas fa-times"></i>
                    </button>
                  </div>
                </div>
                
                <button 
                  type="button" 
                  class="add-platform-btn" 
                  @click="addPlatform"
                >
                  <i class="fas fa-plus"></i> Add Platform
                </button>
              </div>
            </div>
            
            <div v-else-if="userRole === 'brand'" class="form-section">
              <h3 class="section-title">Brand Details</h3>
              
              <div class="form-group">
                <label for="company">Company Name</label>
                <input 
                  id="company" 
                  v-model="form.company" 
                  type="text" 
                  placeholder="Your company name"
                />
              </div>
              
              <div class="form-group">
                <label for="website">Website</label>
                <input 
                  id="website" 
                  v-model="form.website" 
                  type="url" 
                  placeholder="Your company website"
                />
              </div>
              
              <div class="form-group">
                <label for="industry">Industry</label>
                <select id="industry" v-model="form.industry">
                  <option value="">Select Industry</option>
                  <option value="fashion">Fashion</option>
                  <option value="beauty">Beauty</option>
                  <option value="technology">Technology</option>
                  <option value="food">Food & Beverage</option>
                  <option value="health">Health & Fitness</option>
                  <option value="travel">Travel</option>
                  <option value="entertainment">Entertainment</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>
            
            <div class="form-actions">
              <button type="submit" class="save-btn" :disabled="saving">
                <span v-if="!saving">Save Changes</span>
                <span v-else><i class="fas fa-spinner fa-spin"></i> Saving...</span>
              </button>
            </div>
          </form>
          
          <div v-else class="profile-view">
            <div class="profile-section">
              <h3 class="section-title">Personal Information</h3>
              
              <div class="profile-field">
                <span class="field-label">Full Name:</span>
                <span class="field-value">{{ profileData.name }}</span>
              </div>
              
              <div class="profile-field">
                <span class="field-label">Email:</span>
                <span class="field-value">{{ profileData.email }}</span>
              </div>
              
              <div class="profile-field" v-if="profileData.phone">
                <span class="field-label">Phone:</span>
                <span class="field-value">{{ profileData.phone }}</span>
              </div>
              
              <div class="profile-field" v-if="profileData.bio">
                <span class="field-label">Bio:</span>
                <p class="field-value bio-text">{{ profileData.bio }}</p>
              </div>
            </div>
            
            <div class="profile-section" v-if="profileData.country || profileData.city">
              <h3 class="section-title">Location</h3>
              
              <div class="profile-field">
                <span class="field-label">Location:</span>
                <span class="field-value">
                  {{ [profileData.city, profileData.country].filter(Boolean).join(', ') }}
                </span>
              </div>
            </div>
            
            <div v-if="userRole === 'influencer'" class="profile-section">
              <h3 class="section-title">Influencer Details</h3>
              
              <div class="profile-field" v-if="profileData.categories && profileData.categories.length">
                <span class="field-label">Categories:</span>
                <div class="categories-display">
                  <span 
                    v-for="category in profileData.categories" 
                    :key="category"
                    class="category-tag"
                  >
                    {{ category }}
                  </span>
                </div>
              </div>
              
              <div class="profile-field" v-if="profileData.socialMedia && profileData.socialMedia.length">
                <span class="field-label">Social Media:</span>
                <div class="social-media-list">
                  <div 
                    v-for="(platform, index) in profileData.socialMedia" 
                    :key="index"
                    class="social-platform"
                  >
                    <i :class="getSocialIcon(platform.platform)"></i>
                    <div class="platform-details">
                      <span class="platform-name">{{ getPlatformName(platform.platform) }}</span>
                      <span class="platform-handle">{{ platform.handle }}</span>
                      <span class="platform-followers">{{ formatFollowers(platform.followers) }} followers</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-else-if="userRole === 'brand'" class="profile-section">
              <h3 class="section-title">Brand Details</h3>
              
              <div class="profile-field" v-if="profileData.company">
                <span class="field-label">Company:</span>
                <span class="field-value">{{ profileData.company }}</span>
              </div>
              
              <div class="profile-field" v-if="profileData.website">
                <span class="field-label">Website:</span>
                <a :href="profileData.website" target="_blank" class="website-link">
                  {{ profileData.website }}
                </a>
              </div>
              
              <div class="profile-field" v-if="profileData.industry">
                <span class="field-label">Industry:</span>
                <span class="field-value">{{ capitalizeFirst(profileData.industry) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { ref, computed, reactive, onMounted } from 'vue';
import { useStore } from 'vuex';

export default {
  name: 'ProfileView',
  
  setup() {
    const store = useStore();
    const loading = ref(true);
    const editMode = ref(false);
    const saving = ref(false);
    
    // Profile data from the API
    const profileData = ref({});
    
    // Form data for edit mode
    const form = reactive({
      name: '',
      email: '',
      phone: '',
      bio: '',
      country: '',
      city: '',
      company: '',
      website: '',
      industry: '',
      categories: [],
      socialMedia: [{
        platform: 'instagram',
        handle: '',
        followers: 0
      }]
    });
    
    // Available categories for influencers
    const availableCategories = [
      'Fashion', 'Beauty', 'Lifestyle', 'Travel', 'Food', 'Fitness', 'Technology', 
      'Gaming', 'Education', 'Business', 'Entertainment', 'Art', 'Music', 'Sports', 'Parenting'
    ];
    
    // User role from auth state
    const userRole = computed(() => {
      const user = store.getters['auth/user'];
      return user?.role?.toLowerCase() || 'influencer';
    });
    
    const userRoleDisplay = computed(() => {
      return userRole.value === 'brand' ? 'Brand Account' : 'Influencer Account';
    });
    
    const formattedJoinDate = computed(() => {
      if (!profileData.value.createdAt) return '';
      
      const date = new Date(profileData.value.createdAt);
      return date.toLocaleDateString('en-US', {
        month: 'long',
        year: 'numeric'
      });
    });
    
    // Load profile data
    onMounted(async () => {
      try {
        // Get profile data from the API
        const response = await store.dispatch('user/getProfile');
        profileData.value = response;
        
        // Initialize form with profile data
        initializeForm();
      } catch (error) {
        console.error('Error loading profile:', error);
      } finally {
        loading.value = false;
      }
    });
    
    // Initialize form with profile data
    const initializeForm = () => {
      form.name = profileData.value.name || '';
      form.email = profileData.value.email || '';
      form.phone = profileData.value.phone || '';
      form.bio = profileData.value.bio || '';
      form.country = profileData.value.country || '';
      form.city = profileData.value.city || '';
      
      if (userRole.value === 'brand') {
        form.company = profileData.value.company || '';
        form.website = profileData.value.website || '';
        form.industry = profileData.value.industry || '';
      } else {
        form.categories = [...(profileData.value.categories || [])];
        
        if (profileData.value.socialMedia && profileData.value.socialMedia.length > 0) {
          form.socialMedia = profileData.value.socialMedia.map(platform => ({ ...platform }));
        }
      }
    };
    
    // Handle avatar change
    const handleAvatarChange = async (event) => {
      const file = event.target.files[0];
      if (!file) return;
      
      const formData = new FormData();
      formData.append('avatar', file);
      
      try {
        const response = await store.dispatch('user/updateProfileAvatar', formData);
        profileData.value.avatar = response.avatar;
      } catch (error) {
        console.error('Error uploading avatar:', error);
      }
    };
    
    // Toggle category selection
    const toggleCategory = (category) => {
      const index = form.categories.indexOf(category);
      if (index === -1) {
        form.categories.push(category);
      } else {
        form.categories.splice(index, 1);
      }
    };
    
    // Add new social media platform
    const addPlatform = () => {
      form.socialMedia.push({
        platform: 'instagram',
        handle: '',
        followers: 0
      });
    };
    
    // Remove social media platform
    const removePlatform = (index) => {
      form.socialMedia.splice(index, 1);
    };
    
    // Save profile changes
    const saveProfile = async () => {
      saving.value = true;
      
      try {
        // Create updated profile data
        const updatedProfile = {
          name: form.name,
          phone: form.phone,
          bio: form.bio,
          country: form.country,
          city: form.city
        };
        
        if (userRole.value === 'brand') {
          updatedProfile.company = form.company;
          updatedProfile.website = form.website;
          updatedProfile.industry = form.industry;
        } else {
          updatedProfile.categories = form.categories;
          updatedProfile.socialMedia = form.socialMedia;
        }
        
        // Update profile via API
        const response = await store.dispatch('user/updateProfile', updatedProfile);
        profileData.value = response;
        
        // Exit edit mode
        editMode.value = false;
      } catch (error) {
        console.error('Error saving profile:', error);
      } finally {
        saving.value = false;
      }
    };
    
    // Utility functions
    const capitalizeFirst = (str) => {
      if (!str) return '';
      return str.charAt(0).toUpperCase() + str.slice(1);
    };
    
    const formatFollowers = (count) => {
      if (!count) return '0';
      
      if (count >= 1000000) {
        return (count / 1000000).toFixed(1) + 'M';
      } else if (count >= 1000) {
        return (count / 1000).toFixed(1) + 'K';
      }
      
      return count.toString();
    };
    
    const getSocialIcon = (platform) => {
      const icons = {
        instagram: 'fab fa-instagram',
        tiktok: 'fab fa-tiktok',
        youtube: 'fab fa-youtube',
        twitter: 'fab fa-twitter',
        facebook: 'fab fa-facebook'
      };
      
      return icons[platform] || 'fas fa-link';
    };
    
    const getPlatformName = (platform) => {
      const names = {
        instagram: 'Instagram',
        tiktok: 'TikTok',
        youtube: 'YouTube',
        twitter: 'Twitter',
        facebook: 'Facebook'
      };
      
      return names[platform] || platform;
    };
    
    return {
      loading,
      profileData,
      editMode,
      saving,
      form,
      userRole,
      userRoleDisplay,
      formattedJoinDate,
      availableCategories,
      handleAvatarChange,
      toggleCategory,
      addPlatform,
      removePlatform,
      saveProfile,
      capitalizeFirst,
      formatFollowers,
      getSocialIcon,
      getPlatformName
    };
  }
};
</script>

<style scoped>
.profile-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

.loading-state {
  text-align: center;
  padding: 3rem;
  background: #f9fafb;
  border-radius: 0.5rem;
  color: #6b7280;
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.toggle-edit-btn {
  padding: 0.5rem 1rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.toggle-edit-btn:hover {
  background-color: #2563eb;
}

.profile-content {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: 2rem;
}

/* Sidebar styles */
.profile-sidebar {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.profile-avatar-container {
  position: relative;
  width: 150px;
  height: 150px;
  margin-bottom: 1.5rem;
}

.profile-avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid white;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.profile-avatar-container:hover .avatar-overlay {
  opacity: 1;
}

.avatar-upload-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: white;
  cursor: pointer;
}

.avatar-upload-label i {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.avatar-upload {
  display: none;
}

.profile-meta {
  text-align: center;
}

.profile-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 0.5rem;
}

.profile-role {
  color: #3b82f6;
  font-weight: 500;
  margin: 0 0 1rem;
}

.profile-joined {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0;
}

.profile-joined i {
  margin-right: 0.25rem;
}

/* Profile form styles */
.profile-form, .profile-view {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.form-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.subsection-title {
  font-size: 1rem;
  font-weight: 600;
  color: #475569;
  margin: 1.5rem 0 1rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #475569;
  margin-bottom: 0.375rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.625rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  color: #1e293b;
  background-color: white;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.25);
}

.form-group input:disabled {
  background-color: #f8fafc;
  color: #64748b;
  cursor: not-allowed;
}

.field-hint {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

/* Categories selection */
.categories-selection {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.category-chip {
  padding: 0.375rem 0.75rem;
  background-color: #f1f5f9;
  color: #475569;
  border-radius: 1rem;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.category-chip:hover {
  background-color: #e2e8f0;
}

.category-chip.active {
  background-color: #3b82f6;
  color: white;
}

/* Social media section */
.social-media-item {
  margin-bottom: 1rem;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  background-color: #f8fafc;
}

.platform-select {
  flex: 0.3;
}

.handle-input {
  flex: 0.4;
}

.followers-input {
  flex: 0.3;
}

.remove-platform-btn {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #ef4444;
  color: #ef4444;
  background: none;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s;
  align-self: flex-end;
  margin-bottom: 0.5rem;
}

.remove-platform-btn:hover {
  background-color: #ef4444;
  color: white;
}

.add-platform-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: #f8fafc;
  color: #3b82f6;
  border: 1px solid #3b82f6;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.add-platform-btn:hover {
  background-color: #ebf5ff;
}

/* Form actions */
.form-actions {
  margin-top: 2rem;
  text-align: right;
}

.save-btn {
  padding: 0.75rem 1.5rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.save-btn:hover:not(:disabled) {
  background-color: #2563eb;
}

.save-btn:disabled {
  background-color: #94a3b8;
  cursor: not-allowed;
}

/* Profile view styles */
.profile-section {
  margin-bottom: 2rem;
}

.profile-field {
  margin-bottom: 1rem;
}

.field-label {
  font-weight: 500;
  color: #475569;
  min-width: 100px;
  display: inline-block;
}

.field-value {
  color: #1e293b;
}

.bio-text {
  white-space: pre-line;
  margin-top: 0.5rem;
  line-height: 1.5;
}

.categories-display {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.category-tag {
  padding: 0.375rem 0.75rem;
  background-color: #ebf5ff;
  color: #3b82f6;
  border-radius: 1rem;
  font-size: 0.75rem;
}

.social-media-list {
  margin-top: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.social-platform {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.social-platform i {
  font-size: 1.25rem;
  color: #3b82f6;
  width: 1.5rem;
  text-align: center;
}

.platform-details {
  display: flex;
  flex-direction: column;
}

.platform-name {
  font-weight: 500;
  color: #1e293b;
}

.platform-handle {
  color: #475569;
  font-size: 0.875rem;
}

.platform-followers {
  color: #6b7280;
  font-size: 0.75rem;
}

.website-link {
  color: #3b82f6;
  text-decoration: none;
}

.website-link:hover {
  text-decoration: underline;
}

/* Responsive styles */
@media (max-width: 768px) {
  .profile-content {
    grid-template-columns: 1fr;
  }
  
  .profile-sidebar {
    margin-bottom: 2rem;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .social-media-item .form-row {
    display: flex;
    flex-direction: column;
  }
  
  .remove-platform-btn {
    align-self: flex-end;
    margin-top: -2.5rem;
  }
}
</style> 