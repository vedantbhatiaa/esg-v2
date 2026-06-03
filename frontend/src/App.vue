<template>
  <div class="h-full">
    <!-- Public pages (Login) -->
    <router-view v-if="!auth.isLoggedIn" />

    <!-- Authenticated shell -->
    <div v-else class="flex h-full">
      <Sidebar />
      <div class="flex-1 flex flex-col overflow-hidden min-w-0">
        <Navbar />
        <main class="flex-1 overflow-y-auto p-5">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from "@/stores/auth.js";
import Sidebar from "@/components/Sidebar.vue";
import Navbar  from "@/components/Navbar.vue";

const auth = useAuthStore();
</script>
