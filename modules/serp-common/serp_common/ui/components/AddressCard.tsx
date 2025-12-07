/**
 * AddressCard component - displays an address in a card format.
 */

import * as React from 'react';
import type { Address } from '../types';

// Import from shell UI components
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui';
import { MapPin, Star, Building2, Home, Truck, CreditCard } from 'lucide-react';

interface AddressCardProps {
    address: Address;
    onClick?: () => void;
    showActions?: boolean;
    onEdit?: () => void;
    onDelete?: () => void;
}

const typeIcons: Record<string, React.ReactNode> = {
    BILLING: <CreditCard className="h-4 w-4" />,
    SHIPPING: <Truck className="h-4 w-4" />,
    OFFICE: <Building2 className="h-4 w-4" />,
    HOME: <Home className="h-4 w-4" />,
    OTHER: <MapPin className="h-4 w-4" />,
};

export function AddressCard({
    address,
    onClick,
    showActions = false,
    onEdit,
    onDelete,
}: AddressCardProps) {
    return (
        <Card
            className={onClick ? 'cursor-pointer hover:bg-accent transition-colors' : ''}
            onClick={onClick}
        >
            <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        {typeIcons[address.address_type] || typeIcons.OTHER}
                        <CardTitle className="text-sm font-medium">
                            {address.label}
                        </CardTitle>
                    </div>
                    {address.is_primary && (
                        <Star className="h-4 w-4 text-yellow-500 fill-yellow-500" />
                    )}
                </div>
            </CardHeader>
            <CardContent>
                <div className="text-sm text-muted-foreground space-y-1">
                    <p>{address.street}</p>
                    <p>
                        {address.city}
                        {address.state && `, ${address.state}`}
                        {address.postal_code && ` ${address.postal_code}`}
                    </p>
                    <p>{address.country}</p>
                </div>

                {showActions && (onEdit || onDelete) && (
                    <div className="mt-4 flex gap-2">
                        {onEdit && (
                            <button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    onEdit();
                                }}
                                className="text-xs text-primary hover:underline"
                            >
                                Edit
                            </button>
                        )}
                        {onDelete && (
                            <button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    onDelete();
                                }}
                                className="text-xs text-destructive hover:underline"
                            >
                                Delete
                            </button>
                        )}
                    </div>
                )}
            </CardContent>
        </Card>
    );
}

export default AddressCard;
