import { defineStore } from "pinia";
import { ref, computed } from "vue";

export const useAuthStore = defineStore("auth", () => {
  const user = ref(JSON.parse(localStorage.getItem("esg_user") || "null"));

  const isLoggedIn  = computed(() => !!user.value);
  const role        = computed(() => user.value?.role || null);
  const companyId   = computed(() => user.value?.company_id || null);
  const companyName = computed(() => user.value?.company_name || null);
  const displayName = computed(() => user.value?.name || null);

  // Local-only auth — no backend needed yet
  // Replace with real auth (Azure AD / Entra ID) when ready
  const DEMO_USERS = [
    { email: "verdatyres@tip.com",    password: "tip2024", role: "client", company_id: "verdatyres",   company_name: "VerdaTyres Corp",  name: "VerdaTyres Coordinator" },
    { email: "alphatread@tip.com",    password: "tip2024", role: "client", company_id: "alphatread",   company_name: "AlphaTread Ltd",   name: "AlphaTread Coordinator" },
    { email: "analyst@consultdss.com", password: "dss2024", role: "dss",  company_id: null,           company_name: null,               name: "Sarah Analyst" },
    { email: "admin@consultdss.com",  password: "dss2024", role: "dss",  company_id: null,           company_name: null,               name: "Admin User" },
  ];

  function login(email, password) {
    const found = DEMO_USERS.find(
      (u) => u.email === email.toLowerCase() && u.password === password
    );
    if (!found) return { success: false, error: "Invalid credentials" };
    user.value = { ...found };
    localStorage.setItem("esg_user", JSON.stringify(user.value));
    return { success: true };
  }

  function logout() {
    user.value = null;
    localStorage.removeItem("esg_user");
  }

  return { user, isLoggedIn, role, companyId, companyName, displayName, login, logout };
});
