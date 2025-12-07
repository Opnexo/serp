'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import {
    Building2,
    User,
    Mail,
    Phone,
    MapPin,
    Globe,
    Calendar,
    Edit,
    ArrowLeft,
} from 'lucide-react';
import {
    Button,
    Badge,
    Card,
    CardHeader,
    CardTitle,
    CardContent,
    Spinner,
} from '@/components/ui';
import { getPartner } from '../api/partners';

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
        createdAt: '2024-01-15',
        updatedAt: '2024-11-20',
    },
    {
        id: '2',
        name: 'Global Industries Ltd',
        partnerType: 'COMPANY',
        isCustomer: true,
        isSupplier: true,
        isActive: true,
        email: 'info@globalind.com',
        phone: '+1 555-0200',
        industry: 'Manufacturing',
        website: 'https://globalind.com',
        taxId: '98-7654321',
        address: {
            street: '456 Industrial Blvd',
            city: 'Chicago',
            state: 'IL',
            postalCode: '60601',
            country: 'USA',
        },
        createdAt: '2023-06-10',
        updatedAt: '2024-12-01',
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
    createdAt?: string;
    updatedAt?: string;
}

export default function PartnerDetailView() {
    const router = useRouter();
    const params = useParams();
    const partnerId = params?.id as string;
    const [partner, setPartner] = useState<Partner | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchPartner = async () => {
            if (!partnerId) return;
            try {
                setIsLoading(true);
                const data = await getPartner(partnerId);
                setPartner(data);
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

    const handleEdit = () => {
        router.push(`/crm/partners/${partnerId}/edit`);
    };

    const handleBack = () => {
        router.push('/crm/partners');
    };

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
                        <Button variant="outline" onClick={handleBack}>
                            <ArrowLeft className="h-4 w-4 mr-2" />
                            Back to Partners
                        </Button>
                    </CardContent>
                </Card>
            </div>
        );
    }

    const getPartnerTypeBadge = (type: string) => {
        return type === 'COMPANY' ? (
            <Badge variant="primary">
                <Building2 className="h-3 w-3 mr-1" />
                Company
            </Badge>
        ) : (
            <Badge variant="secondary">
                <User className="h-3 w-3 mr-1" />
                Individual
            </Badge>
        );
    };

    const getRoleBadges = () => {
        const badges = [];
        if (partner.isCustomer) {
            badges.push(
                <Badge key="customer" variant="success" className="mr-1">
                    Customer
                </Badge>
            );
        }
        if (partner.isSupplier) {
            badges.push(
                <Badge key="supplier" variant="warning" className="mr-1">
                    Supplier
                </Badge>
            );
        }
        return badges;
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Button variant="ghost" size="icon" onClick={handleBack}>
                        <ArrowLeft className="h-5 w-5" />
                    </Button>
                    <div>
                        <h1 className="text-2xl font-bold">{partner.name}</h1>
                        <div className="flex items-center gap-2 mt-1">
                            {getPartnerTypeBadge(partner.partnerType)}
                            {getRoleBadges()}
                            <Badge variant={partner.isActive ? 'success' : 'secondary'}>
                                {partner.isActive ? 'Active' : 'Inactive'}
                            </Badge>
                        </div>
                    </div>
                </div>
                <Button variant="primary" onClick={handleEdit}>
                    <Edit className="h-4 w-4 mr-2" />
                    Edit
                </Button>
            </div>

            {/* Partner Information */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Basic Information */}
                <Card>
                    <CardHeader>
                        <CardTitle>Basic Information</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div>
                            <label className="text-sm font-medium text-muted-foreground">
                                Partner Name
                            </label>
                            <p className="mt-1">{partner.name}</p>
                        </div>
                        <div>
                            <label className="text-sm font-medium text-muted-foreground">
                                Partner Type
                            </label>
                            <p className="mt-1">{partner.partnerType}</p>
                        </div>
                        {partner.industry && (
                            <div>
                                <label className="text-sm font-medium text-muted-foreground">
                                    Industry
                                </label>
                                <p className="mt-1">{partner.industry}</p>
                            </div>
                        )}
                        {partner.taxId && (
                            <div>
                                <label className="text-sm font-medium text-muted-foreground">
                                    Tax ID
                                </label>
                                <p className="mt-1">{partner.taxId}</p>
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Contact Information */}
                <Card>
                    <CardHeader>
                        <CardTitle>Contact Information</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {partner.email && (
                            <div className="flex items-center gap-3">
                                <Mail className="h-4 w-4 text-muted-foreground" />
                                <div>
                                    <label className="text-sm font-medium text-muted-foreground">
                                        Email
                                    </label>
                                    <p className="mt-1">
                                        <a
                                            href={`mailto:${partner.email}`}
                                            className="text-primary hover:underline"
                                        >
                                            {partner.email}
                                        </a>
                                    </p>
                                </div>
                            </div>
                        )}
                        {partner.phone && (
                            <div className="flex items-center gap-3">
                                <Phone className="h-4 w-4 text-muted-foreground" />
                                <div>
                                    <label className="text-sm font-medium text-muted-foreground">
                                        Phone
                                    </label>
                                    <p className="mt-1">
                                        <a
                                            href={`tel:${partner.phone}`}
                                            className="text-primary hover:underline"
                                        >
                                            {partner.phone}
                                        </a>
                                    </p>
                                </div>
                            </div>
                        )}
                        {partner.website && (
                            <div className="flex items-center gap-3">
                                <Globe className="h-4 w-4 text-muted-foreground" />
                                <div>
                                    <label className="text-sm font-medium text-muted-foreground">
                                        Website
                                    </label>
                                    <p className="mt-1">
                                        <a
                                            href={partner.website}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-primary hover:underline"
                                        >
                                            {partner.website}
                                        </a>
                                    </p>
                                </div>
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Address Information */}
                {partner.address && (
                    <Card>
                        <CardHeader>
                            <CardTitle>Address</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="flex items-start gap-3">
                                <MapPin className="h-4 w-4 text-muted-foreground mt-1" />
                                <div>
                                    <p>{partner.address.street}</p>
                                    <p>
                                        {partner.address.city}, {partner.address.state}{' '}
                                        {partner.address.postalCode}
                                    </p>
                                    <p>{partner.address.country}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                )}

                {/* Metadata */}
                <Card>
                    <CardHeader>
                        <CardTitle>Metadata</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="flex items-center gap-3">
                            <Calendar className="h-4 w-4 text-muted-foreground" />
                            <div>
                                <label className="text-sm font-medium text-muted-foreground">
                                    Created
                                </label>
                                <p className="mt-1">
                                    {new Date(partner.createdAt).toLocaleDateString()}
                                </p>
                            </div>
                        </div>
                        <div className="flex items-center gap-3">
                            <Calendar className="h-4 w-4 text-muted-foreground" />
                            <div>
                                <label className="text-sm font-medium text-muted-foreground">
                                    Last Updated
                                </label>
                                <p className="mt-1">
                                    {new Date(partner.updatedAt).toLocaleDateString()}
                                </p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
