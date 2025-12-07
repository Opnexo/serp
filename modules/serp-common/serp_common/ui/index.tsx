/**
 * Common module UI entry point.
 *
 * Exports all public components, types, and utilities.
 */

// Views
export { default as AddressesListView } from './views/AddressesListView';
export { default as AddressDetailView } from './views/AddressDetailView';
export { default as AddressEditView } from './views/AddressEditView';

// Components
export { AddressPicker } from './components/AddressPicker';
export { AddressCard } from './components/AddressCard';

// API clients
export * from './api/addresses';

// Types
export * from './types';

// Module metadata
export const MODULE_ID = 'common';
export const MODULE_NAME = 'Common';
export const MODULE_VERSION = '0.1.0';

// Component map for dynamic loading
export const components = {
    AddressesListView: () => import('./views/AddressesListView'),
    AddressDetailView: () => import('./views/AddressDetailView'),
    AddressEditView: () => import('./views/AddressEditView'),
};

export function getComponent(name: string) {
    return components[name as keyof typeof components];
}
