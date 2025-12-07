'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { Check } from 'lucide-react';

export interface CheckboxProps
    extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type' | 'onChange'> {
    label?: string;
    onChange?: (checked: boolean) => void;
}

const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
    ({ className, label, onChange, checked, ...props }, ref) => {
        const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
            onChange?.(e.target.checked);
        };

        return (
            <label className="inline-flex items-center gap-2 cursor-pointer">
                <div className="relative">
                    <input
                        type="checkbox"
                        className="peer sr-only"
                        ref={ref}
                        checked={checked}
                        onChange={handleChange}
                        {...props}
                    />
                    <div
                        className={cn(
                            'h-4 w-4 shrink-0 rounded-sm border border-input ring-offset-background',
                            'peer-focus-visible:outline-none peer-focus-visible:ring-2 peer-focus-visible:ring-ring peer-focus-visible:ring-offset-2',
                            'peer-disabled:cursor-not-allowed peer-disabled:opacity-50',
                            'peer-checked:bg-primary peer-checked:border-primary',
                            className
                        )}
                    />
                    <Check
                        className={cn(
                            'absolute top-0 left-0 h-4 w-4 text-primary-foreground opacity-0 peer-checked:opacity-100 pointer-events-none'
                        )}
                    />
                </div>
                {label && (
                    <span className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                        {label}
                    </span>
                )}
            </label>
        );
    }
);

Checkbox.displayName = 'Checkbox';

export { Checkbox };
