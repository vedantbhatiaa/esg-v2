<template>
  <aside class="w-44 bg-[#0A2240] flex flex-col flex-shrink-0 h-full">
    <!-- Brand -->
    <div class="px-4 py-4 border-b border-[#1a3560]">
      <div class="text-white font-black text-[15px]">TIP ESG Platform</div>
      <div class="text-[10px] text-[#64748B] mt-0.5">dss+ · Tire Industry Project</div>
    </div>

    <!-- Company chip -->
    <div class="mx-3 mt-3 mb-1 bg-[#1a3560] rounded-lg px-3 py-2">
      <div class="text-[9px] text-[#64748B] uppercase tracking-wider mb-0.5">YOUR COMPANY</div>
      <div class="text-[12px] font-semibold text-white truncate">{{ auth.companyName }}</div>
    </div>

    <!-- Nav items -->
    <nav class="flex-1 px-2 py-2 space-y-0.5 overflow-y-auto">
      <!-- Client nav -->
      <template v-if="auth.isClient">
        <NavItem v-for="item in CLIENT_NAV" :key="item.to" v-bind="item" />
      </template>

      <!-- DSS+ nav -->
      <template v-if="auth.isDss">
        <NavItem v-for="item in DSS_NAV" :key="item.to" v-bind="item" />
      </template>
    </nav>

    <!-- User info -->
    <div class="border-t border-[#1a3560] px-4 py-3">
      <div class="flex items-center gap-2">
        <div class="w-7 h-7 rounded-full bg-[#16A34A] flex items-center justify-center
                    text-white text-[11px] font-bold">
          {{ initial }}
        </div>
        <div>
          <div class="text-[11px] font-semibold text-white">{{ auth.companyName?.split(' ')[0] }}</div>
          <div class="text-[9px] text-[#64748B]">{{ auth.isDss ? 'dss+ Analyst' : `Client · ${auth.companyName}` }}</div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed }     from 'vue'
import { useRoute }     from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

const auth  = useAuthStore()
const route = useRoute()

const initial = computed(() => auth.companyName?.[0] || 'U')

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
</script>

<!-- NavItem as local sub-component -->
<script>
import { defineComponent, h }  from 'vue'
import { RouterLink, useRoute } from 'vue-router'

export const NavItem = defineComponent({
  props: { to: String, label: String },
  setup(props) {
    const route = useRoute()
    return () => h(RouterLink, { to: props.to, class: [
      'flex items-center px-3 py-2 rounded-lg text-[12px] font-medium transition-colors w-full',
      route.path === props.to || route.path.startsWith(props.to + '/')
        ? 'bg-[#1a3560] text-white'
        : 'text-[#94A3B8] hover:text-white hover:bg-[#142a50]',
    ] }, () => props.label)
  }
})
</script>
