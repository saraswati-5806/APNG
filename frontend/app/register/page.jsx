"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function RegisterPage() {
  const router = useRouter();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleRegister(e) {
    e.preventDefault();

    setError("");
    setSuccess("");

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        "http://localhost:8000/api/auth/register",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            username,
            password,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Registration failed");
      }

      setSuccess("Registration successful. Redirecting to login...");

      setTimeout(() => {
        router.push("/login");
      }, 1000);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={styles.page}>
      <div style={styles.card}>
        <div style={styles.logo}>APNG</div>

        <h1 style={styles.title}>
          Create Account
        </h1>

        <p style={styles.subtitle}>
          Autonomous Predictive Network Guardian
        </p>

        <form onSubmit={handleRegister}>
          <label style={styles.label}>Username</label>

          <input
            type="text"
            placeholder="Enter username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            style={styles.input}
          />

          <label style={styles.label}>Password</label>

          <input
            type="password"
            placeholder="Enter password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={styles.input}
          />

          <label style={styles.label}>Confirm Password</label>

          <input
            type="password"
            placeholder="Confirm password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            style={styles.input}
          />

          {error && (
            <div style={styles.error}>
              {error}
            </div>
          )}

          {success && (
            <div style={styles.success}>
              {success}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={styles.button}
          >
            {loading ? "Creating Account..." : "REGISTER"}
          </button>
        </form>

        <p style={styles.loginText}>
          Already have an account?
        </p>

        <button
          type="button"
          onClick={() => router.push("/login")}
          style={styles.loginButton}
        >
          LOGIN
        </button>

        <p style={styles.footer}>
          APNG • Secure Local Access
        </p>
      </div>
    </main>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    background: "#070b12",
    color: "#ffffff",
    fontFamily: "Arial, sans-serif",
    padding: "20px",
  },

  card: {
    width: "100%",
    maxWidth: "430px",
    background: "#111827",
    border: "1px solid #263244",
    borderRadius: "14px",
    padding: "40px",
    boxShadow: "0 20px 50px rgba(0,0,0,0.45)",
  },

  logo: {
    textAlign: "center",
    fontSize: "42px",
    fontWeight: "800",
    letterSpacing: "4px",
    color: "#38bdf8",
    marginBottom: "18px",
  },

  title: {
    textAlign: "center",
    fontSize: "24px",
    margin: "0",
  },

  subtitle: {
    textAlign: "center",
    color: "#94a3b8",
    marginBottom: "32px",
  },

  label: {
    display: "block",
    marginBottom: "8px",
    marginTop: "18px",
    color: "#cbd5e1",
    fontSize: "14px",
  },

  input: {
    width: "100%",
    boxSizing: "border-box",
    padding: "13px",
    borderRadius: "8px",
    border: "1px solid #334155",
    background: "#0f172a",
    color: "#ffffff",
    outline: "none",
    fontSize: "15px",
  },

  button: {
    width: "100%",
    marginTop: "28px",
    padding: "13px",
    border: "none",
    borderRadius: "8px",
    background: "#38bdf8",
    color: "#07111f",
    fontWeight: "700",
    fontSize: "15px",
    cursor: "pointer",
  },

  loginButton: {
    width: "100%",
    padding: "11px",
    border: "1px solid #334155",
    borderRadius: "8px",
    background: "transparent",
    color: "#38bdf8",
    fontWeight: "700",
    fontSize: "14px",
    cursor: "pointer",
  },

  error: {
    marginTop: "15px",
    padding: "10px",
    borderRadius: "6px",
    background: "#3f1d1d",
    color: "#fca5a5",
    fontSize: "14px",
  },

  success: {
    marginTop: "15px",
    padding: "10px",
    borderRadius: "6px",
    background: "#123524",
    color: "#86efac",
    fontSize: "14px",
  },

  loginText: {
    textAlign: "center",
    color: "#64748b",
    fontSize: "13px",
    marginTop: "25px",
    marginBottom: "10px",
  },

  footer: {
    textAlign: "center",
    color: "#64748b",
    fontSize: "12px",
    marginTop: "28px",
  },
};