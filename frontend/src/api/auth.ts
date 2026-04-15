import { apiClient } from "./client";
import type { AuthUser } from "./types";

type LoginInput = {
  username: string;
  password: string;
};

type AuthUserResponse = {
  user: AuthUser;
};

export const authApi = {
  login(input: LoginInput) {
    return apiClient.post<AuthUserResponse>("/api/auth/login", input);
  },
  logout() {
    return apiClient.post<{ message: string }>("/api/auth/logout");
  },
  me() {
    return apiClient.get<AuthUserResponse>("/api/auth/me");
  },
};

