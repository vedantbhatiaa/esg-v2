<template>
  <div id="app">
    <template v-if="isPublicRoute">
      <router-view />
    </template>

    <template v-else>
      <div style="display:flex; height:100vh; overflow:hidden;">
        <!-- Sidebar -->
        <aside style="width:176px; background:#0A2240; display:flex; flex-direction:column; flex-shrink:0; height:100vh; overflow-y:auto;">
          <div style="padding:16px 16px 12px; border-bottom:1px solid #1a3560;">
            <div style="color:white; font-weight:900; font-size:15px;">TIP ESG Platform</div>
            <div style="color:#64748B; font-size:10px; margin-top:2px;">dss+ · Tire Industry Project</div>
          </div>
          <div style="margin:12px 8px 4px; background:#1a3560; border-radius:8px; padding:8px 12px;">
            <div style="color:#64748B; font-size:9px; text-transform:uppercase; letter-spacing:0.05em;">YOUR COMPANY</div>
            <div style="color:white; font-size:12px; font-weight:600; margin-top:2px;">{{ auth.companyName }}</div>
          </div>
          <nav style="flex:1; padding:8px; display:flex; flex-direction:column; gap:2px;">
            <router-link
              v-for="item in navItems" :key="item.to" :to="item.to"
              style="display:block; padding:8px 12px; border-radius:8px; font-size:12px; font-weight:500; text-decoration:none; transition:background 0.15s;"
              :style="isActive(item.to)
                ? 'background:#1a3560; color:white;'
                : 'color:#94A3B8;'"
              @mouseenter="e => { if(!isActive(item.to)) e.target.style.color='white' }"
              @mouseleave="e => { if(!isActive(item.to)) e.target.style.color='#94A3B8' }">
              {{ item.label }}
            </router-link>
          </nav>
          <div style="border-top:1px solid #1a3560; padding:12px 16px;">
            <div style="display:flex; align-items:center; gap:8px;">
              <div style="width:28px; height:28px; border-radius:50%; background:#16A34A; display:flex; align-items:center; justify-content:center; color:white; font-size:11px; font-weight:700; flex-shrink:0;">
                {{ initial }}
              </div>
              <div>
                <div style="color:white; font-size:11px; font-weight:600;">{{ auth.companyName?.split(' ')[0] }}</div>
                <div style="color:#64748B; font-size:9px;">{{ auth.isDss ? 'dss+ Analyst' : 'Client' }}</div>
              </div>
            </div>
            <button @click="logout"
              style="margin-top:8px; width:100%; color:#64748B; font-size:11px; background:none; border:none; cursor:pointer; text-align:left; padding:0;">
              Sign out
            </button>
          </div>
        </aside>

        <!-- Main -->
        <div style="flex:1; display:flex; flex-direction:column; overflow:hidden;">
          <header style="height:48px; background:#0A2240; display:flex; align-items:center; justify-content:space-between; padding:0 24px; flex-shrink:0;">
            <span style="color:#E31E24; font-weight:900; font-size:17px;">TIP ESG Platform</span>
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
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

const auth   = useAuthStore()
const route  = useRoute()
const router = useRouter()

const isPublicRoute = computed(() => route.meta?.public)
const initial       = computed(() => (auth.companyName || 'U')[0].toUpperCase())

const CLIENT_NAV = [
  { to: '/home',       label: 'Home' },
  { to: '/dashboard',  label: 'My Dashboard' },
  { to: '/my-records', label: 'My Records' },
  { to: '/benchmarks', label: 'Benchmarks' },
  { to: '/reports',    label: 'Reports' },
  { to: '/entry',      label: 'Submit Data' },
  { to: '/settings',   label: 'Settings' },
]
const DSS_NAV = [
  { to: '/portfolio',    label: 'Portfolio' },
  { to: '/company-data', label: 'Company Data' },
  { to: '/verification', label: 'Verification Queue' },
  { to: '/analysis',     label: 'Analysis' },
  { to: '/benchmarks',   label: 'Benchmarks' },
  { to: '/reports',      label: 'Sector Reports' },
  { to: '/admin',        label: 'Admin' },
  { to: '/settings',     label: 'Settings' },
]

const navItems = computed(() => auth.isDss ? DSS_NAV : CLIENT_NAV)

function isActive(to) {
  return route.path === to || route.path.startsWith(to + '/')
}

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<style>
.fade-enter-active, .fade-leave-active { transition: opacity 200ms ease; }
.fade-enter-from, .fade-leave-to       { opacity: 0; }
</style>