import * as React from 'react';
import { cn } from '@/lib/utils';
import { ChevronDown } from 'lucide-react';

export interface SelectOption {
    value: string;
    label: string;
    disabled?: boolean;
}

export interface SelectProps
    extends Omit<React.SelectHTMLAttributes<HTMLSelectElement>, 'onChange'> {
    options: SelectOption[];
    placeholder?: string;
    error?: string;
    onChange?: (value: string) => void;
}

const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
    ({ className, options, placeholder, error, onChange, ...props }, ref) => {
        const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
            onChange?.(e.target.value);
        };

        return (
            <div className="relative w-full">
                <select
                    className={cn(
                        'flex h-10 w-full appearance-none rounded-md border border-input bg-background px-3 py-2 pr-8 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
                        error && 'border-destructive focus-visible:ring-destructive',
                        className
                    )}
                    ref={ref}
                    onChange={handleChange}
                    {...props}
                >
                    {placeholder && (
                        <option value="" disabled>
                            {placeholder}
                        </option>
                    )}
                    {options.map((option) => (
                        <option
                            key={option.value}
                            value={option.value}
                            disabled={option.disabled}
                        >
                            {option.label}
                        </option>
                    ))}
                </select>
                <ChevronDown className="absolute right-3 top-3 h-4 w-4 opacity-50 pointer-events-none" />
                {error && (
                    <p className="mt-1 text-sm text-destructive">{error}</p>
                )}
            </div>
        );
    }
);

Select.displayName = 'Select';

export { Select };
