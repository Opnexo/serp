/**
 * TypeScript types for Common module.
 */

export interface Address {
    id: string;
    label: string;
    street: string;
    city: string;
    country: string;
    state?: string;
    postal_code?: string;
    address_type: AddressType;
    owner_type?: string;
    owner_id?: string;
    is_primary: boolean;
    is_active: boolean;
    notes?: string;
    single_line: string;
    created_at: string;
    updated_at: string;
}

export type AddressType = 'BILLING' | 'SHIPPING' | 'OFFICE' | 'HOME' | 'OTHER';

export interface AddressCreateInput {
    label: string;
    street: string;
    city: string;
    country: string;
    state?: string;
    postal_code?: string;
    address_type?: AddressType;
    owner_type?: string;
    owner_id?: string;
    is_primary?: boolean;
    notes?: string;
}

export interface AddressUpdateInput {
    label?: string;
    street?: string;
    city?: string;
    country?: string;
    state?: string;
    postal_code?: string;
    address_type?: AddressType;
    is_primary?: boolean;
    notes?: string;
}

export interface AddressList {
    items: Address[];
    total: number;
    skip: number;
    limit: number;
}
