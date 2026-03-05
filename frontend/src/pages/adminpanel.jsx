import { useState, useEffect } from "react";
import Navbar from "../components/Navbar";
import { getUsers, updateUserRole } from "../services/api";

const ROLES = ["general", "doctor", "lawyer", "researcher", "consultant", "financial_analyst", "admin"];

export default function AdminPanel({ user, onNavigate, onLogout }) {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [updating, setUpdating] = useState(null); // user id being updated

    const fetchUsers = async () => {
        setLoading(true);
        setError("");
        try {
            const res = await getUsers();
            setUsers(res.data);
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to load users.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { fetchUsers(); }, []);

    const handleRoleChange = async (userId, newRole) => {
        setUpdating(userId);
        try {
            await updateUserRole(userId, newRole);
            setUsers((prev) =>
                prev.map((u) => (u.id === userId ? { ...u, role: newRole } : u))
            );
        } catch (err) {
            alert(err.response?.data?.detail || "Failed to update role.");
        } finally {
            setUpdating(null);
        }
    };

    return (
        <div className="flex flex-col min-h-screen">
            <Navbar
                username={user.username}
                role={user.role}
                currentPage="admin"
                onNavigate={onNavigate}
                onLogout={onLogout}
            />

            <main className="flex-1 px-6 py-8 max-w-5xl mx-auto w-full">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h1 className="text-xl font-bold tracking-tight">User Management</h1>
                        <p className="text-sm text-slate-500 mt-0.5">
                            View and update roles for all registered users
                        </p>
                    </div>
                    <button onClick={fetchUsers} className="btn-secondary text-xs">
                        ↻ Refresh
                    </button>
                </div>

                {error && <p className="alert-error mb-4">{error}</p>}

                <div className="surface overflow-hidden">
                    {loading ? (
                        <div className="flex items-center justify-center py-16 text-slate-500 gap-2">
                            <span className="spinner" /> Loading users…
                        </div>
                    ) : (
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b border-white/10 text-xs uppercase tracking-widest text-slate-500">
                                    <th className="px-5 py-3 text-left font-medium">ID</th>
                                    <th className="px-5 py-3 text-left font-medium">Username</th>
                                    <th className="px-5 py-3 text-left font-medium">Email</th>
                                    <th className="px-5 py-3 text-left font-medium">Role</th>
                                </tr>
                            </thead>
                            <tbody>
                                {users.map((u) => (
                                    <tr
                                        key={u.id}
                                        className="border-b border-white/5 hover:bg-white/5 transition"
                                    >
                                        <td className="px-5 py-3 text-slate-500">{u.id}</td>
                                        <td className="px-5 py-3 font-medium text-slate-200">{u.username}</td>
                                        <td className="px-5 py-3 text-slate-400">{u.email}</td>
                                        <td className="px-5 py-3">
                                            <div className="flex items-center gap-2">
                                                <select
                                                    value={u.role}
                                                    onChange={(e) => handleRoleChange(u.id, e.target.value)}
                                                    disabled={updating === u.id}
                                                    className="rounded-lg border border-white/10 bg-white/5 px-3 py-1
                                     text-xs text-slate-300 outline-none focus:border-indigo-500
                                     transition cursor-pointer disabled:opacity-50"
                                                >
                                                    {ROLES.map((r) => (
                                                        <option key={r} value={r} className="bg-[#161a24]">
                                                            {r}
                                                        </option>
                                                    ))}
                                                </select>
                                                {updating === u.id && <span className="spinner" />}
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>

                <p className="mt-3 text-xs text-slate-600 text-right">
                    {users.length} user{users.length !== 1 ? "s" : ""} total
                </p>
            </main>
        </div>
    );
}
