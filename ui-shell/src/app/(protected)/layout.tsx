'use client';

import { AuthGuard } from '@/lib/auth';
import { Shell } from '@/components/Shell';
import { Ribbon } from '@/components/Ribbon';

export default function ProtectedLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <AuthGuard>
            <Shell>
                <Ribbon />
                <main className="flex-1 overflow-auto p-6">{children}</main>
            </Shell>
        </AuthGuard>
    );
}
