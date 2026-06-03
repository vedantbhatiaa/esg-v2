import { defineStore } from "pinia";
import { ref, computed } from "vue";
import api from "@/services/api.js";

export const useAuthStore = defineStore("auth", () => {
  const user = ref(JSON.parse(localStorage.getItem("esg_user") || "null"));

  const isLoggedIn  = computed(() => !!user.value);
  const role        = computed(() => user.value?.role || "");
  const companyName = computed(() => user.value?.name || "");
  const companyId   = computed(() => user.value?.id   || "");
  const isDss       = computed(() => role.value === "dss");
  const isClient    = computed(() => role.value === "client");

  async function login(email, password) {
    const data = await api.login(email, password);
    user.value = data;
    localStorage.setItem("esg_user", JSON.stringify(data));
    return data;
  }

  function logout() {
    user.value = null;
    localStorage.removeItem("esg_user");
  }

  return { user, isLoggedIn, role, companyName, companyId, isDss, isClient, login, logout };
});
