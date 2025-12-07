// Type definitions for module system

import type { ComponentType } from 'react';

export interface ModuleInfo {
    moduleId: string;
    moduleName: string;
    version: string;
    icon: string;
    description?: string;
}

export interface RibbonAction {
    type: 'navigate' | 'modal' | 'command' | 'function';
    route?: string;
    modalId?: string;
    commandId?: string;
    handler?: () => void | Promise<void>;
}

export interface RibbonButton {
    buttonId: string;
    label: string;
    icon: string;
    permission?: string;
    action: RibbonAction;
    variant?: 'default' | 'primary' | 'secondary' | 'destructive';
    size?: 'sm' | 'default' | 'lg';
    buttonOrder: number;
    disabled?: boolean;
    tooltip?: string;
}

export interface RibbonGroup {
    groupId: string;
    groupLabel: string;
    groupOrder: number;
    buttons: RibbonButton[];
}

export interface RibbonTab {
    tabId: string;
    tabLabel: string;
    tabIcon: string;
    tabOrder: number;
    groups: RibbonGroup[];
}

export interface ModuleRoute {
    routeId: string;
    path: string;
    permission?: string;
    /**
     * Component reference - can be either:
     * - A string (component name from backend config, resolved via componentRegistry)
     * - A dynamic import function (for local/bundled modules)
     */
    component: string | (() => Promise<{ default: ComponentType<any> }>);
    exact?: boolean;
}

export interface ModuleRegistry {
    moduleId: string;
    moduleName: string;
    version: string;
    icon: string;
    description?: string;
    ribbon: RibbonTab;
    routes: ModuleRoute[];
    permissions: string[];
}

export interface LoadedModule extends ModuleRegistry {
    loaded: boolean;
    error?: Error;
}
