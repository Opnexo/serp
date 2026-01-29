/**
 * DM Module Bundle Entry Point
 *
 * This file is the entry point for the Vite build.
 * It exports all components and registers them with the shell's component registry.
 */

import { ComponentType } from 'react';

// Import views directly (they will be bundled)
import DocumentsListView from './views/DocumentsListView';
import DocumentFormView from './views/DocumentFormView';
import DocumentDetailView from './views/DocumentDetailView';
import KanbanBoardView from './views/KanbanBoardView';
import TemplatesView from './views/TemplatesView';
import DocumentTypesView from './views/DocumentTypesView';
import DMProjectsListView from './views/DMProjectsListView';
import DMProjectView from './views/DMProjectView';
import StageTemplatesView from './views/StageTemplatesView';
import ExportView from './views/ExportView';

// Import widgets
import { ProjectDocumentsWidget } from './components';

// Module metadata
export const MODULE_ID = 'dm';
export const MODULE_NAME = 'Document Management';
export const MODULE_VERSION = '0.1.0';

/**
 * Component map - maps component names to actual components
 * The backend sends component names as strings, and this map
 * allows the shell to resolve them to actual React components
 */
export const components: Record<string, () => Promise<{ default: ComponentType<any> }>> = {
    // Views
    DocumentsListView: () => Promise.resolve({ default: DocumentsListView }),
    DocumentFormView: () => Promise.resolve({ default: DocumentFormView }),
    DocumentDetailView: () => Promise.resolve({ default: DocumentDetailView }),
    KanbanBoardView: () => Promise.resolve({ default: KanbanBoardView }),
    TemplatesView: () => Promise.resolve({ default: TemplatesView }),
    DocumentTypesView: () => Promise.resolve({ default: DocumentTypesView }),
    DMProjectsListView: () => Promise.resolve({ default: DMProjectsListView }),
    DMProjectView: () => Promise.resolve({ default: DMProjectView }),
    StageTemplatesView: () => Promise.resolve({ default: StageTemplatesView }),
    ExportView: () => Promise.resolve({ default: ExportView }),

    // Widgets (for PM integration)
    ProjectDocumentsWidget: () => Promise.resolve({ default: ProjectDocumentsWidget }),
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
        console.log('📦 DM Module: Auto-registering with shell registry');
        registry.register(MODULE_ID, {
            MODULE_ID,
            MODULE_NAME,
            MODULE_VERSION,
            components,
            getComponent,
        });
    } else {
        console.warn('📦 DM Module: Registry not found, module loaded but not registered');
    }
}
