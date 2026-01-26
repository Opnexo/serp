/**
 * PM Module Bundle Entry Point
 *
 * This file is the entry point for the Vite build.
 * It exports all components and registers them with the shell's component registry.
 */

import { ComponentType } from 'react';

// Import views directly (they will be bundled)
import ProjectsListView from './views/ProjectsListView';

// Module metadata
export const MODULE_ID = 'pm';
export const MODULE_NAME = 'Project Management';
export const MODULE_VERSION = '0.1.0';

/**
 * Component map - maps component names to actual components
 * The backend sends component names as strings, and this map
 * allows the shell to resolve them to actual React components
 */
export const components: Record<string, () => Promise<{ default: ComponentType<any> }>> = {
    ProjectsListView: () => Promise.resolve({ default: ProjectsListView }),
    // Placeholder views
    ProjectFormView: () =>
        Promise.resolve({
            default: () => (
                <div className="p-6">
                    <h1 className="text-2xl font-bold">New Project</h1>
                    <p className="text-muted-foreground">Coming soon...</p>
                </div>
            ),
        }),
    ProjectDetailView: () =>
        Promise.resolve({
            default: () => (
                <div className="p-6">
                    <h1 className="text-2xl font-bold">Project Details</h1>
                    <p className="text-muted-foreground">Coming soon...</p>
                </div>
            ),
        }),
    TasksListView: () =>
        Promise.resolve({
            default: () => (
                <div className="p-6">
                    <h1 className="text-2xl font-bold">Tasks</h1>
                    <p className="text-muted-foreground">Coming soon...</p>
                </div>
            ),
        }),
};

/**
 * Get a component loader by name
 */
export function getComponent(
    name: string
): (() => Promise<{ default: ComponentType<any> }>) | undefined {
    return components[name];
}

// Auto-register when loaded in browser
if (typeof window !== 'undefined') {
    const registry = (window as any).__SERP_MODULE_REGISTRY__;
    if (registry) {
        console.log('📦 PM Module: Auto-registering with shell registry');
        registry.register(MODULE_ID, {
            MODULE_ID,
            MODULE_NAME,
            MODULE_VERSION,
            components,
            getComponent,
        });
    } else {
        console.warn('📦 PM Module: Registry not found, module loaded but not registered');
    }
}
