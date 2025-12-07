'use client';

import type { ModuleRegistry } from '@/types';
import { cn } from '@/lib/utils';
import * as Icons from 'lucide-react';

interface RibbonTabsProps {
    modules: ModuleRegistry[];
    activeTabId: string | null;
    onTabChange: (tabId: string) => void;
}

/**
 * Ribbon tabs row
 */
export function RibbonTabs({
    modules,
    activeTabId,
    onTabChange,
}: RibbonTabsProps) {
    return (
        <div className="flex space-x-1 px-2 pt-1">
            {modules.map((module) => {
                const Icon = (Icons as any)[module.ribbon.tabIcon] || Icons.Package;
                const isActive = module.ribbon.tabId === activeTabId;

                return (
                    <button
                        key={module.ribbon.tabId}
                        onClick={() => onTabChange(module.ribbon.tabId)}
                        className={cn(
                            'flex items-center space-x-2 rounded-t-md px-4 py-2 text-sm font-medium transition-colors',
                            isActive
                                ? 'bg-[#3a3a3a] text-white'
                                : 'text-gray-400 hover:bg-[#333333] hover:text-gray-200'
                        )}
                    >
                        <Icon className="h-4 w-4" />
                        <span>{module.ribbon.tabLabel}</span>
                    </button>
                );
            })}
        </div>
    );
}
