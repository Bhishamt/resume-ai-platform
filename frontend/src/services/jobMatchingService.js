import api from "./api";

const jobMatchingService = {
  async matchJob(payload) {
    const response = await api.post("/job-matching", payload);
    return response.data;
  },

  async getMatches(skip = 0, limit = 100) {
    const response = await api.get(`/job-matching?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  async getMatchById(id) {
    const response = await api.get(`/job-matching/${id}`);
    return response.data;
  },

  async deleteMatch(id) {
    const response = await api.delete(`/job-matching/${id}`);
    return response.data;
  },
};

export default jobMatchingService;
