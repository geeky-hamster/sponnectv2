<template>
  <div class="campaign-submission">
    <div class="page-header">
      <router-link :to="`/influencer/requests/${requestId}`" class="back-link">
        <i class="fas fa-arrow-left"></i> Back to Request
      </router-link>
      <h1 class="page-title">Submit Deliverables</h1>
    </div>
    
    <div v-if="loading" class="loading-state">
      <p>Loading submission form...</p>
    </div>
    
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="fetchRequest" class="retry-button">Retry</button>
      <router-link :to="`/influencer/requests/${requestId}`" class="back-link">
        Back to Request
      </router-link>
    </div>
    
    <div v-else class="submission-container">
      <div class="campaign-info">
        <div class="campaign-title-wrapper">
          <h2 class="campaign-title">{{ adRequest.campaign?.title }}</h2>
          <span :class="['request-status', `status-${adRequest.status.toLowerCase()}`]">
            {{ adRequest.status }}
          </span>
        </div>
        
        <div class="campaign-sponsor">
          <img 
            :src="adRequest.campaign?.sponsor?.profileImage || '/img/default-company.png'" 
            :alt="adRequest.campaign?.sponsor?.name"
            class="sponsor-logo"
          />
          <span class="sponsor-name">{{ adRequest.campaign?.sponsor?.name }}</span>
        </div>
      </div>
      
      <div class="submission-form-container">
        <form @submit.prevent="submitDeliverables" class="submission-form">
          <h3 class="section-title">Required Deliverables</h3>
          
          <div v-if="!adRequest.campaign?.deliverables || adRequest.campaign.deliverables.length === 0" class="no-deliverables">
            <p>No specific deliverables have been outlined for this campaign.</p>
            <p>Please submit your content based on the campaign details and your application.</p>
          </div>
          
          <div v-else class="deliverables-list">
            <div v-for="(deliverable, index) in adRequest.campaign.deliverables" :key="index" class="deliverable-item">
              <div class="deliverable-header">
                <h4 class="deliverable-title">{{ deliverable.title }}</h4>
                <span class="deliverable-type">{{ deliverable.type }}</span>
              </div>
              <p class="deliverable-description">{{ deliverable.description }}</p>
            </div>
          </div>
          
          <div class="form-section">
            <h3 class="section-title">Your Submission</h3>
            
            <div class="form-group">
              <label for="submissionTitle" class="form-label">Title</label>
              <input 
                type="text"
                id="submissionTitle"
                v-model="submissionForm.title"
                class="form-input"
                placeholder="Give your submission a descriptive title"
                required
              />
            </div>
            
            <div class="form-group">
              <label for="submissionDescription" class="form-label">Description</label>
              <textarea 
                id="submissionDescription"
                v-model="submissionForm.description"
                class="form-textarea"
                placeholder="Describe what you've created and how it fulfills the campaign requirements"
                rows="4"
                required
              ></textarea>
            </div>
            
            <div class="form-group">
              <label class="form-label">Content URLs</label>
              <p class="help-text">Provide URLs to your content (e.g., Instagram post, YouTube video, TikTok, blog post)</p>
              
              <div 
                v-for="(url, index) in submissionForm.contentUrls" 
                :key="`url-${index}`"
                class="url-input-group"
              >
                <input 
                  type="url"
                  v-model="submissionForm.contentUrls[index]"
                  class="form-input"
                  placeholder="https://..."
                  required
                />
                <button 
                  type="button"
                  @click="removeUrl(index)"
                  class="remove-url-btn"
                  v-if="submissionForm.contentUrls.length > 1"
                >
                  <i class="fas fa-trash-alt"></i>
                </button>
              </div>
              
              <button 
                type="button"
                @click="addUrl"
                class="add-url-btn"
              >
                <i class="fas fa-plus"></i> Add Another URL
              </button>
            </div>
            
            <div class="form-group">
              <label class="form-label">Media Uploads (optional)</label>
              <p class="help-text">Upload screenshots, images, or additional files related to your submission</p>
              
              <div class="file-upload-container">
                <div class="file-upload-area" @click="triggerFileInput" @drop.prevent="handleFileDrop" @dragover.prevent>
                  <input 
                    type="file"
                    ref="fileInput"
                    @change="handleFileSelect"
                    multiple
                    class="file-input"
                  />
                  <i class="fas fa-cloud-upload-alt upload-icon"></i>
                  <p class="upload-text">
                    Drag files here or click to upload (max 5 files, 10MB each)
                  </p>
                </div>
                
                <div v-if="uploadedFiles.length > 0" class="uploaded-files">
                  <div 
                    v-for="(file, index) in uploadedFiles" 
                    :key="`file-${index}`"
                    class="uploaded-file-item"
                  >
                    <div class="file-info">
                      <i class="fas fa-file file-icon"></i>
                      <span class="file-name">{{ file.name }}</span>
                      <span class="file-size">({{ formatFileSize(file.size) }})</span>
                    </div>
                    <button 
                      type="button"
                      @click="removeFile(index)"
                      class="remove-file-btn"
                    >
                      <i class="fas fa-times"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="form-group">
              <label for="submissionNotes" class="form-label">Additional Notes (optional)</label>
              <textarea 
                id="submissionNotes"
                v-model="submissionForm.notes"
                class="form-textarea"
                placeholder="Any additional information you'd like to share with the sponsor"
                rows="3"
              ></textarea>
            </div>
          </div>
          
          <div class="form-actions">
            <router-link :to="`/influencer/requests/${requestId}`" class="cancel-button">
              Cancel
            </router-link>
            <button 
              type="submit"
              class="submit-button"
              :disabled="isSubmitting"
            >
              <span v-if="isSubmitting">
                <i class="fas fa-spinner fa-spin"></i> Submitting...
              </span>
              <span v-else>
                <i class="fas fa-paper-plane"></i> Submit Deliverables
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRoute, useRouter } from 'vue-router';

export default {
  name: 'CampaignSubmission',
  
  setup() {
    const store = useStore();
    const route = useRoute();
    const router = useRouter();
    const fileInput = ref(null);
    
    const requestId = route.params.id;
    const adRequest = ref({});
    const loading = ref(true);
    const error = ref(null);
    const isSubmitting = ref(false);
    const uploadedFiles = ref([]);
    
    const submissionForm = reactive({
      title: '',
      description: '',
      contentUrls: [''],
      notes: ''
    });
    
    const fetchRequest = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        const response = await store.dispatch('adRequests/getAdRequestById', requestId);
        adRequest.value = response;
        
        // Check if request is in the right status to allow submission
        if (!['ACCEPTED', 'IN_PROGRESS', 'NEEDS_REVISION'].includes(adRequest.value.status)) {
          error.value = 'This ad request is not currently in a state that allows submissions.';
        }
      } catch (err) {
        console.error('Error fetching ad request:', err);
        error.value = 'Failed to load ad request details. Please try again.';
      } finally {
        loading.value = false;
      }
    };
    
    const addUrl = () => {
      submissionForm.contentUrls.push('');
    };
    
    const removeUrl = (index) => {
      submissionForm.contentUrls.splice(index, 1);
    };
    
    const triggerFileInput = () => {
      fileInput.value.click();
    };
    
    const handleFileSelect = (event) => {
      const files = Array.from(event.target.files);
      validateAndAddFiles(files);
    };
    
    const handleFileDrop = (event) => {
      const files = Array.from(event.dataTransfer.files);
      validateAndAddFiles(files);
    };
    
    const validateAndAddFiles = (files) => {
      const MAX_FILES = 5;
      const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
      
      // Check if adding these new files would exceed the limit
      if (uploadedFiles.value.length + files.length > MAX_FILES) {
        alert(`You can upload a maximum of ${MAX_FILES} files.`);
        return;
      }
      
      const validFiles = files.filter(file => {
        if (file.size > MAX_FILE_SIZE) {
          alert(`File "${file.name}" exceeds the 10MB size limit.`);
          return false;
        }
        return true;
      });
      
      uploadedFiles.value = [...uploadedFiles.value, ...validFiles];
    };
    
    const removeFile = (index) => {
      uploadedFiles.value.splice(index, 1);
    };
    
    const formatFileSize = (bytes) => {
      if (bytes < 1024) return bytes + ' B';
      else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
      else return (bytes / 1048576).toFixed(1) + ' MB';
    };
    
    const submitDeliverables = async () => {
      isSubmitting.value = true;
      
      try {
        // Filter out empty URLs
        const filteredUrls = submissionForm.contentUrls.filter(url => url.trim() !== '');
        
        if (filteredUrls.length === 0) {
          alert('Please provide at least one content URL.');
          isSubmitting.value = false;
          return;
        }
        
        // Create FormData if there are files to upload
        let formData = null;
        if (uploadedFiles.value.length > 0) {
          formData = new FormData();
          uploadedFiles.value.forEach((file, index) => {
            formData.append(`file${index}`, file);
          });
        }
        
        // Prepare submission data
        const submissionData = {
          requestId,
          title: submissionForm.title,
          description: submissionForm.description,
          contentUrls: filteredUrls,
          notes: submissionForm.notes,
          files: formData
        };
        
        // Send the submission to the backend
        await store.dispatch('adRequests/submitDeliverables', submissionData);
        
        // Show success message
        // toast.success('Your deliverables have been submitted successfully!');
        
        // Redirect back to the ad request page
        router.push(`/influencer/requests/${requestId}`);
      } catch (err) {
        console.error('Error submitting deliverables:', err);
        // toast.error('Failed to submit deliverables. Please try again.');
      } finally {
        isSubmitting.value = false;
      }
    };
    
    // Initialize data
    onMounted(() => {
      fetchRequest();
    });
    
    return {
      requestId,
      adRequest,
      loading,
      error,
      submissionForm,
      isSubmitting,
      fileInput,
      uploadedFiles,
      fetchRequest,
      addUrl,
      removeUrl,
      triggerFileInput,
      handleFileSelect,
      handleFileDrop,
      removeFile,
      formatFileSize,
      submitDeliverables
    };
  }
};
</script>

<style scoped>
.campaign-submission {
  padding: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.back-link {
  color: #4b5563;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.loading-state, .error-state {
  text-align: center;
  padding: 3rem;
  background: #f9fafb;
  border-radius: 0.5rem;
  margin: 2rem 0;
}

.error-state .back-link {
  display: inline-block;
  margin-top: 1rem;
}

.retry-button {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  margin-top: 1rem;
  cursor: pointer;
}

.submission-container {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  overflow: hidden;
}

.campaign-info {
  padding: 1.5rem;
  background-color: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.campaign-title-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.campaign-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.request-status {
  padding: 0.25rem 0.75rem;
  border-radius: 2rem;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.status-accepted {
  background-color: #10b981;
  color: white;
}

.status-in_progress {
  background-color: #3b82f6;
  color: white;
}

.status-needs_revision {
  background-color: #f59e0b;
  color: white;
}

.campaign-sponsor {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sponsor-logo {
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  object-fit: cover;
}

.sponsor-name {
  font-size: 0.875rem;
  color: #4b5563;
}

.submission-form-container {
  padding: 1.5rem;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-top: 0;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.no-deliverables {
  background-color: #f9fafb;
  border-radius: 0.375rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.no-deliverables p {
  margin: 0 0 0.5rem 0;
  color: #4b5563;
}

.deliverables-list {
  margin-bottom: 2rem;
}

.deliverable-item {
  background-color: #f9fafb;
  border-radius: 0.375rem;
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.deliverable-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.deliverable-title {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
}

.deliverable-type {
  font-size: 0.75rem;
  color: #6b7280;
  background-color: #e5e7eb;
  padding: 0.125rem 0.5rem;
  border-radius: 1rem;
}

.deliverable-description {
  margin: 0;
  color: #4b5563;
  line-height: 1.5;
}

.form-section {
  margin-top: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #1f2937;
}

.help-text {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0;
  margin-bottom: 0.75rem;
}

.form-input, .form-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-input:focus, .form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.url-input-group {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.remove-url-btn {
  background-color: #ef4444;
  color: white;
  border: none;
  width: 2.5rem;
  border-radius: 0.375rem;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
}

.add-url-btn {
  background: none;
  border: 1px dashed #d1d5db;
  color: #4b5563;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.add-url-btn:hover {
  background-color: #f9fafb;
  color: #3b82f6;
  border-color: #3b82f6;
}

.file-upload-container {
  margin-top: 0.5rem;
}

.file-upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 0.375rem;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s;
  position: relative;
}

.file-upload-area:hover {
  border-color: #3b82f6;
}

.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.upload-icon {
  font-size: 2rem;
  color: #6b7280;
  margin-bottom: 1rem;
}

.upload-text {
  margin: 0;
  color: #6b7280;
}

.uploaded-files {
  margin-top: 1rem;
}

.uploaded-file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background-color: #f9fafb;
  border-radius: 0.375rem;
  margin-bottom: 0.5rem;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.file-icon {
  color: #6b7280;
}

.file-name {
  font-size: 0.875rem;
  font-weight: 500;
}

.file-size {
  font-size: 0.75rem;
  color: #6b7280;
}

.remove-file-btn {
  background: none;
  border: none;
  color: #ef4444;
  cursor: pointer;
  font-size: 1rem;
}

.form-actions {
  margin-top: 2rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.cancel-button {
  padding: 0.75rem 1.5rem;
  background-color: white;
  color: #6b7280;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-weight: 500;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
}

.submit-button {
  padding: 0.75rem 1.5rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.submit-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .campaign-title-wrapper {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .request-status {
    align-self: flex-start;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .cancel-button, .submit-button {
    width: 100%;
    justify-content: center;
  }
}
</style> 