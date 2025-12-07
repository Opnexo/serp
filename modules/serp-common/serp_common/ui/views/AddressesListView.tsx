/**
 * AddressesListView - displays a list of all addresses.
 */

import * as React from 'react';
import type { Address, AddressList } from '../types';
import { listAddresses, deleteAddress } from '../api/addresses';
import { AddressCard } from '../components/AddressCard';

// Import from shell UI components
import { Button } from '@/components/ui';
import { Plus, RefreshCw } from 'lucide-react';

// Next.js navigation
import { useRouter } from 'next/navigation';

export function AddressesListView() {
    const router = useRouter();
    const [data, setData] = React.useState<AddressList | null>(null);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState<string | null>(null);

    const loadAddresses = React.useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            const result = await listAddresses({ limit: 100 });
            setData(result);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load addresses');
        } finally {
            setLoading(false);
        }
    }, []);

    React.useEffect(() => {
        loadAddresses();
    }, [loadAddresses]);

    const handleEdit = (address: Address) => {
        router.push(`/common/addresses/${address.id}/edit`);
    };

    const handleDelete = async (address: Address) => {
        if (!confirm(`Are you sure you want to delete "${address.label}"?`)) {
            return;
        }

        try {
            await deleteAddress(address.id);
            await loadAddresses();
        } catch (err) {
            alert(err instanceof Error ? err.message : 'Failed to delete address');
        }
    };

    const handleCreate = () => {
        router.push('/common/addresses/new');
    };

    const handleViewDetail = (address: Address) => {
        router.push(`/common/addresses/${address.id}`);
    };

    if (loading && !data) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin h-8 w-8 border-2 border-primary border-t-transparent rounded-full" />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Addresses</h1>
                    <p className="text-muted-foreground">
                        Manage shared addresses across your organization
                    </p>
                </div>
                <div className="flex gap-2">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={loadAddresses}
                        disabled={loading}
                    >
                        <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                        Refresh
                    </Button>
                    <Button size="sm" onClick={handleCreate}>
                        <Plus className="h-4 w-4 mr-2" />
                        New Address
                    </Button>
                </div>
            </div>

            {/* Error */}
            {error && (
                <div className="bg-destructive/10 text-destructive p-4 rounded-lg">
                    {error}
                </div>
            )}

            {/* Content */}
            {data && data.items.length === 0 ? (
                <div className="text-center py-12">
                    <p className="text-muted-foreground mb-4">No addresses found</p>
                    <Button onClick={handleCreate}>
                        <Plus className="h-4 w-4 mr-2" />
                        Create your first address
                    </Button>
                </div>
            ) : (
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {data?.items.map((address) => (
                        <AddressCard
                            key={address.id}
                            address={address}
                            onClick={() => handleViewDetail(address)}
                            showActions
                            onEdit={() => handleEdit(address)}
                            onDelete={() => handleDelete(address)}
                        />
                    ))}
                </div>
            )}

            {/* Pagination info */}
            {data && data.total > 0 && (
                <div className="text-sm text-muted-foreground text-center">
                    Showing {data.items.length} of {data.total} addresses
                </div>
            )}
        </div>
    );
}

export default AddressesListView;
