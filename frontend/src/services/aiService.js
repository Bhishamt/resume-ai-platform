import api from "./api";

const aiService = {
  async reviewResume(resumeId, analysisId = null) {
    const response = await api.post("/ai/review", {
      resume_id: resumeId,
      analysis_id: analysisId,
    });
    return response.data;
  },

  async generateCoverLetter(resumeId, payload = {}) {
    const response = await api.post("/ai/cover-letter", {
      resume_id: resumeId,
      job_description_id: payload.jobDescriptionId || null,
      company_name: payload.companyName || null,
      job_title: payload.jobTitle || null,
      job_text: payload.jobText || null,
    });
    return response.data;
  },

  async improveSummary(resumeId) {
    const response = await api.post("/ai/improve-summary", {
      resume_id: resumeId,
    });
    return response.data;
  },

  async improveProjects(resumeId) {
    const response = await api.post("/ai/improve-projects", {
      resume_id: resumeId,
    });
    return response.data;
  },

  async prepareInterview(resumeId, jobDescriptionId = null) {
    const response = await api.post("/ai/interview", {
      resume_id: resumeId,
      job_description_id: jobDescriptionId,
    });
    return response.data;
  },

  async suggestCareer(resumeId) {
    const response = await api.post("/ai/career", {
      resume_id: resumeId,
    });
    return response.data;
  },

  async getHistory() {
    const response = await api.get("/ai/history");
    return response.data;
  },

  async deleteHistory(id) {
    const response = await api.delete(`/ai/history/${id}`);
    return response.data;
  },
};

export default aiService;
