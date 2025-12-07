/**
 * AddressEditView - form for creating/editing addresses.
 */

import * as React from 'react';
import type { Address, AddressCreateInput, AddressType } from '../types';
import { getAddress, createAddress, updateAddress } from '../api/addresses';

// Import from shell UI components
import { Button, Card, CardContent, CardHeader, CardTitle, Input, Label } from '@/components/ui';
import { ArrowLeft, Save } from 'lucide-react';

// Next.js navigation
import { useRouter, useParams } from 'next/navigation';

const ADDRESS_TYPES: AddressType[] = ['BILLING', 'SHIPPING', 'OFFICE', 'HOME', 'OTHER'];

export function AddressEditView() {
    const router = useRouter();
    const params = useParams();
    const addressId = params?.id as string | undefined;
    const isNew = !addressId || addressId === 'new';

    const [loading, setLoading] = React.useState(!isNew);
    const [saving, setSaving] = React.useState(false);
    const [error, setError] = React.useState<string | null>(null);

    // Form state
    const [formData, setFormData] = React.useState<AddressCreateInput>({
        label: '',
        street: '',
        city: '',
        country: 'US',
        state: '',
        postal_code: '',
        address_type: 'OTHER',
        is_primary: false,
        notes: '',
    });

    // Load existing address if editing
    React.useEffect(() => {
        async function loadAddress() {
            if (isNew || !addressId) return;

            try {
                setLoading(true);
                setError(null);
                const data = await getAddress(addressId);
                setFormData({
                    label: data.label,
                    street: data.street,
                    city: data.city,
                    country: data.country,
                    state: data.state || '',
                    postal_code: data.postal_code || '',
                    address_type: data.address_type,
                    is_primary: data.is_primary,
                    notes: data.notes || '',
                });
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load address');
            } finally {
                setLoading(false);
            }
        }

        loadAddress();
    }, [addressId, isNew]);

    const handleChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
    ) => {
        const { name, value, type } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        try {
            setSaving(true);
            setError(null);

            if (isNew) {
                await createAddress(formData);
            } else if (addressId) {
                await updateAddress(addressId, formData);
            }

            router.push('/common/addresses');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to save address');
        } finally {
            setSaving(false);
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

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center gap-4">
                <Button variant="ghost" size="sm" onClick={handleBack}>
                    <ArrowLeft className="h-4 w-4" />
                </Button>
                <div>
                    <h1 className="text-2xl font-bold">
                        {isNew ? 'New Address' : 'Edit Address'}
                    </h1>
                    <p className="text-muted-foreground">
                        {isNew
                            ? 'Create a new address'
                            : 'Update address details'}
                    </p>
                </div>
            </div>

            {/* Error */}
            {error && (
                <div className="bg-destructive/10 text-destructive p-4 rounded-lg">
                    {error}
                </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit}>
                <Card>
                    <CardHeader>
                        <CardTitle>Address Details</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {/* Label and Type */}
                        <div className="grid gap-4 md:grid-cols-2">
                            <div className="space-y-2">
                                <Label htmlFor="label">Label *</Label>
                                <Input
                                    id="label"
                                    name="label"
                                    value={formData.label}
                                    onChange={handleChange}
                                    placeholder="e.g., Main Office"
                                    required
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="address_type">Type</Label>
                                <select
                                    id="address_type"
                                    name="address_type"
                                    value={formData.address_type}
                                    onChange={handleChange}
                                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                                >
                                    {ADDRESS_TYPES.map((type) => (
                                        <option key={type} value={type}>
                                            {type}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        {/* Street */}
                        <div className="space-y-2">
                            <Label htmlFor="street">Street *</Label>
                            <Input
                                id="street"
                                name="street"
                                value={formData.street}
                                onChange={handleChange}
                                placeholder="123 Main St"
                                required
                            />
                        </div>

                        {/* City, State */}
                        <div className="grid gap-4 md:grid-cols-2">
                            <div className="space-y-2">
                                <Label htmlFor="city">City *</Label>
                                <Input
                                    id="city"
                                    name="city"
                                    value={formData.city}
                                    onChange={handleChange}
                                    placeholder="New York"
                                    required
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="state">State</Label>
                                <Input
                                    id="state"
                                    name="state"
                                    value={formData.state || ''}
                                    onChange={handleChange}
                                    placeholder="NY"
                                />
                            </div>
                        </div>

                        {/* Postal Code, Country */}
                        <div className="grid gap-4 md:grid-cols-2">
                            <div className="space-y-2">
                                <Label htmlFor="postal_code">Postal Code</Label>
                                <Input
                                    id="postal_code"
                                    name="postal_code"
                                    value={formData.postal_code || ''}
                                    onChange={handleChange}
                                    placeholder="10001"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="country">Country *</Label>
                                <Input
                                    id="country"
                                    name="country"
                                    value={formData.country}
                                    onChange={handleChange}
                                    placeholder="US"
                                    maxLength={2}
                                    required
                                />
                            </div>
                        </div>

                        {/* Primary checkbox */}
                        <div className="flex items-center gap-2">
                            <input
                                id="is_primary"
                                name="is_primary"
                                type="checkbox"
                                checked={formData.is_primary}
                                onChange={handleChange}
                                className="h-4 w-4"
                            />
                            <Label htmlFor="is_primary" className="font-normal">
                                Set as primary address
                            </Label>
                        </div>

                        {/* Notes */}
                        <div className="space-y-2">
                            <Label htmlFor="notes">Notes</Label>
                            <textarea
                                id="notes"
                                name="notes"
                                value={formData.notes || ''}
                                onChange={handleChange}
                                placeholder="Additional notes..."
                                rows={3}
                                className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                            />
                        </div>

                        {/* Actions */}
                        <div className="flex justify-end gap-2 pt-4">
                            <Button
                                type="button"
                                variant="outline"
                                onClick={handleBack}
                                disabled={saving}
                            >
                                Cancel
                            </Button>
                            <Button type="submit" disabled={saving}>
                                {saving ? (
                                    <div className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full mr-2" />
                                ) : (
                                    <Save className="h-4 w-4 mr-2" />
                                )}
                                {isNew ? 'Create' : 'Save'}
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            </form>
        </div>
    );
}

export default AddressEditView;
