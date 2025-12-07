import * as React from 'react';
import { cn } from '@/lib/utils';

export interface ButtonProps
    extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'default' | 'primary' | 'secondary' | 'destructive' | 'outline' | 'ghost';
    size?: 'default' | 'sm' | 'lg' | 'icon';
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = 'default', size = 'default', ...props }, ref) => {
        const variantClasses = {
            default: 'bg-background text-foreground hover:bg-muted',
            primary: 'bg-primary text-primary-foreground hover:bg-primary/90',
            secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
            destructive:
                'bg-destructive text-destructive-foreground hover:bg-destructive/90',
            outline: 'border border-input bg-background hover:bg-accent hover:text-accent-foreground',
            ghost: 'hover:bg-accent hover:text-accent-foreground',
        };

        const sizeClasses = {
            default: 'h-10 px-4 py-2',
            sm: 'h-9 rounded-md px-3',
            lg: 'h-11 rounded-md px-8',
            icon: 'h-10 w-10',
        };

        return (
            <button
                className={cn(
                    'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50',
                    variantClasses[variant],
                    sizeClasses[size],
                    className
                )}
                ref={ref}
                {...props}
            />
        );
    }
);

Button.displayName = 'Button';

export { Button };
