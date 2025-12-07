'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { X } from 'lucide-react';
import { Button } from './Button';

interface ModalContextValue {
    open: boolean;
    onClose: () => void;
}

const ModalContext = React.createContext<ModalContextValue | null>(null);

function useModal() {
    const context = React.useContext(ModalContext);
    if (!context) {
        throw new Error('Modal components must be used within a Modal');
    }
    return context;
}

export interface ModalProps {
    open: boolean;
    onClose: () => void;
    children: React.ReactNode;
}

function Modal({ open, onClose, children }: ModalProps) {
    // Close on escape key
    React.useEffect(() => {
        const handleEscape = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose();
        };
        if (open) {
            document.addEventListener('keydown', handleEscape);
            document.body.style.overflow = 'hidden';
        }
        return () => {
            document.removeEventListener('keydown', handleEscape);
            document.body.style.overflow = 'unset';
        };
    }, [open, onClose]);

    if (!open) return null;

    return (
        <ModalContext.Provider value={{ open, onClose }}>
            <div className="fixed inset-0 z-50 flex items-center justify-center">
                {/* Backdrop */}
                <div
                    className="fixed inset-0 bg-black/50 backdrop-blur-sm"
                    onClick={onClose}
                    aria-hidden="true"
                />
                {/* Content */}
                {children}
            </div>
        </ModalContext.Provider>
    );
}

interface ModalContentProps extends React.HTMLAttributes<HTMLDivElement> {
    size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
}

function ModalContent({
    className,
    size = 'md',
    children,
    ...props
}: ModalContentProps) {
    const sizeClasses = {
        sm: 'max-w-sm',
        md: 'max-w-md',
        lg: 'max-w-lg',
        xl: 'max-w-xl',
        full: 'max-w-4xl',
    };

    return (
        <div
            className={cn(
                'relative z-50 w-full rounded-lg border bg-background p-6 shadow-lg animate-in fade-in-0 zoom-in-95',
                sizeClasses[size],
                className
            )}
            {...props}
        >
            {children}
        </div>
    );
}

function ModalHeader({
    className,
    children,
    ...props
}: React.HTMLAttributes<HTMLDivElement>) {
    const { onClose } = useModal();

    return (
        <div
            className={cn(
                'flex items-center justify-between space-y-1.5 pb-4',
                className
            )}
            {...props}
        >
            <div>{children}</div>
            <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6"
                onClick={onClose}
            >
                <X className="h-4 w-4" />
                <span className="sr-only">Close</span>
            </Button>
        </div>
    );
}

function ModalTitle({
    className,
    ...props
}: React.HTMLAttributes<HTMLHeadingElement>) {
    return (
        <h2
            className={cn(
                'text-lg font-semibold leading-none tracking-tight',
                className
            )}
            {...props}
        />
    );
}

function ModalDescription({
    className,
    ...props
}: React.HTMLAttributes<HTMLParagraphElement>) {
    return (
        <p
            className={cn('text-sm text-muted-foreground', className)}
            {...props}
        />
    );
}

function ModalBody({
    className,
    ...props
}: React.HTMLAttributes<HTMLDivElement>) {
    return <div className={cn('py-4', className)} {...props} />;
}

function ModalFooter({
    className,
    ...props
}: React.HTMLAttributes<HTMLDivElement>) {
    return (
        <div
            className={cn(
                'flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2 pt-4',
                className
            )}
            {...props}
        />
    );
}

export {
    Modal,
    ModalContent,
    ModalHeader,
    ModalTitle,
    ModalDescription,
    ModalBody,
    ModalFooter,
};
