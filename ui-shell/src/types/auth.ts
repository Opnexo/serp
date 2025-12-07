// Type definitions for authentication

export interface User {
    id: string;
    username: string;
    email: string;
    fullName: string;
    roles: string[];
    permissions: string[];
    avatar?: string;
    tenantId?: string;
}

export interface LoginCredentials {
    username: string;
    password: string;
}

export interface LoginResponse {
    accessToken: string;
    refreshToken: string;
    user: User;
    expiresIn: number;
}

export interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
}

export interface RefreshTokenResponse {
    accessToken: string;
    expiresIn: number;
}
