<template>
  <div class="min-h-screen bg-[#1A1A6B] flex items-center justify-center p-4">
    <div class="bg-[#F4F5F7] rounded-2xl p-8 w-full max-w-sm shadow-2xl">
      <!-- Logo -->
      <div class="mb-6">
        <span class="text-[#E31E24] font-black text-[22px] tracking-tight">dss+</span>
        <div class="text-[9px] text-[#94A3B8] font-semibold tracking-[0.25em] uppercase mt-0.5">
          PROTECT · TRANSFORM · SUSTAIN
        </div>
      </div>

      <!-- Role tabs -->
      <div class="flex rounded-lg bg-[#E8E9ED] p-1 gap-1 mb-6">
        <button v-for="r in ROLES" :key="r.key" @click="switchRole(r.key)"
          class="flex-1 py-2 rounded-md text-[12px] font-semibold transition-all flex items-center justify-center gap-1.5"
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
          <label class="block text-[10px] font-bold text-[#64748B] uppercase tracking-wider mb-1.5">
            EMAIL ADDRESS
          </label>
          <input v-model="email" type="email" required autocomplete="email"
            class="w-full h-10 px-3 rounded-lg border border-[#D1D5DB] bg-white text-[13px]
                   text-[#0F172A] focus:outline-none focus:ring-2 focus:ring-[#E31E24]/20
                   focus:border-[#E31E24] transition-colors" />
        </div>
        <div>
          <label class="block text-[10px] font-bold text-[#64748B] uppercase tracking-wider mb-1.5">
            PASSWORD
          </label>
          <div class="relative">
            <input v-model="password" :type="showPw ? 'text' : 'password'" required
              class="w-full h-10 px-3 pr-10 rounded-lg border border-[#D1D5DB] bg-white text-[13px]
                     text-[#0F172A] focus:outline-none focus:ring-2 focus:ring-[#E31E24]/20
                     focus:border-[#E31E24] transition-colors" />
            <button type="button" @click="showPw = !showPw"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-[#94A3B8] hover:text-[#64748B]">
              {{ showPw ? '🙈' : '👁' }}
            </button>
          </div>
        </div>

        <p v-if="error" class="text-[11px] text-red-500 text-center">{{ error }}</p>

        <button type="submit" :disabled="loading"
          class="w-full h-11 bg-[#0A2240] hover:bg-[#1a3560] text-white rounded-lg font-semibold
                 text-[13px] transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
          {{ loading ? 'Signing in…' : 'Sign in to workspace' }}
        </button>
      </form>

      <p class="text-center text-[10px] text-[#94A3B8] mt-5">
        Demo: verdatyres@tip-reporting.com (Client) · employee@consultdss.com (dss+)
        <br>Password: <strong>demo1234</strong>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter }    from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

const auth   = useAuthStore()
const router = useRouter()

const ROLES = [
  { key: 'client', label: 'TIP Client Company' },
  { key: 'dss',    label: 'dss+ Analyst' },
]

const EMAILS = { client: 'verdatyres@tip-reporting.com', dss: 'employee@consultdss.com' }

const role     = ref('client')
const email    = ref(EMAILS.client)
const password = ref('demo1234')
const showPw   = ref(false)
const loading  = ref(false)
const error    = ref('')

function switchRole(r) {
  role.value  = r
  email.value = EMAILS[r]
  error.value = ''
}

async function handleLogin() {
  loading.value = true
  error.value   = ''
  try {
    await auth.login(email.value, password.value)
    router.push('/home')
  } catch (e) {
    error.value = 'Invalid email or password'
  } finally {
    loading.value = false
  }
}
</script>
