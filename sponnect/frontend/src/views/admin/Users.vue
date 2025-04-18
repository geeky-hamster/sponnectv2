<template>
  <div class="admin-users">
    <h1 class="text-3xl font-bold mb-6">User Management</h1>
    
    <!-- Search and Filter -->
    <div class="bg-white rounded-lg shadow p-4 mb-6">
      <div class="flex flex-wrap gap-4">
        <div class="grow">
          <input 
            type="text" 
            v-model="searchTerm" 
            placeholder="Search users..." 
            class="w-full p-2 border rounded"
            @input="filterUsers"
          />
        </div>
        <div class="flex gap-2">
          <select v-model="roleFilter" class="p-2 border rounded" @change="filterUsers">
            <option value="">All Roles</option>
            <option value="admin">Admin</option>
            <option value="sponsor">Sponsor</option>
            <option value="influencer">Influencer</option>
          </select>
          <select v-model="statusFilter" class="p-2 border rounded" @change="filterUsers">
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="flagged">Flagged</option>
          </select>
        </div>
      </div>
    </div>
    
    <!-- Users Table -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-gray-500">
        Loading users...
      </div>
      
      <div v-else-if="filteredUsers.length === 0" class="p-8 text-center text-gray-500">
        No users found matching your criteria.
      </div>
      
      <table v-else class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              User
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Role
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Email
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Joined
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="user in filteredUsers" :key="user.id">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <div class="flex-shrink-0 h-10 w-10">
                  <img 
                    :src="user.profileImage || '/images/default-avatar.png'" 
                    class="h-10 w-10 rounded-full object-cover"
                    alt="User avatar"
                  >
                </div>
                <div class="ml-4">
                  <div class="text-sm font-medium text-gray-900">{{ user.fullName }}</div>
                  <div class="text-sm text-gray-500" v-if="user.role === 'sponsor'">{{ user.companyName }}</div>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="[
                'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                user.role === 'admin' ? 'bg-purple-100 text-purple-800' : 
                user.role === 'sponsor' ? 'bg-blue-100 text-blue-800' : 
                'bg-green-100 text-green-800'
              ]">
                {{ capitalizeFirst(user.role) }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ user.email }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="[
                'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                user.flagged ? 'bg-red-100 text-red-800' : 
                !user.isActive ? 'bg-gray-100 text-gray-800' : 
                'bg-green-100 text-green-800'
              ]">
                {{ user.flagged ? 'Flagged' : (user.isActive ? 'Active' : 'Inactive') }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ formatDate(user.createdAt) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              <button 
                v-if="user.flagged"
                @click="unflagUser(user.id)"
                class="text-blue-600 hover:text-blue-900 mr-2"
                :disabled="isProcessing"
              >
                Unflag
              </button>
              <button 
                v-else
                @click="flagUser(user.id)"
                class="text-red-600 hover:text-red-900 mr-2"
                :disabled="isProcessing"
              >
                Flag
              </button>
              <button
                v-if="user.isActive"
                @click="deactivateUser(user.id)"
                class="text-gray-600 hover:text-gray-900"
                :disabled="isProcessing"
              >
                Deactivate
              </button>
              <button
                v-else
                @click="activateUser(user.id)"
                class="text-green-600 hover:text-green-900"
                :disabled="isProcessing"
              >
                Activate
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useToast } from 'vue-toastification';

export default {
  name: 'AdminUsers',
  setup() {
    const store = useStore();
    const toast = useToast();
    
    const users = ref([]);
    const filteredUsers = ref([]);
    const loading = ref(true);
    const isProcessing = ref(false);
    
    // Filter state
    const searchTerm = ref('');
    const roleFilter = ref('');
    const statusFilter = ref('');
    
    // Fetch users on component mount
    onMounted(async () => {
      try {
        const response = await store.dispatch('admin/fetchUsers');
        users.value = response;
        filterUsers();
        loading.value = false;
      } catch (error) {
        toast.error('Failed to load users');
        console.error('Error loading users:', error);
        loading.value = false;
      }
    });
    
    // Filter users based on search term and filters
    const filterUsers = () => {
      filteredUsers.value = users.value.filter(user => {
        // Search term filter
        const searchMatch = searchTerm.value === '' || 
          user.fullName.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
          user.email.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
          (user.companyName && user.companyName.toLowerCase().includes(searchTerm.value.toLowerCase()));
        
        // Role filter
        const roleMatch = roleFilter.value === '' || user.role === roleFilter.value;
        
        // Status filter
        const statusMatch = statusFilter.value === '' || 
          (statusFilter.value === 'flagged' && user.flagged) ||
          (statusFilter.value === 'active' && user.isActive && !user.flagged) ||
          (statusFilter.value === 'inactive' && !user.isActive);
        
        return searchMatch && roleMatch && statusMatch;
      });
    };
    
    // User actions
    const flagUser = async (userId) => {
      isProcessing.value = true;
      try {
        await store.dispatch('admin/flagUser', userId);
        // Update local state
        const userIndex = users.value.findIndex(u => u.id === userId);
        if (userIndex !== -1) {
          users.value[userIndex].flagged = true;
          filterUsers();
        }
        toast.success('User has been flagged');
      } catch (error) {
        toast.error('Failed to flag user');
        console.error('Error flagging user:', error);
      } finally {
        isProcessing.value = false;
      }
    };
    
    const unflagUser = async (userId) => {
      isProcessing.value = true;
      try {
        await store.dispatch('admin/unflagUser', userId);
        // Update local state
        const userIndex = users.value.findIndex(u => u.id === userId);
        if (userIndex !== -1) {
          users.value[userIndex].flagged = false;
          filterUsers();
        }
        toast.success('User has been unflagged');
      } catch (error) {
        toast.error('Failed to unflag user');
        console.error('Error unflagging user:', error);
      } finally {
        isProcessing.value = false;
      }
    };
    
    const deactivateUser = async (userId) => {
      isProcessing.value = true;
      try {
        await store.dispatch('admin/deactivateUser', userId);
        // Update local state
        const userIndex = users.value.findIndex(u => u.id === userId);
        if (userIndex !== -1) {
          users.value[userIndex].isActive = false;
          filterUsers();
        }
        toast.success('User has been deactivated');
      } catch (error) {
        toast.error('Failed to deactivate user');
        console.error('Error deactivating user:', error);
      } finally {
        isProcessing.value = false;
      }
    };
    
    const activateUser = async (userId) => {
      isProcessing.value = true;
      try {
        await store.dispatch('admin/activateUser', userId);
        // Update local state
        const userIndex = users.value.findIndex(u => u.id === userId);
        if (userIndex !== -1) {
          users.value[userIndex].isActive = true;
          filterUsers();
        }
        toast.success('User has been activated');
      } catch (error) {
        toast.error('Failed to activate user');
        console.error('Error activating user:', error);
      } finally {
        isProcessing.value = false;
      }
    };
    
    // Helper methods
    const formatDate = (dateString) => {
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
    
    return {
      users,
      filteredUsers,
      loading,
      isProcessing,
      searchTerm,
      roleFilter,
      statusFilter,
      filterUsers,
      flagUser,
      unflagUser,
      deactivateUser,
      activateUser,
      formatDate,
      capitalizeFirst
    };
  }
};
</script>

<style scoped>
.admin-users {
  @apply py-6 px-4 max-w-7xl mx-auto;
}
</style> 