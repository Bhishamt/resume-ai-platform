import api from "./api";

const atsService = {
  async analyzeResume(resumeId) {
    const response = await api.post(`/analysis/${resumeId}`);
    return response.data;
  },

  async getAnalyses() {
    const response = await api.get("/analysis");
    return response.data;
  },

  async getAnalysisById(id) {
    const response = await api.get(`/analysis/${id}`);
    return response.data;
  },

  async deleteAnalysis(id) {
    const response = await api.delete(`/analysis/${id}`);
    return response.data;
  },
};

export default atsService;
