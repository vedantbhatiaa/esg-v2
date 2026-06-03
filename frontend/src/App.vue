<template>
  <div id="app" class="min-h-screen bg-[#F4F5F7]">
    <!-- Public pages (login) — no chrome -->
    <template v-if="isPublicRoute">
      <router-view />
    </template>

    <!-- Authenticated shell -->
    <template v-else>
      <div class="flex h-screen overflow-hidden">
        <!-- Sidebar -->
        <Sidebar />

        <!-- Main content -->
        <div class="flex-1 flex flex-col overflow-hidden">
          <!-- Top bar -->
          <div class="h-14 bg-[#0A2240] flex items-center justify-between px-6 flex-shrink-0">
            <div class="flex items-center gap-2">
              <span class="text-[#E31E24] font-black text-[18px]">TIP ESG Platform</span>
            </div>
            <div class="flex items-center gap-4">
              <span class="text-[11px] text-[#94A3B8]">{{ auth.companyName }}</span>
              <button @click="logout"
                class="text-[11px] text-[#64748B] hover:text-white transition-colors">
                Sign out
              </button>
            </div>
          </div>

          <!-- Page content -->
          <main class="flex-1 overflow-y-auto p-6">
            <router-view v-slot="{ Component, route }">
              <transition name="fade" mode="out-in">
                <component :is="Component" :key="route.path" />
              </transition>
            </router-view>
          </main>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed }     from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import Sidebar          from '@/components/Sidebar.vue'

const auth   = useAuthStore()
const route  = useRoute()
const router = useRouter()

const isPublicRoute = computed(() => route.meta.public)

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<style>
.fade-enter-active, .fade-leave-active { transition: opacity 200ms ease; }
.fade-enter-from, .fade-leave-to       { opacity: 0; }
</style>
