'use client';

import { useRouter } from 'next/navigation';
import type { RibbonButton as RibbonButtonType } from '@/types';
import { PermissionGate } from '@/lib/permissions';
import { cn } from '@/lib/utils';
import * as Icons from 'lucide-react';

interface RibbonButtonProps {
    button: RibbonButtonType;
}

/**
 * Ribbon action button
 */
export function RibbonButton({ button }: RibbonButtonProps) {
    const router = useRouter();
    const Icon = (Icons as any)[button.icon] || Icons.Square;

    const handleClick = () => {
        if (button.disabled) return;

        switch (button.action.type) {
            case 'navigate':
                if (button.action.route) {
                    router.push(button.action.route);
                }
                break;
            case 'function':
                if (button.action.handler) {
                    button.action.handler();
                }
                break;
            case 'modal':
                if (button.action.modalId) {
                    // Import dynamically to avoid circular dependencies
                    import('@/lib/modals/modalRegistry').then(({ modalRegistry }) => {
                        modalRegistry.open(button.action.modalId!);
                    });
                }
                break;
            // TODO: Handle command actions
        }
    };

    const variantClasses = {
        default: 'bg-transparent text-gray-200 hover:bg-[#4a4a4a]',
        primary: 'bg-blue-600 text-white hover:bg-blue-700',
        secondary: 'bg-[#505050] text-gray-200 hover:bg-[#5a5a5a]',
        destructive: 'bg-red-600 text-white hover:bg-red-700',
    };

    const buttonContent = (
        <button
            onClick={handleClick}
            disabled={button.disabled}
            title={button.tooltip || button.label}
            className={cn(
                'flex flex-col items-center px-3 py-2 text-sm transition-colors',
                variantClasses[button.variant || 'default'],
                button.disabled && 'cursor-not-allowed opacity-50'
            )}
            style={{ borderRadius: '2px' }}
        >
            <Icon className="h-5 w-5" />
            <span className="mt-1 text-xs">{button.label}</span>
        </button>
    );

    // Wrap with permission gate if permission is specified
    if (button.permission) {
        return (
            <PermissionGate permission={button.permission}>
                {buttonContent}
            </PermissionGate>
        );
    }

    return buttonContent;
}
