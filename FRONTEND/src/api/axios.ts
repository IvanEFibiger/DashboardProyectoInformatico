import axios, { AxiosError, AxiosRequestConfig, InternalAxiosRequestConfig } from "axios";
import { getToken, setToken, clearAuth } from "../security/localAuth";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5500";

export const api = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  withCredentials: true, 
});


api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getToken();
  if (token) {
    config.headers = config.headers || {};
    config.headers["Authorization"] = `Bearer ${token}`;
  }
  return config;
});


let isRefreshing = false;
let refreshPromise: Promise<string> | null = null;
type Subscriber = (token: string) => void;
const subscribers: Subscriber[] = [];

function onRefreshed(token: string) {
  subscribers.forEach((cb) => cb(token));
  subscribers.length = 0;
}

function addSubscriber(cb: Subscriber) {
  subscribers.push(cb);
}

async function refreshAccessToken(): Promise<string> {
  if (isRefreshing && refreshPromise) return refreshPromise;

  isRefreshing = true;
  refreshPromise = (async () => {
    const res = await api.post("/auth/refresh"); 
    const { token } = res.data || {};
    if (!token) throw new Error("Refresh sin token");
    setToken(token);
    return token as string;
  })();

  try {
    const newToken = await refreshPromise;
    onRefreshed(newToken);
    return newToken;
  } finally {
    isRefreshing = false;
    refreshPromise = null;
  }
}

type RetriableConfig = AxiosRequestConfig & { _retry?: boolean };


api.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const original = (error.config || {}) as RetriableConfig;

    if (error.response?.status !== 401 || original._retry) {
      return Promise.reject(error);
    }

    original._retry = true;

    try {
      const newToken = await refreshAccessToken();
      original.headers = original.headers || {};
      original.headers["Authorization"] = `Bearer ${newToken}`;
      return api(original);
    } catch (e) {
      clearAuth();
      return Promise.reject(e);
    }
  }
);


let preRefreshTimer: number | null = null;

export function schedulePreRefresh(secondsFromNow: number) {
  if (preRefreshTimer) window.clearTimeout(preRefreshTimer);
  preRefreshTimer = window.setTimeout(async () => {
    try {
      const t = await refreshAccessToken();
      setToken(t); 
    } catch {
      
    }
  }, secondsFromNow * 1000) as unknown as number;
}


export function cancelPreRefresh() {
  if (preRefreshTimer) {
    window.clearTimeout(preRefreshTimer);
    preRefreshTimer = null;
  }
}
