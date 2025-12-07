'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';

export default function LogoutPage() {
    const router = useRouter();
    const { logout } = useAuth();

    useEffect(() => {
        const performLogout = async () => {
            await logout();
            router.push('/login');
        };

        performLogout();
    }, [logout, router]);

    return (
        <div className="flex min-h-screen items-center justify-center">
            <div className="text-center">
                <p className="text-lg">Logging out...</p>
            </div>
        </div>
    );
}
