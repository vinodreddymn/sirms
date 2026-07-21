import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Eye, EyeOff, User, Lock, Loader2 } from "lucide-react";
import { api } from "../../services/api";
import logo from "../../assets/geebee-logo.png";
import "./Login.css";

export const Login: React.FC = () => {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();

    setLoading(true);
    setError("");

    try {
      const response = await api.post("/auth/login", {
        username,
        password,
      });

      localStorage.setItem(
        "access_token",
        response.data.access_token
      );

      navigate("/");
    } catch {
      setError("Invalid username or password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">

      <div className="login-left">

        <div className="overlay">

          <img
            src={logo}
            alt="Gee Bee"
            className="company-logo"
          />

          <h1>SIRMS</h1>

          <h2>
            Stock & Infrastructure Resource
            Management System
          </h2>

          <p>
            Centralized Asset Management, Incident
            Tracking, Preventive Maintenance and
            Engineering Operations Platform.
          </p>

        </div>

      </div>

      <div className="login-right">

        <div className="login-card">

          <h2>Welcome Back</h2>

          <p>
            Please login to continue
          </p>

          {error && (
            <div className="login-error">
              {error}
            </div>
          )}

          <form onSubmit={handleLogin}>

            <div className="input-group">

              <User size={18} />

              <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) =>
                  setUsername(e.target.value)
                }
                required
              />

            </div>

            <div className="input-group">

              <Lock size={18} />

              <input
                type={
                  showPassword
                    ? "text"
                    : "password"
                }
                placeholder="Password"
                value={password}
                onChange={(e) =>
                  setPassword(e.target.value)
                }
                required
              />

              <button
                type="button"
                className="password-toggle"
                onClick={() =>
                  setShowPassword(!showPassword)
                }
              >
                {showPassword ? (
                  <EyeOff size={18} />
                ) : (
                  <Eye size={18} />
                )}
              </button>

            </div>

            <button
              className="login-btn"
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader2
                    className="spin"
                    size={18}
                  />
                  Signing In...
                </>
              ) : (
                "Sign In"
              )}
            </button>

          </form>

          <div className="footer">

            © 2026 Gee Bee Network Pvt. Ltd.

          </div>

        </div>

      </div>

    </div>
  );
};