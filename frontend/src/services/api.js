import axios from "axios";

// In Docker, nginx proxies /api/ → http://api:8000/
// For local dev without Docker, set VITE_API_URL=http://localhost:8000 in .env
const API = axios.create({
    // baseURL: "http://localhost:8000",
    baseURL: import.meta.env.VITE_API_URL ?? "/api",

});

// ── Request interceptor: attach access token ──────────────────────────────────
API.interceptors.request.use((config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// ── Response interceptor: auto-refresh on 401 ────────────────────────────────
let isRefreshing = false;
let failedQueue = [];  // requests waiting while token is being refreshed

const processQueue = (error, token = null) => {
    failedQueue.forEach((prom) => {
        if (error) prom.reject(error);
        else prom.resolve(token);
    });
    failedQueue = [];
};

API.interceptors.response.use(
    (response) => response,
    async (error) => {
        const original = error.config;

        // Only retry on 401, and only once per request
        if (error.response?.status !== 401 || original._retry) {
            return Promise.reject(error);
        }

        // Don't retry refresh/login/logout calls themselves
        const skipPaths = ["/auth/refresh", "/auth/login", "/auth/logout"];
        if (skipPaths.some((p) => original.url?.includes(p))) {
            return Promise.reject(error);
        }

        if (isRefreshing) {
            // Queue this request until the refresh finishes
            return new Promise((resolve, reject) => {
                failedQueue.push({ resolve, reject });
            }).then((token) => {
                original.headers.Authorization = `Bearer ${token}`;
                return API(original);
            });
        }

        original._retry = true;
        isRefreshing = true;

        const refreshToken = localStorage.getItem("refresh_token");
        if (!refreshToken) {
            // No refresh token — force logout
            localStorage.clear();
            window.location.reload();
            return Promise.reject(error);
        }

        try {
            const res = await axios.post(
                // "http://localhost:8000/auth/refresh",
                `${import.meta.env.VITE_API_URL ?? "/api"}/auth/refresh`,
                { refresh_token: refreshToken }
            );
            const { access_token, refresh_token: newRefresh } = res.data;

            localStorage.setItem("access_token", access_token);
            localStorage.setItem("refresh_token", newRefresh);

            API.defaults.headers.common.Authorization = `Bearer ${access_token}`;
            processQueue(null, access_token);

            original.headers.Authorization = `Bearer ${access_token}`;
            return API(original);
        } catch (refreshError) {
            processQueue(refreshError, null);
            // Refresh failed — session is truly expired, force re-login
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            localStorage.removeItem("user_info");
            window.location.reload();
            return Promise.reject(refreshError);
        } finally {
            isRefreshing = false;
        }
    }
);

// ── Auth ──────────────────────────────────────────────────────────────────────
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

export const getUserFiles = () => API.get("/upload/files");

// ── Admin 
export const getUsers = () => API.get("/users/");
export const updateUserRole = (user_id, role) =>
    API.put(`/users/${user_id}/role`, { role });