import { logoutUser } from "../services/api";

export default function Navbar({ username, role, currentPage, onNavigate, onLogout }) {
    const handleLogout = async () => {
        try { await logoutUser(); } catch (_) { }
        onLogout();
    };

    return (
        <nav className="sticky top-0 z-50 flex items-center justify-between
                    border-b border-white/10 bg-[#0d0f14]/80 px-6 py-3 backdrop-blur">
            {/* Brand */}
            <div className="flex items-center gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg
                        bg-gradient-to-br from-indigo-500 to-indigo-700 text-base select-none">
                    📄
                </div>
                <span className="text-base font-bold tracking-tight">DocuChat</span>
            </div>

            {/* Nav links */}
            <div className="flex items-center gap-1">
                <button
                    onClick={() => onNavigate("dashboard")}
                    className={`rounded-lg px-3 py-1.5 text-sm font-medium transition
            ${currentPage === "dashboard"
                            ? "bg-indigo-600/20 text-indigo-400"
                            : "text-slate-400 hover:text-slate-100 hover:bg-white/5"}`}
                >
                    Dashboard
                </button>
                {role === "admin" && (
                    <button
                        onClick={() => onNavigate("admin")}
                        className={`rounded-lg px-3 py-1.5 text-sm font-medium transition
              ${currentPage === "admin"
                                ? "bg-indigo-600/20 text-indigo-400"
                                : "text-slate-400 hover:text-slate-100 hover:bg-white/5"}`}
                    >
                        Admin
                    </button>
                )}
            </div>

            {/* User + Logout */}
            <div className="flex items-center gap-3">
                <span className="hidden text-xs text-slate-500 sm:block">
                    {username}
                    {role && (
                        <span className="ml-2 rounded-full bg-indigo-600/20 px-2 py-0.5
                             text-[10px] font-semibold uppercase tracking-wider text-indigo-400">
                            {role}
                        </span>
                    )}
                </span>
                <button onClick={handleLogout} className="btn-secondary text-xs py-1.5 px-3">
                    Logout
                </button>
            </div>
        </nav>
    );
}
