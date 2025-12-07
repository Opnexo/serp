'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import {
    Building2,
    User,
    ArrowLeft,
    Save,
    X,
} from 'lucide-react';
import {
    Button,
    Input,
    Card,
    CardHeader,
    CardTitle,
    CardContent,
    Spinner,
    Select,
    Checkbox,
} from '@/components/ui';
import { getPartner, updatePartner } from '../api/partners';

const mockPartners_unused = [
    {
        id: '1',
        name: 'Acme Corporation',
        partnerType: 'COMPANY',
        isCustomer: true,
        isSupplier: false,
        isActive: true,
        email: 'contact@acme.com',
        phone: '+1 555-0100',
        industry: 'Technology',
        website: 'https://acme.com',
        taxId: '12-3456789',
        address: {
            street: '123 Tech Street',
            city: 'San Francisco',
            state: 'CA',
            postalCode: '94105',
            country: 'USA',
        },
    },
];

interface Partner {
    id: string;
    name: string;
    partnerType: string;
    isCustomer: boolean;
    isSupplier: boolean;
    isActive: boolean;
    email?: string;
    phone?: string;
    industry?: string;
    website?: string;
    taxId?: string;
    address?: {
        street?: string;
        city?: string;
        state?: string;
        postalCode?: string;
        country?: string;
    };
}

interface PartnerFormData {
    name: string;
    partnerType: string;
    isCustomer: boolean;
    isSupplier: boolean;
    isActive: boolean;
    email: string;
    phone: string;
    industry: string;
    website: string;
    taxId: string;
    street: string;
    city: string;
    state: string;
    postalCode: string;
    country: string;
}

export default function PartnerEditView() {
    const router = useRouter();
    const params = useParams();
    const partnerId = params?.id as string;
    const [partner, setPartner] = useState<Partner | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Initialize form data
    const [formData, setFormData] = useState<PartnerFormData>({
        name: '',
        partnerType: 'COMPANY',
        isCustomer: false,
        isSupplier: false,
        isActive: true,
        email: '',
        phone: '',
        industry: '',
        website: '',
        taxId: '',
        street: '',
        city: '',
        state: '',
        postalCode: '',
        country: '',
    });

    useEffect(() => {
        const fetchPartner = async () => {
            if (!partnerId) return;
            try {
                setIsLoading(true);
                const data = await getPartner(partnerId);
                setPartner(data);
                setFormData({
                    name: data.name || '',
                    partnerType: data.partnerType || 'COMPANY',
                    isCustomer: data.isCustomer || false,
                    isSupplier: data.isSupplier || false,
                    isActive: data.isActive !== undefined ? data.isActive : true,
                    email: data.email || '',
                    phone: data.phone || '',
                    industry: data.industry || '',
                    website: data.website || '',
                    taxId: data.taxId || '',
                    street: data.address?.street || '',
                    city: data.address?.city || '',
                    state: data.address?.state || '',
                    postalCode: data.address?.postalCode || '',
                    country: data.address?.country || '',
                });
                setError(null);
            } catch (err) {
                console.error('Failed to load partner:', err);
                setError('Failed to load partner');
            } finally {
                setIsLoading(false);
            }
        };
        fetchPartner();
    }, [partnerId]);

    const handleInputChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
    ) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleCheckboxChange = (name: string, checked: boolean) => {
        setFormData((prev) => ({ ...prev, [name]: checked }));
    };

    const handleSelectChange = (name: string, value: string) => {
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleSave = async () => {
        setIsSaving(true);
        try {
            await updatePartner(partnerId, formData);
            router.push(`/crm/partners/${partnerId}`);
        } catch (error) {
            console.error('Error saving partner:', error);
            alert('Failed to save partner. Please try again.');
        } finally {
            setIsSaving(false);
        }
    };

    const handleCancel = () => {
        router.push(`/crm/partners/${partnerId}`);
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <Spinner size="lg" />
            </div>
        );
    }

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <Spinner size="lg" />
            </div>
        );
    }

    if (error || !partner) {
        return (
            <div className="p-6">
                <Card>
                    <CardContent className="py-12 text-center">
                        <p className="text-red-600 mb-4">{error || 'Partner not found'}</p>
                        <Button variant="outline" onClick={() => router.push('/crm/partners')}>
                            <ArrowLeft className="h-4 w-4 mr-2" />
                            Back to Partners
                        </Button>
                    </CardContent>
                </Card>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Button variant="ghost" size="icon" onClick={handleCancel}>
                        <ArrowLeft className="h-5 w-5" />
                    </Button>
                    <div>
                        <h1 className="text-2xl font-bold">Edit Partner</h1>
                        <p className="text-muted-foreground">{partner.name}</p>
                    </div>
                </div>
                <div className="flex gap-2">
                    <Button variant="outline" onClick={handleCancel} disabled={isSaving}>
                        <X className="h-4 w-4 mr-2" />
                        Cancel
                    </Button>
                    <Button variant="primary" onClick={handleSave} disabled={isSaving}>
                        {isSaving ? (
                            <Spinner size="sm" className="mr-2" />
                        ) : (
                            <Save className="h-4 w-4 mr-2" />
                        )}
                        Save
                    </Button>
                </div>
            </div>

            {/* Form */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Basic Information */}
                <Card>
                    <CardHeader>
                        <CardTitle>Basic Information</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div>
                            <label className="text-sm font-medium">
                                Partner Name <span className="text-destructive">*</span>
                            </label>
                            <Input
                                name="name"
                                value={formData.name}
                                onChange={handleInputChange}
                                placeholder="Enter partner name"
                                className="mt-1"
                            />
                        </div>

                        <div>
                            <label className="text-sm font-medium">
                                Partner Type <span className="text-destructive">*</span>
                            </label>
                            <Select
                                value={formData.partnerType}
                                onChange={(value) => handleSelectChange('partnerType', value)}
                                options={[
                                    { value: 'COMPANY', label: 'Company' },
                                    { value: 'INDIVIDUAL', label: 'Individual' },
                                ]}
                                className="mt-1"
                            />
                        </div>

                        <div>
                            <label className="text-sm font-medium">Industry</label>
                            <Input
                                name="industry"
                                value={formData.industry}
                                onChange={handleInputChange}
                                placeholder="e.g., Technology, Manufacturing"
                                className="mt-1"
                            />
                        </div>

                        <div>
                            <label className="text-sm font-medium">Tax ID</label>
                            <Input
                                name="taxId"
                                value={formData.taxId}
                                onChange={handleInputChange}
                                placeholder="Enter tax identification number"
                                className="mt-1"
                            />
                        </div>

                        <div className="space-y-2">
                            <div className="flex items-center space-x-2">
                                <Checkbox
                                    id="isCustomer"
                                    checked={formData.isCustomer}
                                    onChange={(checked) =>
                                        handleCheckboxChange('isCustomer', checked)
                                    }
                                />
                                <label htmlFor="isCustomer" className="text-sm font-medium">
                                    Customer
                                </label>
                            </div>
                            <div className="flex items-center space-x-2">
                                <Checkbox
                                    id="isSupplier"
                                    checked={formData.isSupplier}
                                    onChange={(checked) =>
                                        handleCheckboxChange('isSupplier', checked)
                                    }
                                />
                                <label htmlFor="isSupplier" className="text-sm font-medium">
                                    Supplier
                                </label>
                            </div>
                            <div className="flex items-center space-x-2">
                                <Checkbox
                                    id="isActive"
                                    checked={formData.isActive}
                                    onChange={(checked) =>
                                        handleCheckboxChange('isActive', checked)
                                    }
                                />
                                <label htmlFor="isActive" className="text-sm font-medium">
                                    Active
                                </label>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Contact Information */}
                <Card>
                    <CardHeader>
                        <CardTitle>Contact Information</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div>
                            <label className="text-sm font-medium">Email</label>
                            <Input
                                name="email"
                                type="email"
                                value={formData.email}
                                onChange={handleInputChange}
                                placeholder="email@example.com"
                                className="mt-1"
                            />
                        </div>

                        <div>
                            <label className="text-sm font-medium">Phone</label>
                            <Input
                                name="phone"
                                type="tel"
                                value={formData.phone}
                                onChange={handleInputChange}
                                placeholder="+1 555-0100"
                                className="mt-1"
                            />
                        </div>

                        <div>
                            <label className="text-sm font-medium">Website</label>
                            <Input
                                name="website"
                                type="url"
                                value={formData.website}
                                onChange={handleInputChange}
                                placeholder="https://example.com"
                                className="mt-1"
                            />
                        </div>
                    </CardContent>
                </Card>

                {/* Address Information */}
                <Card className="lg:col-span-2">
                    <CardHeader>
                        <CardTitle>Address</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div>
                            <label className="text-sm font-medium">Street Address</label>
                            <Input
                                name="street"
                                value={formData.street}
                                onChange={handleInputChange}
                                placeholder="123 Main Street"
                                className="mt-1"
                            />
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            <div>
                                <label className="text-sm font-medium">City</label>
                                <Input
                                    name="city"
                                    value={formData.city}
                                    onChange={handleInputChange}
                                    placeholder="City"
                                    className="mt-1"
                                />
                            </div>
                            <div>
                                <label className="text-sm font-medium">State/Province</label>
                                <Input
                                    name="state"
                                    value={formData.state}
                                    onChange={handleInputChange}
                                    placeholder="State"
                                    className="mt-1"
                                />
                            </div>
                            <div>
                                <label className="text-sm font-medium">Postal Code</label>
                                <Input
                                    name="postalCode"
                                    value={formData.postalCode}
                                    onChange={handleInputChange}
                                    placeholder="12345"
                                    className="mt-1"
                                />
                            </div>
                            <div>
                                <label className="text-sm font-medium">Country</label>
                                <Input
                                    name="country"
                                    value={formData.country}
                                    onChange={handleInputChange}
                                    placeholder="Country"
                                    className="mt-1"
                                />
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
