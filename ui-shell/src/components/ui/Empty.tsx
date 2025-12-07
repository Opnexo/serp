import * as React from 'react';
import { cn } from '@/lib/utils';
import { Inbox } from 'lucide-react';

export interface EmptyProps extends React.HTMLAttributes<HTMLDivElement> {
    icon?: React.ReactNode;
    title?: string;
    description?: string;
    action?: React.ReactNode;
}

function Empty({
    className,
    icon,
    title = 'No data',
    description,
    action,
    children,
    ...props
}: EmptyProps) {
    return (
        <div
            className={cn(
                'flex flex-col items-center justify-center py-12 text-center',
                className
            )}
            {...props}
        >
            <div className="text-muted-foreground mb-4">
                {icon || <Inbox className="h-12 w-12" />}
            </div>
            <h3 className="text-lg font-medium">{title}</h3>
            {description && (
                <p className="mt-1 text-sm text-muted-foreground max-w-sm">
                    {description}
                </p>
            )}
            {action && <div className="mt-4">{action}</div>}
            {children}
        </div>
    );
}

export { Empty };
