import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1",
  headers: { "Content-Type": "application/json" },
  timeout: 15000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("refund_access_token");
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && !String(error.config?.url ?? "").includes("/auth/")) {
      localStorage.removeItem("refund_access_token");
      localStorage.removeItem("refund_user");
      window.location.assign("/login");
    }
    return Promise.reject(error);
  }
);

export default api;
