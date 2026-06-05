<template>
  <div class="min-h-screen flex items-center justify-center p-4"
    style="background: linear-gradient(135deg, #1A1A6B 0%, #0A2240 60%, #0A1628 100%)">

    <!-- Background pattern -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-40 -right-40 w-96 h-96 rounded-full opacity-10"
        style="background: radial-gradient(circle, #C8102E, transparent)"></div>
      <div class="absolute -bottom-40 -left-40 w-96 h-96 rounded-full opacity-10"
        style="background: radial-gradient(circle, #16A34A, transparent)"></div>
    </div>

    <!-- Card -->
    <div class="relative w-full max-w-sm"
      style="animation: tipFadeIn 350ms ease-out both">
      <div class="bg-[#F4F5F7] rounded-2xl p-8 shadow-2xl w-full">

        <!-- dss+ logo -->
        <div class="mb-7">
          <div class="flex items-center gap-2 mb-1">
            <span class="text-[#E31E24] font-black text-[24px] tracking-tight leading-none">dss+</span>
          </div>
          <div class="text-[9.5px] text-[#94A3B8] font-semibold tracking-[0.28em] uppercase">
            PROTECT · TRANSFORM · SUSTAIN
          </div>
          <div class="mt-3 h-px bg-[#E2E8F0]"></div>
          <div class="text-[11px] text-[#64748B] mt-2.5 font-medium">
            TIP ESG Platform · Tire Industry Project
          </div>
        </div>

        <!-- Role tabs -->
        <div class="flex rounded-xl bg-[#E8E9ED] p-1 gap-1 mb-6">
          <button v-for="r in ROLES" :key="r.key" @click="switchRole(r.key)"
            class="flex-1 py-2.5 rounded-lg text-[12px] font-semibold transition-all duration-200 flex items-center justify-center gap-1.5"
            :class="role === r.key
              ? 'bg-white text-[#E31E24] shadow-sm'
              : 'text-[#94A3B8] hover:text-[#64748B]'">
            <span v-if="role === r.key" class="w-2 h-2 rounded-full bg-[#E31E24]"></span>
            {{ r.label }}
          </button>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-[10px] font-bold text-[#64748B] uppercase tracking-[0.08em] mb-1.5">
              Email Address
            </label>
            <input v-model="email" type="email" required autocomplete="email"
              class="w-full h-10 px-3 rounded-lg border border-[#D1D5DB] bg-white text-[13px]
                     text-[#0F172A] focus:outline-none focus:ring-2 focus:ring-[#E31E24]/20
                     focus:border-[#E31E24] transition-colors placeholder:text-[#CBD5E1]" />
          </div>
          <div>
            <label class="block text-[10px] font-bold text-[#64748B] uppercase tracking-[0.08em] mb-1.5">
              Password
            </label>
            <div class="relative">
              <input v-model="password" :type="showPw ? 'text' : 'password'" required
                class="w-full h-10 px-3 pr-10 rounded-lg border border-[#D1D5DB] bg-white text-[13px]
                       text-[#0F172A] focus:outline-none focus:ring-2 focus:ring-[#E31E24]/20
                       focus:border-[#E31E24] transition-colors" />
              <button type="button" @click="showPw = !showPw"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-[#94A3B8] hover:text-[#64748B] text-base">
                {{ showPw ? '🙈' : '👁' }}
              </button>
            </div>
          </div>

          <p v-if="error" class="text-[11px] text-red-500 text-center bg-red-50 rounded-lg py-2 px-3">
            {{ error }}
          </p>

          <button type="submit" :disabled="loading"
            class="w-full h-11 text-white rounded-xl font-semibold text-[13px] transition-all duration-200
                   hover:opacity-90 active:scale-[.98] disabled:opacity-50 disabled:cursor-not-allowed"
            style="background: #0A2240">
            <span v-if="loading" class="inline-flex items-center gap-2">
              <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              Signing in…
            </span>
            <span v-else>Sign in to workspace</span>
          </button>
        </form>

        <!-- Demo credentials -->
        <div class="mt-5 pt-4 border-t border-[#E2E8F0]">
          <p class="text-[10px] text-[#94A3B8] text-center leading-relaxed">
            Demo: <span class="text-[#64748B]">verdatyres@tip-reporting.com</span> (Client)<br>
            <span class="text-[#64748B]">employee@consultdss.com</span> (dss+)<br>
            Password: <strong class="text-[#0F172A]">demo1234</strong>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

const auth   = useAuthStore()
const router = useRouter()

const ROLES  = [{ key:'client', label:'TIP Client Company' }, { key:'dss', label:'dss+ Analyst' }]
const EMAILS = { client:'verdatyres@tip-reporting.com', dss:'employee@consultdss.com' }

const role     = ref('client')
const email    = ref(EMAILS.client)
const password = ref('demo1234')
const showPw   = ref(false)
const loading  = ref(false)
const error    = ref('')

function switchRole(r) { role.value = r; email.value = EMAILS[r]; error.value = '' }

async function handleLogin() {
  loading.value = true; error.value = ''
  try {
    await auth.login(email.value, password.value)
    router.push('/home')
  } catch(e) {
    error.value = 'Invalid email or password. Check the Python & Node services are running.'
  } finally { loading.value = false }
}
</script>