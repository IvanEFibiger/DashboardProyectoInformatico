// src/services/api.ts
import axios from "axios";

const baseURL =
  (import.meta.env.VITE_API_BASE_URL as string) ?? "http://127.0.0.1:5500";

export const api = axios.create({ baseURL });
