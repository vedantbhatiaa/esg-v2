<template>
  <div id="app" class="h-full">
    <!-- Public pages (Login etc) -->
    <router-view v-if="isPublicRoute" />

    <!-- Authenticated shell -->
    <div v-else style="display:flex; height:100vh; overflow:hidden;">
      <Sidebar />
      <div style="flex:1; display:flex; flex-direction:column; overflow:hidden;">
        <header style="height:46px; background:#0A2240; display:flex; align-items:center;
                       justify-content:space-between; padding:0 24px; flex-shrink:0;">
          <span style="color:#E31E24; font-weight:900; font-size:16px; letter-spacing:-0.3px;">
            TIP ESG Platform
          </span>
          <span style="color:#64748B; font-size:11px;">{{ auth.companyName }}</span>
        </header>
        <main style="flex:1; overflow-y:auto; padding:24px; background:#F4F5F7;">
          <router-view v-slot="{ Component, route }">
            <transition name="fade" mode="out-in">
              <component :is="Component" :key="route.path" />
            </transition>
          </router-view>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import Sidebar from '@/components/Sidebar.vue'

const auth  = useAuthStore()
const route = useRoute()

const isPublicRoute = computed(() => route.meta?.public)
</script>

<style>
.fade-enter-active, .fade-leave-active { transition: opacity 200ms ease; }
.fade-enter-from, .fade-leave-to       { opacity: 0; }

html, body, #app { height: 100%; margin: 0; }
</style>