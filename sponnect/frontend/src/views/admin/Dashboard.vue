<!-- Admin Dashboard.vue -->
<template>
  <div class="admin-dashboard">
    <h1 class="text-3xl font-bold mb-6">Admin Dashboard</h1>
    
    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div v-for="(stat, key) in stats" :key="key" class="stat-card bg-white rounded-lg shadow p-6">
        <h3 class="text-gray-500 text-sm uppercase mb-1">{{ stat.label }}</h3>
        <div class="flex items-end">
          <span class="text-3xl font-bold mr-2">{{ stat.value }}</span>
          <span :class="[
            'text-sm',
            stat.change > 0 ? 'text-green-500' : (stat.change < 0 ? 'text-red-500' : 'text-gray-500')
          ]">
            {{ stat.change > 0 ? '+' : '' }}{{ stat.change }}%
          </span>
        </div>
      </div>
    </div>
    
    <!-- Charts Section -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-bold mb-4">User Growth</h2>
        <div class="h-64">
          <LineChart
            v-if="chartData.userGrowth && chartData.userGrowth.labels && chartData.userGrowth.labels.length"
            :chart-data="prepareUserGrowthChart"
            :options="lineChartOptions"
          />
          <div v-else class="h-full flex items-center justify-center text-gray-400">
            No user growth data available.
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-bold mb-4">Campaign Activity</h2>
        <div class="h-64">
          <BarChart
            v-if="chartData.campaignActivity && chartData.campaignActivity.labels && chartData.campaignActivity.labels.length"
            :chart-data="prepareCampaignActivityChart"
            :options="barChartOptions"
          />
          <div v-else class="h-full flex items-center justify-center text-gray-400">
            No campaign activity data available.
          </div>
        </div>
      </div>
    </div>
    
    <!-- Pending Sponsors Section -->
    <div class="bg-white rounded-lg shadow p-6 mb-8">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-bold">Pending Sponsor Approvals</h2>
        <router-link 
          to="/admin/sponsors" 
          class="text-blue-600 hover:text-blue-800 text-sm"
        >
          View All
        </router-link>
      </div>
      
      <div v-if="loadingPendingSponsors" class="py-8 text-center text-gray-500">
        Loading pending sponsors...
      </div>
      
      <div v-else-if="pendingSponsors.length === 0" class="py-8 text-center text-gray-500">
        No pending sponsor approvals at this time.
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Company
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Contact
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Registered
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="sponsor in pendingSponsors.slice(0, 5)" :key="sponsor.id">
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
                    <div class="text-sm text-gray-500">{{ sponsor.website }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ sponsor.fullName }}</div>
                <div class="text-sm text-gray-500">{{ sponsor.email }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(sponsor.createdAt) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
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
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import LineChart from '@/components/charts/LineChart.vue';
import BarChart from '@/components/charts/BarChart.vue';

export default {
  name: 'AdminDashboard',
  components: {
    LineChart,
    BarChart
  },
  setup() {
    console.log('AdminDashboard component loaded');
    const store = useStore();
    const router = useRouter();
    const toast = useToast();
    const isProcessing = ref(false);
    const loadingPendingSponsors = ref(true);
    
    // Fetch data on component mount
    onMounted(async () => {
      try {
        console.log('Fetching admin stats...');
        await store.dispatch('admin/fetchAdminStats');
        console.log('Fetching pending sponsors...');
        await store.dispatch('admin/fetchPendingSponsors');
        loadingPendingSponsors.value = false;
        console.log('Fetching user growth data...');
        await store.dispatch('admin/fetchUserGrowthChart');
        console.log('Fetching campaign activity data...');
        await store.dispatch('admin/fetchCampaignActivityChart');
      } catch (error) {
        toast.error('Failed to load dashboard data');
        console.error('Dashboard data loading error:', error);
      }
    });
    
    // Computed properties for accessing store data
    const stats = computed(() => {
      const statsData = store.getters['admin/adminStats'];
      return {
        users: {
          label: 'Total Users',
          value: statsData.total_users || 0,
          change: 0
        },
        sponsors: {
          label: 'Active Sponsors',
          value: statsData.active_sponsors || 0, // Updated to match API response
          change: 0 // Placeholder since `sponsorGrowthRate` is not provided in the API response
        },
        campaigns: {
          label: 'Public Campaigns',
          value: statsData.public_campaigns || 0, // Updated to match API response
          change: 0 // Placeholder since `campaignGrowthRate` is not provided in the API response
        },
        adRequests: {
          label: 'Ad Requests',
          value: Object.values(statsData.ad_requests_by_status || {}).reduce((sum, count) => sum + count, 0), // Sum of all ad request statuses
          change: 0 // Placeholder since `adRequestGrowthRate` is not provided in the API response
        }
      };
    });
    
    const pendingSponsors = computed(() => store.getters['admin/pendingSponsors']);
    
    const chartData = computed(() => ({
      userGrowth: store.getters['admin/chartData'].userGrowth || [],
      campaignActivity: store.getters['admin/chartData'].campaignActivity || []
    }));
    console.log('Chart Data:', chartData.value);
    
    // Chart configurations
    const lineChartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            precision: 0
          }
        }
      }
    };
    
    const barChartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            precision: 0
          }
        }
      }
    };
    
    // Format chart data
    const prepareUserGrowthChart = computed(() => {
      const data = chartData.value.userGrowth;
      return {
        labels: data.map(item => item.label),
        datasets: [
          {
            label: 'New Users',
            data: data.map(item => item.value),
            borderColor: '#3B82F6',
            backgroundColor: 'rgba(59, 130, 246, 0.2)',
            tension: 0.3,
            fill: true
          }
        ]
      };
    });
    
    const prepareCampaignActivityChart = computed(() => {
      const data = chartData.value.campaignActivity;
      return {
        labels: data.map(item => item.label),
        datasets: [
          {
            label: 'Campaigns',
            data: data.map(item => item.value),
            backgroundColor: 'rgba(59, 130, 246, 0.6)',
            borderColor: '#3B82F6',
            borderWidth: 1
          }
        ]
      };
    });
    
    // Methods
    const formatDate = (dateString) => {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      }).format(date);
    };
    
    const approveSponsor = async (sponsorId) => {
      isProcessing.value = true;
      try {
        await store.dispatch('admin/approveSponsor', sponsorId);
        toast.success('Sponsor approved successfully');
      } catch (error) {
        toast.error('Failed to approve sponsor');
        console.error('Sponsor approval error:', error);
      } finally {
        isProcessing.value = false;
      }
    };
    
    const rejectSponsor = async (sponsorId) => {
      isProcessing.value = true;
      try {
        await store.dispatch('admin/rejectSponsor', sponsorId);
        toast.success('Sponsor rejected');
      } catch (error) {
        toast.error('Failed to reject sponsor');
        console.error('Sponsor rejection error:', error);
      } finally {
        isProcessing.value = false;
      }
    };
    
    return {
      stats,
      router,
      pendingSponsors,
      chartData,
      lineChartOptions,
      barChartOptions,
      prepareUserGrowthChart,
      prepareCampaignActivityChart,
      formatDate,
      approveSponsor,
      rejectSponsor,
      isProcessing,
      loadingPendingSponsors
    };
  }
};
</script>

<style scoped>
.admin-dashboard {
  @apply py-6 px-4 max-w-7xl mx-auto;
}

.stat-card {
  @apply transition-all duration-300 hover:shadow-lg;
}
</style> 