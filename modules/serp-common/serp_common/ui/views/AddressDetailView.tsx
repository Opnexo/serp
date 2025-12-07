/**
 * AddressDetailView - displays details of a single address.
 */

import * as React from 'react';
import type { Address } from '../types';
import { getAddress, deleteAddress } from '../api/addresses';

// Import from shell UI components
import { Button, Card, CardContent, CardHeader, CardTitle } from '@/components/ui';
import { ArrowLeft, Edit, Trash2, MapPin, Star } from 'lucide-react';

// Next.js navigation
import { useRouter, useParams } from 'next/navigation';

export function AddressDetailView() {
    const router = useRouter();
    const params = useParams();
    const addressId = params?.id as string;

    const [address, setAddress] = React.useState<Address | null>(null);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState<string | null>(null);

    React.useEffect(() => {
        async function loadAddress() {
            if (!addressId) return;

            try {
                setLoading(true);
                setError(null);
                const data = await getAddress(addressId);
                setAddress(data);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load address');
            } finally {
                setLoading(false);
            }
        }

        loadAddress();
    }, [addressId]);

    const handleEdit = () => {
        router.push(`/common/addresses/${addressId}/edit`);
    };

    const handleDelete = async () => {
        if (!address) return;

        if (!confirm(`Are you sure you want to delete "${address.label}"?`)) {
            return;
        }

        try {
            await deleteAddress(address.id);
            router.push('/common/addresses');
        } catch (err) {
            alert(err instanceof Error ? err.message : 'Failed to delete address');
        }
    };

    const handleBack = () => {
        router.push('/common/addresses');
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin h-8 w-8 border-2 border-primary border-t-transparent rounded-full" />
            </div>
        );
    }

    if (error || !address) {
        return (
            <div className="space-y-4">
                <Button variant="ghost" onClick={handleBack}>
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Back to Addresses
                </Button>
                <div className="bg-destructive/10 text-destructive p-4 rounded-lg">
                    {error || 'Address not found'}
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Button variant="ghost" size="sm" onClick={handleBack}>
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                    <div>
                        <div className="flex items-center gap-2">
                            <h1 className="text-2xl font-bold">{address.label}</h1>
                            {address.is_primary && (
                                <Star className="h-5 w-5 text-yellow-500 fill-yellow-500" />
                            )}
                        </div>
                        <p className="text-muted-foreground">
                            {address.address_type} Address
                        </p>
                    </div>
                </div>
                <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={handleEdit}>
                        <Edit className="h-4 w-4 mr-2" />
                        Edit
                    </Button>
                    <Button variant="destructive" size="sm" onClick={handleDelete}>
                        <Trash2 className="h-4 w-4 mr-2" />
                        Delete
                    </Button>
                </div>
            </div>

            {/* Content */}
            <div className="grid gap-6 md:grid-cols-2">
                {/* Address Details */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <MapPin className="h-5 w-5" />
                            Address Details
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div>
                            <label className="text-sm font-medium text-muted-foreground">
                                Street
                            </label>
                            <p>{address.street}</p>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="text-sm font-medium text-muted-foreground">
                                    City
                                </label>
                                <p>{address.city}</p>
                            </div>
                            <div>
                                <label className="text-sm font-medium text-muted-foreground">
                                    State
                                </label>
                                <p>{address.state || '-'}</p>
                            </div>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="text-sm font-medium text-muted-foreground">
                                    Postal Code
                                </label>
                                <p>{address.postal_code || '-'}</p>
                            </div>
                            <div>
                                <label className="text-sm font-medium text-muted-foreground">
                                    Country
                                </label>
                                <p>{address.country}</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Metadata */}
                <Card>
                    <CardHeader>
                        <CardTitle>Metadata</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div>
                            <label className="text-sm font-medium text-muted-foreground">
                                Type
                            </label>
                            <p>{address.address_type}</p>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="text-sm font-medium text-muted-foreground">
                                    Primary
                                </label>
                                <p>{address.is_primary ? 'Yes' : 'No'}</p>
                            </div>
                            <div>
                                <label className="text-sm font-medium text-muted-foreground">
                                    Active
                                </label>
                                <p>{address.is_active ? 'Yes' : 'No'}</p>
                            </div>
                        </div>
                        {address.owner_type && (
                            <div>
                                <label className="text-sm font-medium text-muted-foreground">
                                    Owner
                                </label>
                                <p>
                                    {address.owner_type}: {address.owner_id}
                                </p>
                            </div>
                        )}
                        {address.notes && (
                            <div>
                                <label className="text-sm font-medium text-muted-foreground">
                                    Notes
                                </label>
                                <p>{address.notes}</p>
                            </div>
                        )}
                        <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                            <div>
                                <label className="text-sm font-medium text-muted-foreground">
                                    Created
                                </label>
                                <p className="text-sm">
                                    {new Date(address.created_at).toLocaleString()}
                                </p>
                            </div>
                            <div>
                                <label className="text-sm font-medium text-muted-foreground">
                                    Updated
                                </label>
                                <p className="text-sm">
                                    {new Date(address.updated_at).toLocaleString()}
                                </p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}

export default AddressDetailView;
