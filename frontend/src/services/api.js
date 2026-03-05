import axios from "axios";

const API = axios.create({
    baseURL: "http://localhost:8000",
});

API.interceptors.request.use((config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export const loginUser = (username, password) =>
    API.post("/auth/login", new URLSearchParams({ username, password }), {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });

export const registerUser = (username, email, password, role = "general") =>
    API.post("/auth/register", { username, email, password, role });

export const refreshAccessToken = () =>
    API.post("/auth/refresh", {
        refresh_token: localStorage.getItem("refresh_token"),
    });

export const logoutUser = () =>
    API.post("/auth/logout", {
        refresh_token: localStorage.getItem("refresh_token"),
    });

export const queryDoc = (question, filename = null) => {
    const params = new URLSearchParams({ question });
    if (filename) params.append("filename", filename);
    return API.post(`/rag/query?${params}`);
};

export const uploadFile = (file) => {
    const form = new FormData();
    form.append("file", file);
    return API.post("/upload/file", form);
};

export const getUsers = () => API.get("/users/");
export const updateUserRole = (user_id, role) =>
    API.put(`/users/${user_id}/role`, { role });

export const getUserFiles = () => API.get("/upload/files");