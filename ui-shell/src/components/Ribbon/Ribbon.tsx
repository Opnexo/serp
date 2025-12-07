'use client';

import { useState } from 'react';
import { usePathname } from 'next/navigation';
import { useModules } from '@/lib/modules';
import { RibbonTabs } from './RibbonTabs';
import { RibbonContent } from './RibbonContent';

/**
 * Ribbon toolbar component (Microsoft Office-style)
 */
export function Ribbon() {
    const pathname = usePathname();
    const { modules } = useModules();
    const [activeTabId, setActiveTabId] = useState<string | null>(null);

    // Auto-select tab based on route
    const activeModule = modules.find((m) =>
        pathname?.startsWith(`/${m.moduleId}`)
    );

    const currentTabId = activeTabId || activeModule?.ribbon.tabId || null;
    const currentTab = modules.find((m) => m.ribbon.tabId === currentTabId);

    return (
        <div className="border-b border-gray-700 bg-[#2b2b2b]">
            {/* Ribbon Tabs */}
            <RibbonTabs
                modules={modules}
                activeTabId={currentTabId}
                onTabChange={setActiveTabId}
            />

            {/* Ribbon Content */}
            {currentTab && (
                <RibbonContent ribbon={currentTab.ribbon} />
            )}
        </div>
    );
}
