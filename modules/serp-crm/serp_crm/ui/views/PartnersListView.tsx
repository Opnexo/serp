'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
    Building2,
    User,
    Plus,
    Search,
    Mail,
    Phone,
} from 'lucide-react';
import {
    Button,
    Input,
    Badge,
    Table,
    TableHeader,
    TableBody,
    TableHead,
    TableRow,
    TableCell,
    Empty,
    Spinner,
    Card,
    CardContent,
} from '@/components/ui';
import { getPartners } from '../api/partners';

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
    },
    {
        id: '3',
        name: 'John Smith',
        partnerType: 'INDIVIDUAL',
        isCustomer: true,
        isSupplier: false,
        isActive: true,
        email: 'john.smith@email.com',
        phone: '+1 555-0300',
        industry: null,
    },
    {
        id: '4',
        name: 'Tech Solutions Inc',
        partnerType: 'COMPANY',
        isCustomer: false,
        isSupplier: true,
        isActive: true,
        email: 'sales@techsolutions.com',
        phone: '+1 555-0400',
        industry: 'IT Services',
    },
    {
        id: '5',
        name: 'Inactive Corp',
        partnerType: 'COMPANY',
        isCustomer: true,
        isSupplier: false,
        isActive: false,
        email: 'contact@inactive.com',
        phone: '+1 555-0500',
        industry: 'Retail',
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
}

export default function PartnersListView() {
    const router = useRouter();
    const [searchQuery, setSearchQuery] = useState('');
    const [partners, setPartners] = useState<Partner[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchPartners = async () => {
            try {
                setIsLoading(true);
                const data = await getPartners();
                setPartners(data);
                setError(null);
            } catch (err) {
                console.error('Failed to load partners:', err);
                setError('Failed to load partners');
            } finally {
                setIsLoading(false);
            }
        };
        fetchPartners();
    }, []);

    // Filter partners based on search query
    const filteredPartners = partners.filter(
        (partner) =>
            partner.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            partner.email?.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const handleRowClick = (partner: Partner) => {
        router.push(`/crm/partners/${partner.id}`);
    };

    const handleNewPartner = () => {
        router.push('/crm/partners/new');
    };

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

    const getRoleBadges = (partner: Partner) => {
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
            <div>
                <h1 className="text-2xl font-bold">Partners</h1>
                <p className="text-muted-foreground">
                    Manage your customers and suppliers
                </p>
            </div>

            {/* Search and Filters */}
            <Card>
                <CardContent className="pt-6">
                    <div className="flex gap-4">
                        <div className="relative flex-1 max-w-sm">
                            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                            <Input
                                placeholder="Search partners..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="pl-9"
                            />
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Partners Table */}
            <Card>
                <CardContent className="p-0">
                    {isLoading ? (
                        <div className="flex items-center justify-center py-12">
                            <Spinner size="lg" />
                        </div>
                    ) : filteredPartners.length === 0 ? (
                        <Empty
                            title="No partners found"
                            description={
                                searchQuery
                                    ? 'Try adjusting your search'
                                    : 'Get started by creating your first partner'
                            }
                            action={
                                !searchQuery && (
                                    <Button variant="primary" onClick={handleNewPartner}>
                                        <Plus className="h-4 w-4 mr-2" />
                                        New Partner
                                    </Button>
                                )
                            }
                        />
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Name</TableHead>
                                    <TableHead>Type</TableHead>
                                    <TableHead>Role</TableHead>
                                    <TableHead>Contact</TableHead>
                                    <TableHead>Industry</TableHead>
                                    <TableHead>Status</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {filteredPartners.map((partner) => (
                                    <TableRow
                                        key={partner.id}
                                        className="cursor-pointer"
                                        onClick={() => handleRowClick(partner)}
                                    >
                                        <TableCell className="font-medium">
                                            {partner.name}
                                        </TableCell>
                                        <TableCell>
                                            {getPartnerTypeBadge(partner.partnerType)}
                                        </TableCell>
                                        <TableCell>{getRoleBadges(partner)}</TableCell>
                                        <TableCell>
                                            <div className="flex flex-col gap-1 text-sm">
                                                {partner.email && (
                                                    <div className="flex items-center gap-1 text-muted-foreground">
                                                        <Mail className="h-3 w-3" />
                                                        {partner.email}
                                                    </div>
                                                )}
                                                {partner.phone && (
                                                    <div className="flex items-center gap-1 text-muted-foreground">
                                                        <Phone className="h-3 w-3" />
                                                        {partner.phone}
                                                    </div>
                                                )}
                                            </div>
                                        </TableCell>
                                        <TableCell>
                                            {partner.industry || (
                                                <span className="text-muted-foreground">—</span>
                                            )}
                                        </TableCell>
                                        <TableCell>
                                            <Badge
                                                variant={partner.isActive ? 'success' : 'secondary'}
                                            >
                                                {partner.isActive ? 'Active' : 'Inactive'}
                                            </Badge>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    )}
                </CardContent>
            </Card>

            {/* Summary */}
            <div className="text-sm text-muted-foreground">
                Showing {filteredPartners.length} of {partners.length} partners
            </div>
        </div>
    );
}
