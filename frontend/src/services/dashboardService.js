import api from "./api";

const dashboardService = {
  async getDashboard() {
    const response = await api.get("/dashboard");
    return response.data;
  },

  async getStats() {
    const response = await api.get("/dashboard/stats");
    return response.data;
  },

  async getTrends() {
    const response = await api.get("/dashboard/trends");
    return response.data;
  },

  async getSkills() {
    const response = await api.get("/dashboard/skills");
    return response.data;
  },

  async getRecommendations() {
    const response = await api.get("/dashboard/recommendations");
    return response.data;
  },

  async updatePreferences(preferences) {
    const response = await api.put("/dashboard/preferences", preferences);
    return response.data;
  },
};

export default dashboardService;
