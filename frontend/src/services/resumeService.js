import api from "./api";

const resumeService = {
  async uploadResume(file, title = null) {
    const formData = new FormData();
    formData.append("file", file);
    if (title) {
      formData.append("title", title);
    }
    const response = await api.post("/resumes/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  async getResumes(page = 1, limit = 10) {
    const response = await api.get("/resumes", {
      params: { page, limit },
    });
    return response.data;
  },

  async getResumeById(id) {
    const response = await api.get(`/resumes/${id}`);
    return response.data;
  },

  async deleteResume(id) {
    const response = await api.delete(`/resumes/${id}`);
    return response.data;
  },

  async updateResume(id, title) {
    const response = await api.put(`/resumes/${id}`, { title });
    return response.data;
  },

  async replaceResume(id, file) {
    const formData = new FormData();
    formData.append("file", file);
    const response = await api.post(`/resumes/${id}/replace`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  async getUploadHistory() {
    const response = await api.get("/resumes/history");
    return response.data;
  },
};

export default resumeService;
