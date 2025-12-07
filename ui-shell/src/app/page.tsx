import { redirect } from 'next/navigation';

export default function HomePage() {
    // Redirect to login for now
    // Later this will be the dashboard
    redirect('/login');
}
