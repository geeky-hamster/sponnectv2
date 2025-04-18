<template>
  <div class="submit-ad-request">
    <div v-if="loading" class="loading-state">
      <p>Loading request details...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="fetchRequestDetails" class="retry-button">Retry</button>
      <router-link :to="`/influencer/ad-requests/${requestId}`" class="back-link">Back to Request</router-link>
    </div>

    <template v-else>
      <div class="page-header">
        <div class="breadcrumbs">
          <router-link to="/influencer/ad-requests" class="breadcrumb-link">My Ad Requests</router-link>
          <span class="breadcrumb-separator">/</span>
          <router-link :to="`/influencer/ad-requests/${requestId}`" class="breadcrumb-link">Request #{{ requestId }}</router-link>
          <span class="breadcrumb-separator">/</span>
          <span class="breadcrumb-current">Submit Deliverables</span>
        </div>
      </div>

      <div class="content-container">
        <div class="request-summary-card">
          <h2 class="card-title">Campaign Summary</h2>
          <div class="campaign-header">
            <img 
              v-if="request.campaign.thumbnailUrl" 
              :src="request.campaign.thumbnailUrl" 
              :alt="request.campaign.title" 
              class="campaign-thumbnail"
            />
            <div v-else class="campaign-thumbnail placeholder">
              <i class="fas fa-image"></i>
            </div>
            <div class="campaign-header-info">
              <h3 class="campaign-title">{{ request.campaign.title }}</h3>
              <div class="campaign-sponsor">
                <img 
                  :src="request.sponsor.profileImage || '/img/default-company.png'" 
                  :alt="request.sponsor.name" 
                  class="sponsor-logo"
                />
                <span>{{ request.sponsor.name }}</span>
              </div>
            </div>
          </div>

          <div class="due-date" :class="{ 'overdue': isOverdue(request.dueDate) }">
            <span class="due-date-label">Due Date:</span>
            <span class="due-date-value">{{ formatDate(request.dueDate) }}</span>
            <span v-if="isOverdue(request.dueDate)" class="overdue-label">Overdue!</span>
          </div>

          <div class="deliverables-section">
            <h3>Required Deliverables</h3>
            <ul class="deliverables-list">
              <li v-for="(deliverable, index) in request.campaign.deliverables" :key="index">
                {{ deliverable }}
              </li>
            </ul>
          </div>
        </div>

        <div class="submission-form-card">
          <h2 class="card-title">Submit Your Work</h2>
          
          <form @submit.prevent="submitDeliverables" class="submission-form">
            <div class="form-group">
              <label for="description">Description of Your Work</label>
              <textarea 
                id="description" 
                v-model="submission.description" 
                rows="5" 
                class="form-control"
                placeholder="Describe what you've created and how it meets the requirements..."
                required
              ></textarea>
            </div>

            <div class="form-group">
              <label>Links</label>
              <p class="form-hint">Add links to posts, videos, or other content you've created for this campaign.</p>
              
              <div 
                v-for="(link, index) in submission.links" 
                :key="`link-${index}`"
                class="link-input-group"
              >
                <input 
                  type="url" 
                  v-model="submission.links[index]" 
                  placeholder="https://example.com/your-content" 
                  class="form-control"
                />
                <button 
                  type="button" 
                  @click="removeLink(index)" 
                  class="remove-button"
                  title="Remove link"
                >
                  <i class="fas fa-times"></i>
                </button>
              </div>
              
              <button 
                type="button" 
                @click="addLink" 
                class="add-button"
              >
                <i class="fas fa-plus"></i> Add Link
              </button>
            </div>

            <div class="form-group">
              <label>Attachments</label>
              <p class="form-hint">Upload images, documents, or other files related to your deliverables.</p>
              
              <div class="dropzone" @dragover.prevent @drop="onDrop">
                <input 
                  type="file" 
                  ref="fileInput" 
                  @change="onFileSelected" 
                  multiple 
                  class="file-input" 
                />
                <div class="dropzone-content">
                  <i class="fas fa-cloud-upload-alt"></i>
                  <p>Drag files here or click to browse</p>
                  <p class="dropzone-hint">Max 10MB per file, up to 5 files</p>
                </div>
              </div>
              
              <div v-if="uploadingFiles" class="uploading-indicator">
                <p>Uploading files... {{ uploadProgress }}%</p>
                <div class="progress-bar">
                  <div class="progress" :style="{ width: `${uploadProgress}%` }"></div>
                </div>
              </div>
              
              <div v-if="submission.attachments.length > 0" class="attachments-preview">
                <div 
                  v-for="(file, index) in submission.attachments" 
                  :key="`file-${index}`"
                  class="attachment-preview-item"
                >
                  <div class="attachment-preview">
                    <img 
                      v-if="isImageFile(file.filename)" 
                      :src="file.url" 
                      :alt="file.filename" 
                    />
                    <div v-else class="file-icon">
                      <i class="fas fa-file"></i>
                    </div>
                  </div>
                  <div class="attachment-info">
                    <span class="attachment-filename">{{ file.filename }}</span>
                    <button 
                      type="button" 
                      @click="removeFile(index)" 
                      class="remove-button small"
                      title="Remove file"
                    >
                      <i class="fas fa-times"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div class="form-group verification-checkbox">
              <label class="checkbox-label">
                <input 
                  type="checkbox" 
                  v-model="submission.verified" 
                  required
                />
                <span>I confirm that all the deliverables meet the requirements of this campaign and the content complies with Sponnect's terms of service.</span>
              </label>
            </div>

            <div class="form-actions">
              <router-link :to="`/influencer/ad-requests/${requestId}`" class="cancel-button">
                Cancel
              </router-link>
              <button 
                type="submit" 
                class="submit-button" 
                :disabled="isSubmitting || !isFormValid"
              >
                <span v-if="isSubmitting">
                  <i class="fas fa-spinner fa-spin"></i> Submitting...
                </span>
                <span v-else>Submit Deliverables</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRoute, useRouter } from 'vue-router';

export default {
  name: 'SubmitAdRequest',
  
  setup() {
    const store = useStore();
    const route = useRoute();
    const router = useRouter();
    const fileInput = ref(null);
    
    const requestId = route.params.id;
    const request = ref({});
    const loading = ref(true);
    const error = ref(null);
    
    const submission = ref({
      description: '',
      links: [''],
      attachments: [],
      verified: false
    });
    
    const isSubmitting = ref(false);
    const uploadingFiles = ref(false);
    const uploadProgress = ref(0);
    
    const fetchRequestDetails = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        // Replace with actual API call when implemented
        const response = await store.dispatch('adRequests/getAdRequestById', requestId);
        request.value = response;
        
        // Check if the request is in a state that allows submission
        if (request.value.status !== 'active') {
          error.value = 'This request is not currently active and cannot accept submissions.';
        }
      } catch (err) {
        error.value = 'Failed to load request details. Please try again.';
        console.error(err);
      } finally {
        loading.value = false;
      }
    };
    
    const formatDate = (dateString) => {
      if (!dateString) return 'N/A';
      
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    };
    
    const isOverdue = (dueDate) => {
      if (!dueDate) return false;
      
      const now = new Date();
      const due = new Date(dueDate);
      return due < now;
    };
    
    const isImageFile = (filename) => {
      if (!filename) return false;
      
      const extension = filename.split('.').pop().toLowerCase();
      return ['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(extension);
    };
    
    const addLink = () => {
      submission.value.links.push('');
    };
    
    const removeLink = (index) => {
      submission.value.links = submission.value.links.filter((_, i) => i !== index);
      
      // Always keep at least one link input
      if (submission.value.links.length === 0) {
        submission.value.links.push('');
      }
    };
    
    const onFileSelected = async (event) => {
      const files = Array.from(event.target.files);
      if (files.length === 0) return;
      
      await uploadFiles(files);
    };
    
    const onDrop = async (event) => {
      event.preventDefault();
      const files = Array.from(event.dataTransfer.files);
      if (files.length === 0) return;
      
      await uploadFiles(files);
    };
    
    const uploadFiles = async (files) => {
      // Check file limits
      if (submission.value.attachments.length + files.length > 5) {
        alert('You can upload a maximum of 5 files.');
        return;
      }
      
      const oversizedFiles = files.filter(file => file.size > 10 * 1024 * 1024);
      if (oversizedFiles.length > 0) {
        alert(`The following files exceed the 10MB limit: ${oversizedFiles.map(f => f.name).join(', ')}`);
        return;
      }
      
      uploadingFiles.value = true;
      uploadProgress.value = 0;
      
      try {
        // Simulate upload progress
        const interval = setInterval(() => {
          uploadProgress.value += 5;
          if (uploadProgress.value >= 90) {
            clearInterval(interval);
          }
        }, 100);
        
        // Replace with actual file upload implementation
        // This is a mock implementation
        const uploadedFiles = await Promise.all(files.map(async (file) => {
          // Simulate API call delay
          await new Promise(resolve => setTimeout(resolve, 1000));
          
          // Create a preview URL for the file
          const url = URL.createObjectURL(file);
          
          return {
            id: `temp-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
            filename: file.name,
            size: file.size,
            type: file.type,
            url: url
          };
        }));
        
        // Clear any intervals
        clearInterval(interval);
        uploadProgress.value = 100;
        
        // Add the uploaded files to the attachments
        submission.value.attachments = [
          ...submission.value.attachments,
          ...uploadedFiles
        ];
        
        // Reset the file input
        if (fileInput.value) {
          fileInput.value.value = '';
        }
      } catch (err) {
        console.error('Error uploading files:', err);
        alert('There was an error uploading the files. Please try again.');
      } finally {
        // Set a timeout to show 100% completion briefly before hiding
        setTimeout(() => {
          uploadingFiles.value = false;
          uploadProgress.value = 0;
        }, 500);
      }
    };
    
    const removeFile = (index) => {
      const file = submission.value.attachments[index];
      
      // If there's a URL object, revoke it to free up memory
      if (file.url && file.url.startsWith('blob:')) {
        URL.revokeObjectURL(file.url);
      }
      
      // Remove the file from the array
      submission.value.attachments = submission.value.attachments.filter((_, i) => i !== index);
    };
    
    const isFormValid = computed(() => {
      // Basic validation rules
      const hasDescription = submission.value.description.trim().length > 0;
      const hasValidLinks = submission.value.links.some(link => link.trim().length > 0);
      const isVerified = submission.value.verified;
      
      return hasDescription && (hasValidLinks || submission.value.attachments.length > 0) && isVerified;
    });
    
    const submitDeliverables = async () => {
      if (!isFormValid.value) return;
      
      isSubmitting.value = true;
      
      try {
        // Clean up the links array to remove empty entries
        const links = submission.value.links.filter(link => link.trim().length > 0);
        
        const submissionData = {
          requestId: requestId,
          description: submission.value.description,
          links: links,
          attachmentIds: submission.value.attachments.map(file => file.id)
        };
        
        // Replace with actual API call when implemented
        await store.dispatch('adRequests/submitDeliverables', submissionData);
        
        // Show success message and redirect
        router.push({
          path: `/influencer/ad-requests/${requestId}`,
          query: { submission: 'success' }
        });
      } catch (err) {
        console.error('Error submitting deliverables:', err);
        alert('There was an error submitting your deliverables. Please try again.');
      } finally {
        isSubmitting.value = false;
      }
    };
    
    // Initialize data
    onMounted(() => {
      fetchRequestDetails();
    });
    
    return {
      requestId,
      request,
      loading,
      error,
      submission,
      isSubmitting,
      uploadingFiles,
      uploadProgress,
      fileInput,
      isFormValid,
      formatDate,
      isOverdue,
      isImageFile,
      addLink,
      removeLink,
      onFileSelected,
      onDrop,
      removeFile,
      submitDeliverables,
      fetchRequestDetails
    };
  }
}
</script>

<style scoped>
.submit-ad-request {
  padding: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.loading-state, .error-state {
  text-align: center;
  padding: 3rem;
  background: #f9f9f9;
  border-radius: 8px;
  margin: 2rem 0;
}

.retry-button {
  background-color: #4a90e2;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  margin-top: 1rem;
  cursor: pointer;
}

.back-link {
  display: block;
  margin-top: 1rem;
  color: #4a90e2;
  text-decoration: none;
}

.page-header {
  margin-bottom: 2rem;
}

.breadcrumbs {
  display: flex;
  align-items: center;
  font-size: 0.9rem;
}

.breadcrumb-link {
  color: #4a90e2;
  text-decoration: none;
}

.breadcrumb-separator {
  margin: 0 0.5rem;
  color: #999;
}

.breadcrumb-current {
  color: #666;
  font-weight: 500;
}

.content-container {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 2rem;
}

.request-summary-card, .submission-form-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.card-title {
  font-size: 1.25rem;
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.75rem;
}

.campaign-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.campaign-thumbnail {
  width: 70px;
  height: 70px;
  border-radius: 8px;
  object-fit: cover;
}

.campaign-thumbnail.placeholder {
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #aaa;
  font-size: 1.5rem;
}

.campaign-header-info {
  flex: 1;
}

.campaign-title {
  font-size: 1.1rem;
  margin: 0 0 0.5rem 0;
  color: #333;
}

.campaign-sponsor {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #666;
}

.sponsor-logo {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  object-fit: cover;
}

.due-date {
  background-color: #f9f9f9;
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.due-date-label {
  font-weight: 500;
  color: #555;
}

.due-date.overdue {
  background-color: rgba(217, 83, 79, 0.1);
}

.overdue-label {
  background-color: #d9534f;
  color: white;
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
  border-radius: 10px;
  font-weight: 500;
  margin-left: auto;
}

.deliverables-section h3 {
  font-size: 1rem;
  margin-top: 0;
  margin-bottom: 1rem;
  color: #444;
}

.deliverables-list {
  padding-left: 1.5rem;
  margin-bottom: 0;
}

.deliverables-list li {
  margin-bottom: 0.5rem;
  line-height: 1.5;
}

.submission-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  font-family: inherit;
}

textarea.form-control {
  resize: vertical;
  min-height: 100px;
}

.form-hint {
  font-size: 0.85rem;
  color: #666;
  margin: 0 0 0.5rem 0;
}

.link-input-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.remove-button {
  background-color: #d9534f;
  color: white;
  border: none;
  width: 2rem;
  height: 2rem;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-button.small {
  width: 1.5rem;
  height: 1.5rem;
  font-size: 0.75rem;
}

.add-button {
  background-color: #5bc0de;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  align-self: flex-start;
}

.dropzone {
  border: 2px dashed #ddd;
  border-radius: 4px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  position: relative;
  margin-bottom: 1rem;
}

.dropzone:hover {
  border-color: #5bc0de;
}

.dropzone-content {
  color: #666;
}

.dropzone-content i {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  color: #5bc0de;
}

.dropzone-hint {
  font-size: 0.75rem;
  color: #999;
  margin-top: 0.5rem;
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

.uploading-indicator {
  margin: 1rem 0;
}

.progress-bar {
  height: 8px;
  background-color: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
  margin-top: 0.5rem;
}

.progress {
  height: 100%;
  background-color: #5bc0de;
  transition: width 0.2s ease;
}

.attachments-preview {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.attachment-preview-item {
  display: flex;
  flex-direction: column;
}

.attachment-preview {
  width: 100%;
  height: 100px;
  border-radius: 4px;
  overflow: hidden;
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.5rem;
}

.attachment-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.file-icon {
  color: #999;
  font-size: 2rem;
}

.attachment-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.attachment-filename {
  font-size: 0.8rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: calc(100% - 2rem);
}

.verification-checkbox {
  margin-top: 1rem;
}

.checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  font-size: 0.9rem;
  color: #555;
}

.checkbox-label input {
  margin-top: 3px;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.cancel-button {
  background-color: transparent;
  color: #666;
  border: 1px solid #ddd;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  text-decoration: none;
  text-align: center;
}

.submit-button {
  background-color: #5cb85c;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  min-width: 180px;
}

.submit-button:disabled {
  background-color: #aaa;
  cursor: not-allowed;
}

@media (max-width: 900px) {
  .content-container {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 500px) {
  .form-actions {
    flex-direction: column;
    gap: 1rem;
  }
  
  .cancel-button, .submit-button {
    width: 100%;
  }
}
</style> 