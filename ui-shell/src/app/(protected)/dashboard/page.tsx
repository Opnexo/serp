export default function DashboardPage() {
    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold">Dashboard</h1>
                <p className="text-muted-foreground">Welcome to SERP</p>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                <div className="rounded-lg border bg-card p-6">
                    <h3 className="font-semibold">Getting Started</h3>
                    <p className="mt-2 text-sm text-muted-foreground">
                        Configure your modules and start managing your business.
                    </p>
                </div>

                <div className="rounded-lg border bg-card p-6">
                    <h3 className="font-semibold">Modules</h3>
                    <p className="mt-2 text-sm text-muted-foreground">
                        Install and configure modules to extend functionality.
                    </p>
                </div>

                <div className="rounded-lg border bg-card p-6">
                    <h3 className="font-semibold">Settings</h3>
                    <p className="mt-2 text-sm text-muted-foreground">
                        Manage system settings and preferences.
                    </p>
                </div>
            </div>
        </div>
    );
}
