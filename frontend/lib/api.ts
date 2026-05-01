import axios from "axios";

import type {
  AuthResponse,
  FutureFundingPredictionRequest,
  FutureFundingPredictionResponse,
  LoginRequest,
  RegisterRequest,
  StartupRequest,
  StartupResponse
} from "@/lib/types";

const baseURL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://127.0.0.1:8000";

const authStorageKey = "ventureforge_auth";

const api = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json"
  }
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = window.localStorage.getItem(authStorageKey);

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }

  return config;
});

export async function generateStartup(payload: StartupRequest) {
  const response = await api.post<StartupResponse>(
    "/generate-startup",
    payload
  );

  return response.data;
}

export async function predictFutureFunding(payload: FutureFundingPredictionRequest) {
  const response = await api.post<FutureFundingPredictionResponse>(
    "/predictions/future-funding",
    payload
  );

  return response.data;
}

export async function login(payload: LoginRequest) {
  const formData = new URLSearchParams();

  formData.append("username", payload.email);
  formData.append("password", payload.password);

  const response = await api.post<AuthResponse>(
    "/auth/login",
    formData,
    {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded"
      }
    }
  );

  return response.data;
}

export async function register(payload: RegisterRequest) {
  const response = await api.post<AuthResponse>(
    "/auth/register",
    payload
  );

  return response.data;
}

export async function fetchCurrentUser() {
  const response = await api.get<AuthResponse["user"]>(
    "/auth/me"
  );

  return response.data;
}

export function persistAuthSession(data: AuthResponse) {
  if (typeof window === "undefined") return;

  window.localStorage.setItem(
    authStorageKey,
    data.access_token
  );

  window.localStorage.setItem(
    "ventureforge_user",
    JSON.stringify(data.user)
  );
}

export function clearAuthSession() {
  if (typeof window === "undefined") return;

  window.localStorage.removeItem(authStorageKey);
  window.localStorage.removeItem("ventureforge_user");
}
