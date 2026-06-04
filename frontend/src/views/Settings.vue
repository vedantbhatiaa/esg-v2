<template>
  <div>
    <div class="mb-5">
      <h2 class="text-xl font-bold text-gray-900">Settings</h2>
      <p class="text-sm text-gray-400 mt-0.5">Account & preferences</p>
    </div>

    <div class="flex border-b border-gray-200 mb-5 gap-1">
      <button v-for="t in tabs" :key="t" @click="activeTab=t"
        class="px-4 py-2 text-sm font-medium border-b-2 transition-colors"
        :class="activeTab===t ? 'border-navy text-navy' : 'border-transparent text-gray-400 hover:text-gray-700'">
        {{ t }}
      </button>
    </div>

    <!-- Account -->
    <div v-if="activeTab==='Account'" class="grid grid-cols-2 gap-5 max-w-2xl">
      <div class="bg-white border border-gray-100 rounded-xl p-5">
        <div class="text-sm font-semibold text-gray-700 mb-3">Profile</div>
        <div class="space-y-3">
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">Display Name</label>
            <input :value="auth.userName" class="w-full h-9 border border-gray-200 rounded-lg px-3 text-sm" readonly />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">Email</label>
            <input :value="auth.userEmail" class="w-full h-9 border border-gray-200 rounded-lg px-3 text-sm bg-gray-50 text-gray-400" readonly />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">Role</label>
            <input :value="auth.isDss ? 'dss+ Analyst (Internal)' : 'Client Company User'" class="w-full h-9 border border-gray-200 rounded-lg px-3 text-sm bg-gray-50 text-gray-400" readonly />
          </div>
          <div v-if="!auth.isDss">
            <label class="block text-xs font-medium text-gray-500 mb-1">Company</label>
            <input :value="auth.companyName" class="w-full h-9 border border-gray-200 rounded-lg px-3 text-sm bg-gray-50 text-gray-400" readonly />
          </div>
        </div>
      </div>
      <div class="bg-white border border-gray-100 rounded-xl p-5">
        <div class="text-sm font-semibold text-gray-700 mb-3">Security</div>
        <div class="space-y-3">
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">Current Password</label>
            <input type="password" v-model="curPw" class="w-full h-9 border border-gray-200 rounded-lg px-3 text-sm" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">New Password</label>
            <input type="password" v-model="newPw" class="w-full h-9 border border-gray-200 rounded-lg px-3 text-sm" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">Confirm Password</label>
            <input type="password" v-model="cfmPw" class="w-full h-9 border border-gray-200 rounded-lg px-3 text-sm" />
          </div>
          <button class="w-full h-9 bg-navy text-white rounded-lg text-sm font-medium hover:opacity-90"
            @click="pwMsg='Password change will be available in the production release.'">
            Change Password
          </button>
          <p v-if="pwMsg" class="text-xs text-blue-600">{{ pwMsg }}</p>
        </div>
      </div>
    </div>

    <!-- Notifications -->
    <div v-if="activeTab==='Notifications'" class="max-w-md bg-white border border-gray-100 rounded-xl p-5">
      <div class="text-sm font-semibold text-gray-700 mb-3">Email Notifications</div>
      <div class="space-y-3">
        <label v-for="n in notifOptions" :key="n.key" class="flex items-center gap-3 cursor-pointer">
          <input type="checkbox" v-model="notifs[n.key]" class="rounded" />
          <span class="text-sm text-gray-600">{{ n.label }}</span>
        </label>
      </div>
      <button class="mt-4 px-4 h-9 bg-navy text-white rounded-lg text-sm font-medium hover:opacity-90">
        Save Preferences
      </button>
    </div>

    <!-- About -->
    <div v-if="activeTab==='About'" class="max-w-md">
      <div class="bg-white border border-gray-100 rounded-xl p-5 space-y-3">
        <div class="flex items-center gap-2">
          <div class="w-2.5 h-2.5 rounded-full bg-green-500"></div>
          <span class="text-sm font-semibold text-gray-700">TIP ESG Platform V2</span>
        </div>
        <div class="text-xs text-gray-500 space-y-1">
          <p>Developed by dss+ · Tire Industry Project (WBCSD)</p>
          <p>Stack: Vue 3 + Node.js + Python Azure Functions</p>
          <p>Methodology: GHG Protocol · TIP KPI definitions v3.1</p>
          <p>Emission factors: IEA 2023 · IPCC 2006 Guidelines</p>
        </div>
        <div class="pt-2 border-t border-gray-100">
          <div class="text-xs text-gray-400">Scope 2 EF: 0.45 T.CO₂/MWh (EU avg)</div>
          <div class="text-xs text-gray-400">Waste tire HV: 36.23 GJ/T</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useAuthStore } from "@/stores/auth.js";
const auth = useAuthStore();
const tabs = ["Account","Notifications","About"];
const activeTab = ref("Account");
const curPw = ref(""); const newPw = ref(""); const cfmPw = ref(""); const pwMsg = ref("");
const notifs = ref({ deadline: true, verif: true, sector: false, benchmark: false });
const notifOptions = [
  { key:"deadline", label:"Submission deadline reminders" },
  { key:"verif",    label:"Verification status updates" },
  { key:"sector",   label:"Sector benchmarks published" },
  { key:"benchmark",label:"New benchmark data available" },
];
</script>