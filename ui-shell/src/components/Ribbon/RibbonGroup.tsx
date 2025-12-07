'use client';

import type { RibbonGroup as RibbonGroupType } from '@/types';
import { RibbonButton } from './RibbonButton';

interface RibbonGroupProps {
    group: RibbonGroupType;
}

/**
 * Ribbon group containing related buttons
 */
export function RibbonGroup({ group }: RibbonGroupProps) {
    return (
        <div className="flex flex-col pr-4 last:border-r-0" style={{ borderRight: '1px solid rgba(255, 255, 255, 0.1)' }}>
            <div className="flex space-x-1">
                {group.buttons.map((button) => (
                    <RibbonButton key={button.buttonId} button={button} />
                ))}
            </div>
            <span className="mt-1 text-center text-xs text-gray-400">
                {group.groupLabel}
            </span>
        </div>
    );
}
