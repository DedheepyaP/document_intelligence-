import { useState } from "react";
import { loginUser } from "../services/api";

export default function Login({ onSwitchToRegister, onLoginSuccess }) {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!username.trim() || !password) return;
        setError("");
        setLoading(true);
        try {
            const res = await loginUser(username, password);
            const { access_token, refresh_token, username: returnedUsername, role } = res.data;
            localStorage.setItem("access_token", access_token);
            localStorage.setItem("refresh_token", refresh_token);
            const userInfo = { username: returnedUsername ?? username, role: role ?? "general" };
            localStorage.setItem("user_info", JSON.stringify(userInfo));
            onLoginSuccess(access_token, userInfo);
        } catch (err) {
            setError(err.response?.data?.detail || "Invalid credentials. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center px-4"
            style={{ background: "radial-gradient(ellipse 80% 60% at 20% -10%, rgba(99,102,241,0.15) 0%, transparent 60%), #0d0f14" }}>
            <div className="auth-card">

                {/* Brand */}
                <div className="flex items-center gap-3 mb-8">
                    <div className="flex h-9 w-9 items-center justify-center rounded-xl
                          bg-gradient-to-br from-indigo-500 to-indigo-700 text-lg select-none">
                        📄
                    </div>
                    <span className="text-lg font-bold tracking-tight">DocuChat</span>
                </div>

                <h1 className="text-2xl font-bold tracking-tight mb-1">Welcome back</h1>
                <p className="text-sm text-slate-500 mb-7">Sign in to your account to continue</p>

                {error && <p className="alert-error mb-5">{error}</p>}

                <form onSubmit={handleSubmit} noValidate className="space-y-4">
                    <div>
                        <label htmlFor="lg-username" className="form-label">Username</label>
                        <input
                            id="lg-username" type="text" className="form-input"
                            placeholder="Enter your username" value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            autoComplete="username" required
                        />
                    </div>

                    <div>
                        <label htmlFor="lg-password" className="form-label">Password</label>
                        <div className="relative">
                            <input
                                id="lg-password" className="form-input pr-11"
                                type={showPassword ? "text" : "password"}
                                placeholder="Enter your password" value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                autoComplete="current-password" required
                            />
                            <button type="button" onClick={() => setShowPassword((v) => !v)}
                                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-200 transition text-xs">
                                {showPassword ? "Hide" : "Show"}
                            </button>
                        </div>
                    </div>

                    <button type="submit" className="btn-primary w-full mt-2"
                        disabled={loading || !username || !password}>
                        {loading && <span className="spinner" />}
                        {loading ? "Signing in…" : "Sign In"}
                    </button>
                </form>

                <p className="mt-6 text-center text-sm text-slate-500">
                    Don't have an account?{" "}
                    <button className="text-indigo-400 font-medium hover:text-white transition"
                        onClick={onSwitchToRegister}>
                        Create one
                    </button>
                </p>
            </div>
        </div>
    );
}