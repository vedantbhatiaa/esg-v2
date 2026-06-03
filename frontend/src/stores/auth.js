import { defineStore } from "pinia";
import { ref, computed } from "vue";

export const useAuthStore = defineStore("auth", () => {
  const user = ref(JSON.parse(localStorage.getItem("esg_user") || "null"));

  const isLoggedIn  = computed(() => !!user.value);
  const role        = computed(() => user.value?.role || "");
  const companyName = computed(() => user.value?.name || "");
  const companyId   = computed(() => user.value?.id   || "");
  const isDss       = computed(() => role.value === "dss");
  const isClient    = computed(() => role.value === "client");

  async function login(email, password) {
    const res  = await fetch("http://localhost:3001/api/auth/login", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ email, password }),
    });
    if (!res.ok) throw new Error("Invalid credentials");
    const data = await res.json();
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