<template>
  <div class="ad-request-detail">
    <div v-if="loading" class="loading-state">
      <p>Loading request details...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="fetchRequestDetails" class="retry-button">Retry</button>
      <router-link to="/influencer/ad-requests" class="back-link">Back to Ad Requests</router-link>
    </div>

    <template v-else>
      <div class="page-header">
        <div class="breadcrumbs">
          <router-link to="/influencer/ad-requests" class="breadcrumb-link">My Ad Requests</router-link>
          <span class="breadcrumb-separator">/</span>
          <span class="breadcrumb-current">Request #{{ request.id }}</span>
        </div>
        
        <div class="header-actions">
          <button 
            v-if="canBeCanceled(request.status)"
            @click="cancelRequest" 
            class="cancel-button"
          >
            <i class="fas fa-times"></i> Cancel Request
          </button>
          
          <button 
            v-if="request.status === 'approved'"
            @click="startWork" 
            class="start-button"
          >
            <i class="fas fa-play"></i> Start Work
          </button>
          
          <button 
            v-if="request.status === 'active'"
            @click="submitWork" 
            class="submit-button"
          >
            <i class="fas fa-check"></i> Submit Deliverables
          </button>
        </div>
      </div>

      <div class="request-status-container">
        <div class="status-badge" :class="getStatusClass(request.status)">
          {{ formatStatus(request.status) }}
        </div>
        
        <div v-if="request.status === 'rejected'" class="rejection-reason">
          <strong>Reason for rejection:</strong>
          <p>{{ request.rejectionReason || 'No reason provided' }}</p>
        </div>
      </div>

      <div class="content-grid">
        <div class="campaign-details">
          <div class="campaign-card">
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
              <h2 class="campaign-title">{{ request.campaign.title }}</h2>
            </div>
            
            <div class="campaign-info-grid">
              <div class="info-item">
                <div class="info-label">Sponsor</div>
                <div class="info-value">
                  <img 
                    :src="request.sponsor.profileImage || '/img/default-company.png'" 
                    :alt="request.sponsor.name" 
                    class="sponsor-logo"
                  />
                  <span>{{ request.sponsor.name }}</span>
                </div>
              </div>
              
              <div class="info-item">
                <div class="info-label">Platform</div>
                <div class="info-value">{{ request.campaign.platform }}</div>
              </div>
              
              <div class="info-item">
                <div class="info-label">Category</div>
                <div class="info-value">{{ request.campaign.category }}</div>
              </div>
              
              <div class="info-item">
                <div class="info-label">Budget</div>
                <div class="info-value">${{ request.budget }}</div>
              </div>
              
              <div class="info-item">
                <div class="info-label">Due Date</div>
                <div class="info-value" :class="{ 'overdue': isOverdue(request.dueDate) }">
                  {{ formatDate(request.dueDate) }}
                </div>
              </div>
              
              <div class="info-item">
                <div class="info-label">Request Submitted</div>
                <div class="info-value">{{ formatDate(request.createdAt) }}</div>
              </div>
            </div>
            
            <div class="campaign-description">
              <h3>Campaign Description</h3>
              <p>{{ request.campaign.description }}</p>
            </div>
          </div>
        </div>

        <div class="request-details">
          <div class="request-card">
            <h3>Your Application</h3>
            
            <div class="application-content">
              <p v-if="request.proposal">{{ request.proposal }}</p>
              <p v-else class="no-content">No proposal submitted with this application.</p>
            </div>
            
            <h3>Required Deliverables</h3>
            <ul class="deliverables-list">
              <li v-for="(deliverable, index) in request.campaign.deliverables" :key="index">
                {{ deliverable }}
              </li>
            </ul>
            
            <div v-if="request.status === 'active' || request.status === 'completed'" class="submission-section">
              <h3>Your Submission</h3>
              <div v-if="request.submissions && request.submissions.length > 0">
                <div 
                  v-for="(submission, index) in request.submissions" 
                  :key="index"
                  class="submission-item"
                >
                  <div class="submission-header">
                    <span class="submission-date">Submitted on {{ formatDate(submission.createdAt) }}</span>
                    <span 
                      v-if="submission.status" 
                      class="submission-status"
                      :class="getSubmissionStatusClass(submission.status)"
                    >
                      {{ formatSubmissionStatus(submission.status) }}
                    </span>
                  </div>
                  
                  <div class="submission-content">
                    <p>{{ submission.description }}</p>
                    
                    <div v-if="submission.links && submission.links.length > 0" class="submission-links">
                      <h4>Links</h4>
                      <ul>
                        <li v-for="(link, linkIndex) in submission.links" :key="linkIndex">
                          <a :href="link" target="_blank" rel="noopener noreferrer">{{ link }}</a>
                        </li>
                      </ul>
                    </div>
                    
                    <div v-if="submission.attachments && submission.attachments.length > 0" class="submission-attachments">
                      <h4>Attachments</h4>
                      <div class="attachments-grid">
                        <div 
                          v-for="(attachment, attachIndex) in submission.attachments" 
                          :key="attachIndex"
                          class="attachment-item"
                        >
                          <a 
                            :href="attachment.url" 
                            target="_blank" 
                            rel="noopener noreferrer"
                            class="attachment-link"
                          >
                            <div class="attachment-preview">
                              <img 
                                v-if="isImageAttachment(attachment.filename)" 
                                :src="attachment.url" 
                                :alt="attachment.filename"
                              />
                              <div v-else class="file-icon">
                                <i class="fas fa-file"></i>
                              </div>
                            </div>
                            <span class="attachment-filename">{{ attachment.filename }}</span>
                          </a>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div v-if="submission.feedback" class="submission-feedback">
                    <h4>Sponsor Feedback</h4>
                    <p>{{ submission.feedback }}</p>
                  </div>
                </div>
              </div>
              <div v-else class="no-submission">
                <p v-if="request.status === 'active'">
                  You haven't submitted your deliverables yet.
                  <button @click="submitWork" class="submit-button small">Submit Now</button>
                </p>
                <p v-else>No submission record found.</p>
              </div>
            </div>
          </div>
          
          <div v-if="request.status === 'active' || request.status === 'completed'" class="timeline-card">
            <h3>Request Timeline</h3>
            <ul class="timeline">
              <li 
                v-for="(event, index) in requestTimeline" 
                :key="index"
                class="timeline-item"
                :class="{ 'last': index === requestTimeline.length - 1 }"
              >
                <div class="timeline-marker"></div>
                <div class="timeline-content">
                  <h4 class="event-title">{{ event.title }}</h4>
                  <p class="event-time">{{ formatDateTime(event.timestamp) }}</p>
                  <p v-if="event.description" class="event-description">{{ event.description }}</p>
                </div>
              </li>
            </ul>
          </div>
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
  name: 'AdRequestDetail',
  
  setup() {
    const store = useStore();
    const route = useRoute();
    const router = useRouter();
    
    const requestId = route.params.id;
    const request = ref({});
    const loading = ref(true);
    const error = ref(null);
    
    const fetchRequestDetails = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        // Replace with actual API call when implemented
        const response = await store.dispatch('adRequests/getAdRequestById', requestId);
        request.value = response;
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
    
    const formatDateTime = (dateString) => {
      if (!dateString) return 'N/A';
      
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    };
    
    const formatStatus = (status) => {
      if (!status) return 'Unknown';
      
      const statusMap = {
        'pending': 'Pending Review',
        'approved': 'Approved',
        'active': 'In Progress',
        'completed': 'Completed',
        'rejected': 'Rejected',
        'canceled': 'Canceled'
      };
      
      return statusMap[status] || status;
    };
    
    const formatSubmissionStatus = (status) => {
      if (!status) return 'Pending Review';
      
      const statusMap = {
        'pending': 'Pending Review',
        'approved': 'Approved',
        'rejected': 'Rejected',
        'revision_requested': 'Revision Requested'
      };
      
      return statusMap[status] || status;
    };
    
    const getStatusClass = (status) => {
      return `status-${status}`;
    };
    
    const getSubmissionStatusClass = (status) => {
      return `submission-status-${status}`;
    };
    
    const isOverdue = (dueDate) => {
      if (!dueDate) return false;
      
      const now = new Date();
      const due = new Date(dueDate);
      return due < now;
    };
    
    const canBeCanceled = (status) => {
      return ['pending', 'approved'].includes(status);
    };
    
    const isImageAttachment = (filename) => {
      if (!filename) return false;
      
      const extension = filename.split('.').pop().toLowerCase();
      return ['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(extension);
    };
    
    const requestTimeline = computed(() => {
      if (!request.value || !request.value.history) {
        return [];
      }
      
      return [
        {
          title: 'Request Submitted',
          timestamp: request.value.createdAt,
          description: 'You applied for this campaign.'
        },
        ...(request.value.history || [])
      ];
    });
    
    const startWork = async () => {
      try {
        await store.dispatch('adRequests/startWork', requestId);
        fetchRequestDetails();
      } catch (err) {
        console.error('Failed to start work:', err);
      }
    };
    
    const submitWork = () => {
      router.push(`/influencer/ad-requests/${requestId}/submit`);
    };
    
    const cancelRequest = async () => {
      if (!confirm('Are you sure you want to cancel this request? This action cannot be undone.')) {
        return;
      }
      
      try {
        await store.dispatch('adRequests/cancelRequest', requestId);
        fetchRequestDetails();
      } catch (err) {
        console.error('Failed to cancel request:', err);
      }
    };
    
    // Initialize data
    onMounted(() => {
      fetchRequestDetails();
    });
    
    return {
      request,
      loading,
      error,
      formatDate,
      formatDateTime,
      formatStatus,
      formatSubmissionStatus,
      getStatusClass,
      getSubmissionStatusClass,
      isOverdue,
      canBeCanceled,
      isImageAttachment,
      requestTimeline,
      startWork,
      submitWork,
      cancelRequest,
      fetchRequestDetails
    };
  }
}
</script>

<style scoped>
.ad-request-detail {
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
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

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.header-actions button {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.cancel-button {
  background-color: #d9534f;
  color: white;
}

.start-button {
  background-color: #5bc0de;
  color: white;
}

.submit-button {
  background-color: #5cb85c;
  color: white;
}

.submit-button.small {
  padding: 0.4rem 0.8rem;
  font-size: 0.85rem;
}

.request-status-container {
  margin-bottom: 2rem;
}

.status-badge {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  display: inline-block;
  margin-bottom: 1rem;
}

.status-pending {
  background-color: #f0ad4e;
  color: white;
}

.status-approved {
  background-color: #5bc0de;
  color: white;
}

.status-active {
  background-color: #5cb85c;
  color: white;
}

.status-completed {
  background-color: #7ed321;
  color: white;
}

.status-rejected {
  background-color: #d9534f;
  color: white;
}

.status-canceled {
  background-color: #777;
  color: white;
}

.rejection-reason {
  background-color: rgba(217, 83, 79, 0.1);
  border-left: 4px solid #d9534f;
  padding: 1rem;
  margin-top: 1rem;
}

.rejection-reason p {
  margin: 0.5rem 0 0;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 2rem;
}

.campaign-card, .request-card, .timeline-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.campaign-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.campaign-thumbnail {
  width: 80px;
  height: 80px;
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

.campaign-title {
  font-size: 1.4rem;
  margin: 0;
  color: #333;
}

.campaign-info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  font-size: 0.85rem;
  color: #666;
}

.info-value {
  font-weight: 500;
  color: #333;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sponsor-logo {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
}

.overdue {
  color: #d9534f;
}

.campaign-description h3, .request-card h3, .timeline-card h3 {
  font-size: 1.1rem;
  margin-top: 0;
  margin-bottom: 1rem;
  color: #444;
}

.campaign-description p {
  line-height: 1.6;
  color: #555;
}

.application-content {
  background-color: #f9f9f9;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 2rem;
}

.no-content {
  color: #888;
  font-style: italic;
}

.deliverables-list {
  padding-left: 1.5rem;
  margin-bottom: 2rem;
}

.deliverables-list li {
  margin-bottom: 0.5rem;
  line-height: 1.5;
}

.submission-section h3 {
  margin-top: 1.5rem;
}

.submission-item {
  background-color: #f9f9f9;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.submission-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.submission-date {
  font-size: 0.85rem;
  color: #666;
}

.submission-status {
  padding: 0.25rem 0.5rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
}

.submission-status-pending {
  background-color: #f0ad4e;
  color: white;
}

.submission-status-approved {
  background-color: #5cb85c;
  color: white;
}

.submission-status-rejected {
  background-color: #d9534f;
  color: white;
}

.submission-status-revision_requested {
  background-color: #5bc0de;
  color: white;
}

.submission-content {
  margin-bottom: 1rem;
}

.submission-content p {
  margin-top: 0;
}

.submission-links h4, .submission-attachments h4 {
  font-size: 0.95rem;
  margin-bottom: 0.5rem;
}

.submission-links ul {
  padding-left: 1.5rem;
  margin-bottom: 1rem;
}

.submission-links a {
  color: #4a90e2;
  word-break: break-all;
}

.attachments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 1rem;
}

.attachment-item {
  display: flex;
  flex-direction: column;
}

.attachment-link {
  text-decoration: none;
  color: inherit;
}

.attachment-preview {
  width: 100%;
  height: 80px;
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
  font-size: 1.75rem;
}

.attachment-filename {
  font-size: 0.8rem;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.submission-feedback {
  background-color: rgba(74, 144, 226, 0.1);
  border-left: 4px solid #4a90e2;
  padding: 1rem;
}

.submission-feedback h4 {
  margin-top: 0;
  font-size: 0.95rem;
  margin-bottom: 0.5rem;
  color: #4a90e2;
}

.no-submission {
  background-color: #f9f9f9;
  padding: 1rem;
  border-radius: 4px;
  text-align: center;
}

.timeline {
  list-style: none;
  padding: 0;
  margin: 0;
  position: relative;
}

.timeline::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 7px;
  width: 2px;
  background-color: #eee;
}

.timeline-item {
  position: relative;
  padding-left: 30px;
  padding-bottom: 2rem;
}

.timeline-item.last {
  padding-bottom: 0;
}

.timeline-marker {
  position: absolute;
  left: 0;
  top: 0;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background-color: #4a90e2;
  border: 2px solid white;
  box-shadow: 0 0 0 2px #4a90e2;
}

.timeline-content {
  background-color: #f9f9f9;
  padding: 1rem;
  border-radius: 4px;
}

.event-title {
  margin: 0 0 0.25rem 0;
  font-size: 1rem;
}

.event-time {
  margin: 0 0 0.75rem 0;
  font-size: 0.85rem;
  color: #666;
}

.event-description {
  margin: 0;
  color: #555;
}

@media (max-width: 900px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .campaign-info-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}

@media (max-width: 500px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
}
</style> 