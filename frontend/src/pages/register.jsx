import { useState } from "react";
import { registerUser } from "../services/api";

const ROLES = [
    { value: "general", label: "General" },
    { value: "doctor", label: "Doctor" },
    { value: "lawyer", label: "Lawyer" },
    { value: "researcher", label: "Researcher" },
    { value: "consultant", label: "Consultant" },
    { value: "financial_analyst", label: "Financial Analyst" },
];

function validate({ username, email, password, confirm }) {
    const e = {};
    if (!username.trim()) e.username = "Username is required.";
    if (!/\S+@\S+\.\S+/.test(email)) e.email = "Enter a valid email.";
    if (password.length < 8) e.password = "At least 8 characters.";
    else if (!/[A-Z]/.test(password)) e.password = "Needs an uppercase letter.";
    else if (!/[a-z]/.test(password)) e.password = "Needs a lowercase letter.";
    else if (!/\d/.test(password)) e.password = "Needs a digit.";
    else if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) e.password = "Needs a special character.";
    if (password !== confirm) e.confirm = "Passwords do not match.";
    return e;
}

export default function Register({ onSwitchToLogin }) {
    const [form, setForm] = useState({ username: "", email: "", password: "", confirm: "", role: "general" });
    const [showPw, setShowPw] = useState(false);
    const [fieldErrors, setFieldErrors] = useState({});
    const [globalError, setGlobalError] = useState("");
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);

    const update = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }));

    const handleSubmit = async (e) => {
        e.preventDefault();
        const errs = validate(form);
        setFieldErrors(errs);
        if (Object.keys(errs).length) return;
        setGlobalError(""); setLoading(true);
        try {
            await registerUser(form.username, form.email, form.password, form.role);
            setSuccess(true);
            setTimeout(() => onSwitchToLogin(), 1800);
        } catch (err) {
            setGlobalError(err.response?.data?.detail || "Registration failed.");
        } finally {
            setLoading(false);
        }
    };

    if (success) return (
        <div className="min-h-screen flex items-center justify-center">
            <div className="auth-card text-center">
                <div className="text-5xl mb-4">🎉</div>
                <h2 className="text-xl font-bold mb-2">Account created!</h2>
                <p className="text-sm text-slate-500">Redirecting to sign in…</p>
            </div>
        </div>
    );

    const Field = ({ id, label, error, children }) => (
        <div>
            <label htmlFor={id} className="form-label">{label}</label>
            {children}
            {error && <p className="field-err">{error}</p>}
        </div>
    );

    return (
        <div className="min-h-screen flex items-center justify-center px-4 py-10"
            style={{ background: "radial-gradient(ellipse 60% 50% at 80% 110%, rgba(16,185,129,0.08) 0%, transparent 55%), #0d0f14" }}>
            <div className="auth-card">

                {/* Brand */}
                <div className="flex items-center gap-3 mb-8">
                    <div className="flex h-9 w-9 items-center justify-center rounded-xl
                          bg-gradient-to-br from-indigo-500 to-indigo-700 text-lg select-none">
                        📄
                    </div>
                    <span className="text-lg font-bold tracking-tight">DocuChat</span>
                </div>

                <h1 className="text-2xl font-bold tracking-tight mb-1">Create account</h1>
                <p className="text-sm text-slate-500 mb-7">Get started in seconds</p>

                {globalError && <p className="alert-error mb-5">{globalError}</p>}

                <form onSubmit={handleSubmit} noValidate className="space-y-4">
                    <Field id="rg-username" label="Username" error={fieldErrors.username}>
                        <input id="rg-username" type="text" placeholder="Choose a username" value={form.username}
                            onChange={update("username")} autoComplete="username"
                            className={`form-input ${fieldErrors.username ? "has-error" : ""}`} />
                    </Field>

                    <Field id="rg-email" label="Email" error={fieldErrors.email}>
                        <input id="rg-email" type="email" placeholder="you@example.com" value={form.email}
                            onChange={update("email")} autoComplete="email"
                            className={`form-input ${fieldErrors.email ? "has-error" : ""}`} />
                    </Field>

                    <Field id="rg-role" label="Role" error={null}>
                        <select id="rg-role" value={form.role} onChange={update("role")}
                            className="form-input cursor-pointer">
                            {ROLES.map((r) => (
                                <option key={r.value} value={r.value} className="bg-[#161a24]">{r.label}</option>
                            ))}
                        </select>
                    </Field>

                    <Field id="rg-password" label="Password" error={fieldErrors.password}>
                        <div className="relative">
                            <input id="rg-password" type={showPw ? "text" : "password"}
                                placeholder="Min 8 chars, uppercase, digit, symbol" value={form.password}
                                onChange={update("password")} autoComplete="new-password"
                                className={`form-input pr-11 ${fieldErrors.password ? "has-error" : ""}`} />
                            <button type="button" onClick={() => setShowPw((v) => !v)}
                                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-200 transition text-xs">
                                {showPw ? "Hide" : "Show"}
                            </button>
                        </div>
                    </Field>

                    <Field id="rg-confirm" label="Confirm Password" error={fieldErrors.confirm}>
                        <input id="rg-confirm" type={showPw ? "text" : "password"}
                            placeholder="Repeat your password" value={form.confirm}
                            onChange={update("confirm")} autoComplete="new-password"
                            className={`form-input ${fieldErrors.confirm ? "has-error" : ""}`} />
                    </Field>

                    <button type="submit" className="btn-primary w-full mt-2" disabled={loading}>
                        {loading && <span className="spinner" />}
                        {loading ? "Creating account…" : "Create Account"}
                    </button>
                </form>

                <p className="mt-6 text-center text-sm text-slate-500">
                    Already have an account?{" "}
                    <button className="text-indigo-400 font-medium hover:text-white transition"
                        onClick={onSwitchToLogin}>Sign in</button>
                </p>
            </div>
        </div>
    );
}