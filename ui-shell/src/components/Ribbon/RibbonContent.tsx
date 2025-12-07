'use client';

import type { RibbonTab } from '@/types';
import { RibbonGroup } from './RibbonGroup';

interface RibbonContentProps {
    ribbon: RibbonTab;
}

/**
 * Ribbon content area with groups and buttons
 */
export function RibbonContent({ ribbon }: RibbonContentProps) {
    return (
        <div className="flex space-x-4 bg-[#3a3a3a] px-4 py-3">
            {ribbon.groups.map((group) => (
                <RibbonGroup key={group.groupId} group={group} />
            ))}
        </div>
    );
}
