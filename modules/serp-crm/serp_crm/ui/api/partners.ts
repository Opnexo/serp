/**
 * Partners API Client
 * Handles all HTTP requests for Partner entity
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Partner {
    id: string;
    name: string;
    partnerType: 'COMPANY' | 'INDIVIDUAL';
    isCustomer: boolean;
    isSupplier: boolean;
    isActive: boolean;
    email?: string;
    phone?: string;
    website?: string;
    industry?: string;
    taxId?: string;
    address?: {
        street?: string;
        city?: string;
        state?: string;
        postalCode?: string;
        country?: string;
    };
    createdAt?: string;
    updatedAt?: string;
}

export interface PartnerCreateInput {
    name: string;
    partnerType: 'COMPANY' | 'INDIVIDUAL';
    isCustomer?: boolean;
    isSupplier?: boolean;
    isActive?: boolean;
    email?: string;
    phone?: string;
    website?: string;
    industry?: string;
    taxId?: string;
    address?: {
        street?: string;
        city?: string;
        state?: string;
        postalCode?: string;
        country?: string;
    };
}

export interface PartnerUpdateInput extends Partial<PartnerCreateInput> { }

export interface PartnerListParams {
    search?: string;
    partnerType?: 'COMPANY' | 'INDIVIDUAL';
    isCustomer?: boolean;
    isSupplier?: boolean;
    isActive?: boolean;
    skip?: number;
    limit?: number;
}

export interface PartnerListResponse {
    items: Partner[];
    total: number;
    skip: number;
    limit: number;
}

/**
 * Get authentication token from storage
 */
function getAuthToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('auth_token');
}

/**
 * Build request headers with authentication
 */
function getHeaders(): HeadersInit {
    const headers: HeadersInit = {
        'Content-Type': 'application/json',
    };

    const token = getAuthToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
}

/**
 * Handle API response
 */
async function handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
        const error = await response.json().catch(() => ({
            detail: response.statusText,
        }));
        throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }
    return response.json();
}

/**
 * Get list of partners with optional filters
 */
export async function getPartners(params?: PartnerListParams): Promise<PartnerListResponse> {
    const queryParams = new URLSearchParams();

    if (params?.search) queryParams.append('search', params.search);
    if (params?.partnerType) queryParams.append('partner_type', params.partnerType);
    if (params?.isCustomer !== undefined) queryParams.append('is_customer', String(params.isCustomer));
    if (params?.isSupplier !== undefined) queryParams.append('is_supplier', String(params.isSupplier));
    if (params?.isActive !== undefined) queryParams.append('is_active', String(params.isActive));
    if (params?.skip !== undefined) queryParams.append('skip', String(params.skip));
    if (params?.limit !== undefined) queryParams.append('limit', String(params.limit));

    const url = `${API_BASE_URL}/api/crm/partners?${queryParams}`;

    const response = await fetch(url, {
        method: 'GET',
        headers: getHeaders(),
    });

    return handleResponse<PartnerListResponse>(response);
}

/**
 * Get a single partner by ID
 */
export async function getPartner(id: string): Promise<Partner> {
    const response = await fetch(`${API_BASE_URL}/api/crm/partners/${id}`, {
        method: 'GET',
        headers: getHeaders(),
    });

    return handleResponse<Partner>(response);
}

/**
 * Create a new partner
 */
export async function createPartner(data: PartnerCreateInput): Promise<Partner> {
    const response = await fetch(`${API_BASE_URL}/api/crm/partners`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(data),
    });

    return handleResponse<Partner>(response);
}

/**
 * Update an existing partner
 */
export async function updatePartner(id: string, data: PartnerUpdateInput): Promise<Partner> {
    const response = await fetch(`${API_BASE_URL}/api/crm/partners/${id}`, {
        method: 'PUT',
        headers: getHeaders(),
        body: JSON.stringify(data),
    });

    return handleResponse<Partner>(response);
}

/**
 * Delete a partner
 */
export async function deletePartner(id: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/crm/partners/${id}`, {
        method: 'DELETE',
        headers: getHeaders(),
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({
            detail: response.statusText,
        }));
        throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }
}
