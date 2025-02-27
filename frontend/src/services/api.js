import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const feedService = {
  getAll: async () => {
    const response = await api.get("/feeds");
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/feeds/${id}`);
    return response.data;
  },

  create: async (feed) => {
    const response = await api.post("/feeds", feed);
    return response.data;
  },

  update: async (id, feed) => {
    const response = await api.put(`/feeds/${id}`, feed);
    return response.data;
  },

  delete: async (id) => {
    const response = await api.delete(`/feeds/${id}`);
    return response.data;
  },

  refresh: async (feedId = null) => {
    const url = feedId ? `/feeds/refresh?feed_id=${feedId}` : "/feeds/refresh";
    const response = await api.post(url);
    return response.data;
  },
};

export const articleService = {
  getAll: async (params = {}) => {
    const response = await api.get("/articles", { params });
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/articles/${id}`);
    return response.data;
  },

  markAsRead: async (id, read = true) => {
    const response = await api.put(`/articles/${id}/read?read=${read}`);
    return response.data;
  },

  getFullContent: async (id) => {
    const response = await api.get(`/articles/${id}/full-content`);
    return response.data;
  },
};

export const syncService = {
  getSyncKey: async () => {
    const response = await api.get("/sync/key");
    return response.data.sync_key;
  },

  getSyncData: async (syncKey) => {
    const response = await api.get(`/sync/${syncKey}`);
    return response.data;
  },

  updateSyncData: async (syncKey, data) => {
    const response = await api.post(`/sync/${syncKey}`, data);
    return response.data;
  },

  exportFeeds: async () => {
    const response = await api.get("/export");
    return response.data;
  },

  importFeeds: async (data) => {
    const response = await api.post("/import", { data });
    return response.data;
  },
};

export default {
  feed: feedService,
  article: articleService,
  sync: syncService,
};
