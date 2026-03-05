import { useState } from "react";
import Login from "./pages/login";
import Register from "./pages/register";
import Dashboard from "./pages/Dashboard";
import AdminPanel from "./pages/AdminPanel";

// Decode a JWT payload without a library (base64 decode the middle segment)
function parseJwt(token) {
  try {
    const payload = token.split(".")[1];
    return JSON.parse(atob(payload.replace(/-/g, "+").replace(/_/g, "/")));
  } catch {
    return null;
  }
}

// Read cached user info from localStorage
function readStoredUser() {
  const token = localStorage.getItem("access_token");
  if (!token) return null;
  const info = localStorage.getItem("user_info");
  if (info) return JSON.parse(info);
  return null;
}

export default function App() {
  const [user, setUser] = useState(readStoredUser);
  const [page, setPage] = useState("dashboard");
  const [view, setView] = useState("login");
  // Called after a successful login — userInfo comes directly from login.jsx
  const handleLoginSuccess = (accessToken, userInfo) => {
    setUser(userInfo);
    setPage("dashboard");
  };

  // Store extra user info after register so login can use it
  const handleRegisterSuccess = (username, role) => {
    localStorage.setItem("user_info", JSON.stringify({ username, role }));
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user_info");
    setUser(null);
    setView("login");
  };

  //Unauthenticated
  if (!user) {
    if (view === "register") {
      return (
        <Register
          onSwitchToLogin={() => setView("login")}
          onRegisterSuccess={handleRegisterSuccess}
        />
      );
    }
    return (
      <Login
        onSwitchToRegister={() => setView("register")}
        onLoginSuccess={handleLoginSuccess}
      />
    );
  }

  //Authenticated
  if (page === "admin" && user.role === "admin") {
    return (
      <AdminPanel
        user={user}
        onNavigate={setPage}
        onLogout={handleLogout}
      />
    );
  }

  return (
    <Dashboard
      user={user}
      onLogout={handleLogout}
      onNavigate={setPage}
    />
  );
}
