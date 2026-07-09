import api from "./api";

const authService = {
  async register(data) {
    const response = await api.post("/auth/register", data);
    return response.data;
  },

  async login(data) {
    const response = await api.post("/auth/login", data);
    const { access_token, refresh_token } = response.data.data;
    localStorage.setItem("access_token", access_token);
    localStorage.setItem("refresh_token", refresh_token);
    return response.data;
  },

  logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  },

  async refreshToken() {
    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) throw new Error("No refresh token available.");
    const response = await api.post("/auth/refresh", {
      refresh_token: refreshToken,
    });
    const { access_token, refresh_token: newRefreshToken } = response.data.data;
    localStorage.setItem("access_token", access_token);
    localStorage.setItem("refresh_token", newRefreshToken);
    return response.data;
  },

  async forgotPassword(email) {
    const response = await api.post("/auth/forgot-password", { email });
    return response.data;
  },

  async resetPassword(data) {
    const response = await api.post("/auth/reset-password", data);
    return response.data;
  },

  async getProfile() {
    const response = await api.get("/users/profile");
    return response.data;
  },

  async updateProfile(data) {
    const response = await api.put("/users/profile", data);
    return response.data;
  },
};

export default authService;
