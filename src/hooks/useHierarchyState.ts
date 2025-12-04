import { useState } from 'react';
import type { HierarchyNode } from '../utils/hierarchyFilter';
import { getChildren } from '../utils/hierarchyFilter';

export type HierarchyLevel = 'global' | 'state' | 'district' | 'assembly' | 'village';

export interface HierarchyState {
    currentLevel: HierarchyLevel;
    focusTarget: HierarchyNode | null;
    visibleNodes: HierarchyNode[];
    breadcrumbs: string[];
}

export function useHierarchyState(hierarchyData: HierarchyNode[]) {
    const [focusTarget, setFocusTarget] = useState<HierarchyNode | null>(null);

    const drillDown = (node: HierarchyNode) => {
        setFocusTarget(node);
    };

    const drillUp = () => {
        if (!focusTarget || !focusTarget.parentId) {
            setFocusTarget(null);
            return;
        }

        const parent = hierarchyData.find(n => n.id === focusTarget.parentId);
        setFocusTarget(parent || null);
    };

    const resetToGlobal = () => {
        setFocusTarget(null);
    };

    // Calculate visible nodes
    const visibleNodes = focusTarget
        ? [focusTarget, ...getChildren(hierarchyData, focusTarget.id)]
        : hierarchyData;

    // Calculate breadcrumbs
    const breadcrumbs: string[] = [];
    let currentId: string | null = focusTarget?.id || null;
    while (currentId) {
        const node = hierarchyData.find(n => n.id === currentId);
        if (!node) break;
        breadcrumbs.unshift(node.name);
        currentId = node.parentId;
    }

    // Determine current level
    let currentLevel: HierarchyLevel = 'global';
    if (focusTarget) {
        const typeToLevel: Record<string, HierarchyLevel> = {
            'state': 'state',
            'district': 'district',
            'ac': 'assembly',
            'gp': 'village',
            'village': 'village'
        };
        currentLevel = typeToLevel[focusTarget.type] || 'global';
    }

    return {
        focusTarget,
        visibleNodes,
        breadcrumbs,
        currentLevel,
        drillDown,
        drillUp,
        resetToGlobal
    };
}
