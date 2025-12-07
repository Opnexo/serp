// Type definitions for permissions

import type { ReactNode } from 'react';

export interface Permission {
    resource: string;
    action: string;
    conditions?: Record<string, any>;
}

export interface PermissionCheck {
    permission: string;
    fallback?: ReactNode;
}

export type PermissionOperator = 'AND' | 'OR';

export interface PermissionState {
    permissions: string[];
    isLoading: boolean;
}
