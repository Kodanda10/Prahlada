export interface HierarchyNode {
    id: string;
    name: string;
    lat: number;
    lon: number;
    type: string;
    parentId: string | null;
}

/**
 * Get nodes visible at current hierarchy level
 * Returns the focused node and its direct children
 */
export function getVisibleNodes(
    hierarchyData: HierarchyNode[],
    focusTarget: HierarchyNode | null
): HierarchyNode[] {
    if (!focusTarget) {
        // Global view - return all nodes
        return hierarchyData;
    }

    // Get direct children of focus target
    const children = getChildren(hierarchyData, focusTarget.id);

    // Return focus target + its children
    return [focusTarget, ...children];
}

/**
 * Build breadcrumb trail from node to root
 */
export function getBreadcrumbs(
    hierarchyData: HierarchyNode[],
    nodeId: string
): string[] {
    const breadcrumbs: string[] = [];
    let currentId: string | null = nodeId;

    while (currentId) {
        const node = hierarchyData.find(n => n.id === currentId);
        if (!node) break;

        breadcrumbs.unshift(node.name);
        currentId = node.parentId;
    }

    return breadcrumbs;
}

/**
 * Get direct children of a node
 */
export function getChildren(
    hierarchyData: HierarchyNode[],
    parentId: string | null
): HierarchyNode[] {
    return hierarchyData.filter(node => node.parentId === parentId);
}
