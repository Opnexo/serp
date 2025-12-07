'use client';

import { useParams } from 'next/navigation';
import { Suspense, useState, useEffect, ComponentType } from 'react';
import { useModules, componentRegistry, moduleLoader } from '@/lib/modules';
import { Spinner, Empty } from '@/components/ui';

/**
 * Dynamic module route handler
 *
 * This component:
 * 1. Matches the current path to a module route
 * 2. Ensures the module's bundle is loaded
 * 3. Renders the component from the registry
 */
export default function ModuleRoutePage() {
    const params = useParams();
    const { modules, isLoading: modulesLoading } = useModules();
    const slug = params?.slug as string[] | undefined;
    const path = slug ? `/${slug.join('/')}` : '/';

    const [Component, setComponent] = useState<ComponentType<any> | null>(null);
    const [isLoadingComponent, setIsLoadingComponent] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Find matching route from registered modules
    const matchedRoute = (() => {
        for (const mod of modules) {
            for (const route of mod.routes) {
                // Simple path matching (supports :id params)
                const routePattern = route.path
                    .replace(/:[^/]+/g, '[^/]+')
                    .replace(/\//g, '\\/');
                const regex = new RegExp(`^${routePattern}$`);
                if (regex.test(path)) {
                    return { module: mod, route };
                }
            }
        }
        return null;
    })();

    // Load the component when route matches
    useEffect(() => {
        if (modulesLoading) return;
        if (!matchedRoute) {
            setIsLoadingComponent(false);
            return;
        }

        const { module: mod, route } = matchedRoute;
        const componentName = route.component as unknown as string;

        async function loadComponent() {
            setIsLoadingComponent(true);
            setError(null);

            try {
                // Ensure the module bundle is loaded
                console.log(`🔵 Loading bundle for module: ${mod.moduleId}`);
                const bundleLoaded = await moduleLoader.ensureBundleLoaded(mod.moduleId);

                if (!bundleLoaded) {
                    setError(`Failed to load module bundle for '${mod.moduleId}'`);
                    setIsLoadingComponent(false);
                    return;
                }

                // Get the component loader from the registry
                console.log(`🔵 Getting component: ${componentName} from ${mod.moduleId}`);
                const componentLoader = componentRegistry.getComponent(mod.moduleId, componentName);

                if (!componentLoader) {
                    setError(
                        `Component '${componentName}' not found in module '${mod.moduleId}'`
                    );
                    setIsLoadingComponent(false);
                    return;
                }

                // Load the component
                const componentModule = await componentLoader();
                setComponent(() => componentModule.default);
                console.log(`✅ Component loaded: ${componentName}`);
            } catch (err) {
                console.error('Error loading component:', err);
                setError(err instanceof Error ? err.message : 'Failed to load component');
            } finally {
                setIsLoadingComponent(false);
            }
        }

        loadComponent();
    }, [matchedRoute, modulesLoading]);

    // Still loading modules config
    if (modulesLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Spinner size="lg" />
                <span className="ml-2 text-muted-foreground">Loading modules...</span>
            </div>
        );
    }

    // No matching route
    if (!matchedRoute) {
        return (
            <div className="p-6">
                <Empty
                    title="Page not found"
                    description={`No module route found for: ${path}`}
                />
            </div>
        );
    }

    // Loading component
    if (isLoadingComponent) {
        return (
            <div className="flex items-center justify-center h-64">
                <Spinner size="lg" />
                <span className="ml-2 text-muted-foreground">
                    Loading {matchedRoute.route.component as unknown as string}...
                </span>
            </div>
        );
    }

    // Error loading component
    if (error) {
        return (
            <div className="p-6">
                <Empty
                    title="Failed to load component"
                    description={error}
                />
                <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                    <p className="font-medium">Debug info:</p>
                    <ul className="list-disc list-inside mt-2">
                        <li>Module: {matchedRoute.module.moduleId}</li>
                        <li>Component: {matchedRoute.route.component as unknown as string}</li>
                        <li>Path: {path}</li>
                        <li>Bundle loaded: {componentRegistry.has(matchedRoute.module.moduleId) ? 'Yes' : 'No'}</li>
                    </ul>
                </div>
            </div>
        );
    }

    // Component not found
    if (!Component) {
        return (
            <div className="p-6">
                <Empty
                    title="Component not available"
                    description={`The component for this route could not be loaded.`}
                />
            </div>
        );
    }

    // Render the component
    return (
        <Suspense
            fallback={
                <div className="flex items-center justify-center h-64">
                    <Spinner size="lg" />
                </div>
            }
        >
            <Component />
        </Suspense>
    );
}
