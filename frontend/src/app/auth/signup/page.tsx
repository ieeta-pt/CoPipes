"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { apiClient } from "@/services/api";

function validatePassword(password: string): string | null {
  if (password.length < 12) {
    return "Password must be at least 12 characters long";
  }
  
  if (!/[A-Z]/.test(password)) {
    return "Password must contain at least one uppercase letter";
  }
  
  if (!/[a-z]/.test(password)) {
    return "Password must contain at least one lowercase letter";
  }
  
  if (!/\d/.test(password)) {
    return "Password must contain at least one number";
  }
  
  if (!/[!@#$%^&*()_+\-=\[\]{};:,.<>?]/.test(password)) {
    return "Password must contain at least one special character";
  }
  
  return null;
}

export default function SignupPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    // Validate passwords match
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      setLoading(false);
      return;
    }

    // Validate password strength
    const passwordError = validatePassword(password);
    if (passwordError) {
      setError(passwordError);
      setLoading(false);
      return;
    }

    try {
      const data = await apiClient.post("/api/auth/signup", {
        email,
        password,
        full_name: fullName,
      });

      setSuccess(data.message);
      // Clear form
      setEmail("");
      setPassword("");
      setConfirmPassword("");
      setFullName("");
      
      // Redirect to login after 2 seconds
      setTimeout(() => {
        router.push("/auth/login");
      }, 2000);
    } catch (error) {
      setError(error instanceof Error ? error.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-base-200">
      <div className="card w-full max-w-md bg-base-100 shadow-xl">
        <div className="card-body">
          <h2 className="card-title text-2xl font-bold text-center mb-6">
            Sign Up
          </h2>
          
          {error && (
            <div className="alert alert-error mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{error}</span>
            </div>
          )}
          
          {success && (
            <div className="alert alert-success mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{success}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="form-control">
              <label className="label">
                <span className="label-text">Full Name</span>
              </label>
              <input
                type="text"
                placeholder="Enter your full name"
                className="input input-bordered w-full"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
              />
            </div>

            <div className="form-control">
              <label className="label">
                <span className="label-text">Email</span>
              </label>
              <input
                type="email"
                placeholder="Enter your email"
                className="input input-bordered w-full"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="form-control">
              <label className="label">
                <span className="label-text">Password</span>
              </label>
              <input
                type="password"
                placeholder="Enter your password"
                className="input input-bordered w-full"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={12}
              />
              {/* <label className="label">
                <span className="label-text-alt text-xs">Must be 12+ characters containing uppercase, lowercase, number, and special character.</span>
              </label> */}
            </div>

            <div className="form-control">
              <label className="label">
                <span className="label-text">Confirm Password</span>
              </label>
              <input
                type="password"
                placeholder="Confirm your password"
                className="input input-bordered w-full"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
            </div>

            <div className="form-control mt-6">
              <button
                type="submit"
                className={`btn btn-primary w-full ${loading ? "loading" : ""}`}
                disabled={loading}
              >
                {loading ? "Creating Account..." : "Sign Up"}
              </button>
            </div>
          </form>

          <div className="divider">OR</div>

          <div className="text-center">
            <p>
              Already have an account?{" "}
              <Link href="/auth/login" className="link link-primary">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}