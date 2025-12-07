/**
 * API client for addresses.
 */

import type { Address, AddressCreateInput, AddressList, AddressUpdateInput } from '../types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * List addresses with optional filters.
 */
export async function listAddresses(params?: {
    skip?: number;
    limit?: number;
    owner_type?: string;
    owner_id?: string;
    address_type?: string;
    is_active?: boolean;
}): Promise<AddressList> {
    const searchParams = new URLSearchParams();

    if (params?.skip !== undefined) searchParams.set('skip', String(params.skip));
    if (params?.limit !== undefined) searchParams.set('limit', String(params.limit));
    if (params?.owner_type) searchParams.set('owner_type', params.owner_type);
    if (params?.owner_id) searchParams.set('owner_id', params.owner_id);
    if (params?.address_type) searchParams.set('address_type', params.address_type);
    if (params?.is_active !== undefined) searchParams.set('is_active', String(params.is_active));

    const url = `${API_BASE}/api/common/addresses?${searchParams}`;
    const response = await fetch(url);

    if (!response.ok) {
        throw new Error(`Failed to fetch addresses: ${response.statusText}`);
    }

    return response.json();
}

/**
 * Get a single address by ID.
 */
export async function getAddress(id: string): Promise<Address> {
    const response = await fetch(`${API_BASE}/api/common/addresses/${id}`);

    if (!response.ok) {
        throw new Error(`Failed to fetch address: ${response.statusText}`);
    }

    return response.json();
}

/**
 * Create a new address.
 */
export async function createAddress(data: AddressCreateInput): Promise<Address> {
    const response = await fetch(`${API_BASE}/api/common/addresses`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || `Failed to create address: ${response.statusText}`);
    }

    return response.json();
}

/**
 * Update an existing address.
 */
export async function updateAddress(id: string, data: AddressUpdateInput): Promise<Address> {
    const response = await fetch(`${API_BASE}/api/common/addresses/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || `Failed to update address: ${response.statusText}`);
    }

    return response.json();
}

/**
 * Delete an address.
 */
export async function deleteAddress(id: string): Promise<void> {
    const response = await fetch(`${API_BASE}/api/common/addresses/${id}`, {
        method: 'DELETE',
    });

    if (!response.ok) {
        throw new Error(`Failed to delete address: ${response.statusText}`);
    }
}

/**
 * Get all addresses for an owner.
 */
export async function getAddressesForOwner(
    ownerType: string,
    ownerId: string
): Promise<Address[]> {
    const response = await fetch(
        `${API_BASE}/api/common/addresses/owner/${ownerType}/${ownerId}`
    );

    if (!response.ok) {
        throw new Error(`Failed to fetch addresses: ${response.statusText}`);
    }

    return response.json();
}

/**
 * Get the primary address for an owner.
 */
export async function getPrimaryAddress(
    ownerType: string,
    ownerId: string
): Promise<Address | null> {
    const response = await fetch(
        `${API_BASE}/api/common/addresses/owner/${ownerType}/${ownerId}/primary`
    );

    if (response.status === 404) {
        return null;
    }

    if (!response.ok) {
        throw new Error(`Failed to fetch primary address: ${response.statusText}`);
    }

    return response.json();
}
