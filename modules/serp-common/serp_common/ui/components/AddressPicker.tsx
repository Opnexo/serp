/**
 * AddressPicker component - allows selecting or creating addresses.
 */

import * as React from 'react';
import type { Address } from '../types';
import { getAddressesForOwner } from '../api/addresses';
import { AddressCard } from './AddressCard';

// Import from shell UI components
import { Button } from '@/components/ui';
import { Plus } from 'lucide-react';

interface AddressPickerProps {
    ownerType: string;
    ownerId: string;
    selectedId?: string;
    onSelect: (address: Address | null) => void;
    onCreateNew?: () => void;
    allowCreate?: boolean;
}

export function AddressPicker({
    ownerType,
    ownerId,
    selectedId,
    onSelect,
    onCreateNew,
    allowCreate = true,
}: AddressPickerProps) {
    const [addresses, setAddresses] = React.useState<Address[]>([]);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState<string | null>(null);

    React.useEffect(() => {
        async function loadAddresses() {
            try {
                setLoading(true);
                setError(null);
                const data = await getAddressesForOwner(ownerType, ownerId);
                setAddresses(data);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load addresses');
            } finally {
                setLoading(false);
            }
        }

        if (ownerType && ownerId) {
            loadAddresses();
        }
    }, [ownerType, ownerId]);

    if (loading) {
        return (
            <div className="flex items-center justify-center p-4">
                <div className="animate-spin h-6 w-6 border-2 border-primary border-t-transparent rounded-full" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-sm text-destructive p-4">
                {error}
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {addresses.length === 0 ? (
                <div className="text-sm text-muted-foreground text-center p-4">
                    No addresses found
                </div>
            ) : (
                <div className="grid gap-4 sm:grid-cols-2">
                    {addresses.map((address) => (
                        <div
                            key={address.id}
                            className={
                                selectedId === address.id
                                    ? 'ring-2 ring-primary rounded-lg'
                                    : ''
                            }
                        >
                            <AddressCard
                                address={address}
                                onClick={() => onSelect(address)}
                            />
                        </div>
                    ))}
                </div>
            )}

            {allowCreate && onCreateNew && (
                <Button
                    variant="outline"
                    className="w-full"
                    onClick={onCreateNew}
                >
                    <Plus className="h-4 w-4 mr-2" />
                    Add New Address
                </Button>
            )}
        </div>
    );
}

export default AddressPicker;
