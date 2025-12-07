/**
 * Module Registry
 *
 * Modules are now dynamically discovered from the backend API.
 * This file is kept for backward compatibility but no longer exports static modules.
 * See ModuleContext.tsx for the new dynamic loading approach.
 */

import type { ModuleRegistry } from '@/types';

// Deprecated: Modules are now loaded dynamically from /api/ui-config
export const builtInModules: ModuleRegistry[] = [];
