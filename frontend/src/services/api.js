import axios from "axios";

const API_BASE_URL = "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 15000,
});

// Request interceptor: attach Bearer token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: handle 401 with token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and we haven't already retried, attempt token refresh
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      originalRequest.url !== "/auth/login" &&
      originalRequest.url !== "/auth/refresh"
    ) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem("refresh_token");
      if (!refreshToken) {
        // No refresh token available — force logout
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
        return Promise.reject(error);
      }

      try {
        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const { access_token, refresh_token: newRefreshToken } =
          response.data.data;

        localStorage.setItem("access_token", access_token);
        localStorage.setItem("refresh_token", newRefreshToken);

        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed — force logout
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }

    // Network errors (offline)
    if (!error.response) {
      console.error("Network Error: Please check your internet connection.");
      window.dispatchEvent(new CustomEvent('app-error', { 
        detail: { message: 'Network error. Please check your connection and try again.' } 
      }));
    } 
    // Server errors (500+)
    else if (error.response.status >= 500) {
      console.error("Server Error:", error.response.status);
      window.dispatchEvent(new CustomEvent('app-error', { 
        detail: { message: 'The server encountered an unexpected condition. Our team has been notified.' } 
      }));
    }

    return Promise.reject(error);
  }
);

export default api;
