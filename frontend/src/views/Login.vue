<template>
  <div class="h-full flex items-center justify-center"
    style="background: linear-gradient(135deg, #080838 0%, #0D0D6B 45%, #1a1a8c 80%, #0a0a50 100%)">

    <div class="bg-[#F0F1F7] rounded-2xl w-[420px] px-10 py-10">
      <!-- Logo -->
      <div class="font-head text-3xl font-black tracking-tight mb-1">
        <span class="text-dss">dss</span><span class="text-[#9B9B9B]">+</span>
        <span class="text-[#1E3A8A] italic text-2xl font-semibold ml-1">360</span>
      </div>
      <div class="text-[10px] text-gray-400 uppercase tracking-wider mb-7">
        Protect · Transform · Sustain
      </div>

      <!-- Role tabs -->
      <div class="grid grid-cols-2 gap-1.5 bg-gray-200 rounded-lg p-1 mb-5">
        <button
          v-for="r in roles" :key="r.value"
          @click="selectedRole = r.value"
          class="py-2 rounded-md text-xs font-medium transition-all duration-150"
          :class="selectedRole === r.value
            ? 'bg-white text-gray-900 font-semibold shadow-sm'
            : 'text-gray-400 hover:text-gray-600'"
        >
          {{ r.label }}
        </button>
      </div>

      <!-- Form -->
      <label class="text-[11px] font-semibold text-gray-400 uppercase tracking-wide block mb-1">Email address</label>
      <input
        v-model="email"
        type="email"
        :placeholder="selectedRole === 'client' ? 'verdatyres@tip.com' : 'analyst@consultdss.com'"
        class="w-full h-10 border-[1.5px] border-gray-200 rounded-lg px-3 text-sm mb-3 focus:outline-none focus:border-[#1E3A8A] bg-white"
        @keyup.enter="handleLogin"
      />
      <label class="text-[11px] font-semibold text-gray-400 uppercase tracking-wide block mb-1">Password</label>
      <input
        v-model="password"
        type="password"
        placeholder="Enter password"
        class="w-full h-10 border-[1.5px] border-gray-200 rounded-lg px-3 text-sm mb-1 focus:outline-none focus:border-[#1E3A8A] bg-white"
        @keyup.enter="handleLogin"
      />

      <p v-if="error" class="text-xs text-red-600 mb-2">{{ error }}</p>

      <button
        @click="handleLogin"
        :disabled="loading"
        class="w-full h-10 bg-navy text-white rounded-lg text-sm font-semibold font-head mt-3 hover:bg-[#1a1a5a] transition-colors disabled:opacity-50"
      >
        {{ loading ? "Signing in…" : "Sign in to workspace" }}
      </button>

      <!-- Demo hint -->
      <div class="mt-4 text-center text-[11px] text-gray-400 leading-relaxed">
        <strong>Demo credentials:</strong><br/>
        Client: verdatyres@tip.com / tip2024<br/>
        Analyst: analyst@consultdss.com / dss2024
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth.js";

const auth     = useAuthStore();
const router   = useRouter();
const email    = ref("");
const password = ref("");
const error    = ref("");
const loading  = ref(false);
const selectedRole = ref("client");

const roles = [
  { value: "client", label: "TIP Client Company" },
  { value: "dss",    label: "dss+ Analyst" },
];

// Pre-fill email hint when role switches
watch(selectedRole, (r) => {
  email.value    = r === "client" ? "verdatyres@tip.com" : "analyst@consultdss.com";
  password.value = r === "client" ? "tip2024" : "dss2024";
});

async function handleLogin() {
  error.value   = "";
  loading.value = true;
  const result  = auth.login(email.value, password.value);
  loading.value = false;
  if (result.success) {
    router.push("/dashboard");
  } else {
    error.value = result.error;
  }
}
</script>
