// Type definitions for API responses

export interface ApiResponse<T = any> {
    data: T;
    message?: string;
    success: boolean;
}

export interface ApiError {
    message: string;
    code?: string;
    status?: number;
    details?: Record<string, any>;
}

export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    pageSize: number;
    totalPages: number;
}

export interface PaginationParams {
    page?: number;
    pageSize?: number;
    sortBy?: string;
    sortOrder?: 'asc' | 'desc';
}

export interface FilterParams {
    [key: string]: any;
}
