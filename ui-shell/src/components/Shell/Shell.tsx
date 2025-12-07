'use client';

interface ShellProps {
    children: React.ReactNode;
}

/**
 * Main application shell wrapper
 */
export function Shell({ children }: ShellProps) {
    return (
        <div className="flex h-screen flex-col overflow-hidden bg-background">
            {children}
        </div>
    );
}
