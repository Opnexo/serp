/**
 * Bundle entry point for Common module.
 *
 * This file is the entry point for the Vite build.
 * It exports everything needed for the module to function.
 */

// Export registry for ribbon configuration
export { commonModuleRegistry as registry } from './registry';

// Export all components and utilities
export * from './index';

// Re-export for convenience
export { MODULE_ID, MODULE_NAME, MODULE_VERSION, components, getComponent } from './index';
