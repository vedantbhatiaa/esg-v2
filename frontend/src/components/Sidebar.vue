<template>
  <aside class="w-44 bg-[#0A2240] flex flex-col flex-shrink-0 h-full">
    <!-- Brand -->
    <div class="px-4 py-4 border-b border-[#1a3560]">
      <div class="flex items-center gap-2">
        <div class="w-2.5 h-2.5 rounded-full bg-[#16A34A] flex-shrink-0"></div>
        <div>
          <div class="text-white font-black text-[13.5px] leading-tight">TIP ESG Platform</div>
          <div class="text-[9px] text-[#64748B] mt-0.5">dss+ · Tire Industry Project</div>
        </div>
      </div>
    </div>

    <!-- Company chip (client only) -->
    <div v-if="auth.isClient" class="mx-3 mt-3 mb-1 bg-[#1a3560] rounded-lg px-3 py-2">
      <div class="text-[9px] text-[#64748B] uppercase tracking-wider mb-0.5">YOUR COMPANY</div>
      <div class="text-[12px] font-semibold text-white truncate">{{ auth.companyName }}</div>
    </div>

    <!-- Nav items -->
    <nav class="flex-1 px-2 py-2 space-y-0.5 overflow-y-auto">
      <router-link
        v-for="item in navItems" :key="item.to" :to="item.to"
        class="flex items-center gap-2 px-3 py-2 rounded-lg text-[12px] font-medium transition-colors no-underline"
        :class="isActive(item.to)
          ? 'bg-[#16A34A] text-white'
          : 'text-[#94A3B8] hover:text-white hover:bg-[#142a50]'">
        <span class="w-1.5 h-1.5 rounded-full bg-current opacity-60 flex-shrink-0"></span>
        {{ item.label }}
      </router-link>
    </nav>

    <!-- User footer -->
    <div class="border-t border-[#1a3560] px-4 py-3">
      <div class="flex items-center gap-2 mb-2">
        <div class="w-7 h-7 rounded-full bg-[#16A34A] flex items-center justify-center
                    text-white text-[11px] font-bold flex-shrink-0">
          {{ initial }}
        </div>
        <div class="min-w-0">
          <div class="text-[11px] font-semibold text-white truncate">{{ auth.companyName?.split(' ')[0] }}</div>
          <div class="text-[9px] text-[#64748B]">{{ auth.isDss ? 'dss+ Analyst' : 'Client' }}</div>
        </div>
      </div>
      <button @click="signOut"
        class="w-full text-left text-[11px] text-[#64748B] hover:text-white transition-colors bg-transparent border-0 cursor-pointer py-1 px-0">
        Sign out
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed }     from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

const auth   = useAuthStore()
const route  = useRoute()
const router = useRouter()

const initial = computed(() => (auth.companyName || 'U')[0].toUpperCase())

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
  { to: '/readiness',    label: 'AI Assistant' },
  { to: '/admin',        label: 'Admin' },
  { to: '/settings',     label: 'Settings' },
]

const navItems = computed(() => auth.isDss ? DSS_NAV : CLIENT_NAV)

function isActive(to) {
  return route.path === to || route.path.startsWith(to + '/')
}

function signOut() {
  auth.logout()
  router.push('/login')
}
</script>