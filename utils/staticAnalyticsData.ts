import { ParsedEvent } from '../types';
import { HierarchyNode } from '../components/analytics/HierarchyMindMap';
// @ts-ignore
import tweetsRaw from '../data/parsed_tweets_gemini_parser_v2.jsonl?raw';

export const loadRealTweets = (): ParsedEvent[] => {
    try {
        const lines = tweetsRaw.trim().split('\n');
        return lines.map((line: string) => {
            const raw = JSON.parse(line);
            // Map v9 data to v8 schema for frontend compatibility
            const v9Data = raw.parsed_data_v9 || {};

            return {
                ...raw,
                raw_text: raw.text || raw.raw_text,
                review_status: raw.review_status || 'pending',
                parsed_data_v8: {
                    ...v9Data,
                    // Map potentially missing or renamed fields
                    confidence: v9Data.confidence || 0.8,
                    review_status: 'pending',
                    needs_review: true,
                    visit_count: 0,
                    word_buckets: [],
                    event_type_secondary: [],
                    hierarchy_path: v9Data.location?.hierarchy_path || [],
                    location: {
                        ...v9Data.location,
                        location_type: v9Data.location?.location_type || 'district'
                    }
                },
                metadata_v8: raw.metadata_v9 ? {
                    model: raw.metadata_v9.model,
                    version: raw.metadata_v9.version,
                    processing_time_ms: 0
                } : {
                    model: 'gemini-parser-v2',
                    version: '2.1.0',
                    processing_time_ms: 0
                }
            } as ParsedEvent;
        });
    } catch (error) {
        console.warn(`Failed to load real tweets from static import:`, error);
        return [];
    }
};

export const getTweetStats = (tweets: ParsedEvent[] = loadRealTweets()) => {
    const eventTypeCounts: Record<string, number> = {};

    tweets.forEach(t => {
        const type = t.parsed_data_v8.event_type || 'Unknown';
        eventTypeCounts[type] = (eventTypeCounts[type] || 0) + 1;
    });

    return Object.entries(eventTypeCounts).map(([name, value]) => ({
        name,
        value,
        fill: '#8884d8' // Default color
    }));
};

export const getTweetTimeStats = (tweets: ParsedEvent[] = loadRealTweets()) => {
    const dateCounts: Record<string, number> = {};

    tweets.forEach(t => {
        // tweet.parsed_data_v8.event_date is usually YYYY-MM-DD
        const date = t.parsed_data_v8.event_date || t.created_at.split('T')[0] || 'Unknown';
        dateCounts[date] = (dateCounts[date] || 0) + 1;
    });

    return Object.entries(dateCounts)
        .sort((a, b) => a[0].localeCompare(b[0]))
        .slice(0, 7) // Last 7 days/entries
        .map(([name, value]) => ({
            name,
            value
        }));
};

export const getAnalyticsSummary = (tweets: ParsedEvent[] = loadRealTweets()) => {
    const uniqueDistricts = new Set<string>();
    let totalVillageVisits = 0;
    const locationVisitCounts: Record<string, number> = {};

    tweets.forEach(t => {
        const location = t.parsed_data_v8.location;
        if (location?.district) {
            uniqueDistricts.add(location.district);
        }
        if (location?.village) {
            totalVillageVisits++;
        } else if (location?.canonical) {
            // If no village, count broader canonical locations as a "visit" for summary
            locationVisitCounts[location.canonical] = (locationVisitCounts[location.canonical] || 0) + 1;
        }
    });

    // Sum up visits from canonical locations if no specific village count was available
    const totalCanonicalVisits = Object.values(locationVisitCounts).reduce((sum, count) => sum + count, 0);


    return {
        totalDistricts: uniqueDistricts.size,
        totalVillageVisits: totalVillageVisits > 0 ? totalVillageVisits : totalCanonicalVisits, // Prioritize village, fallback to canonical
        // For now, hardcode coverage as it requires external data for total possible locations
        coveragePercentage: 78 // Example based on mock value from Analytics.tsx
    };
};

export const getHierarchyData = (tweets: ParsedEvent[] = loadRealTweets()): HierarchyNode => {
    const districtsMap = new Map<string, HierarchyNode>(); // Map<DistrictName, HierarchyNode>
    const ulbBlockMap = new Map<string, HierarchyNode>(); // Map<ULB/BlockName, HierarchyNode>

    tweets.forEach(tweet => {
        const loc = tweet.parsed_data_v8.location;
        if (!loc || !loc.district) return;

        // Ensure district node exists
        if (!districtsMap.has(loc.district)) {
            districtsMap.set(loc.district, {
                id: `district-${loc.district}`,
                label: loc.district,
                level: 1,
                visits: 0,
                children: []
            });
        }
        const districtNode = districtsMap.get(loc.district)!;
        districtNode.visits++;

        // Handle ULB or Block level
        const subLocationName = loc.ulb || loc.block;
        if (subLocationName) {
            const subLocationId = `subloc-${loc.district}-${subLocationName}`;
            if (!ulbBlockMap.has(subLocationId)) {
                const newSubNode: HierarchyNode = {
                    id: subLocationId,
                    label: subLocationName,
                    level: loc.ulb ? 2 : 3, // Assuming ULB is level 2, Block level 3
                    visits: 0,
                    children: []
                };
                ulbBlockMap.set(subLocationId, newSubNode);
                districtNode.children!.push(newSubNode);
            }
            const subLocationNode = ulbBlockMap.get(subLocationId)!;
            subLocationNode.visits++;
        }
    });

    const rootChildren = Array.from(districtsMap.values()).sort((a, b) => b.visits - a.visits);

    // Placeholder root node for the entire state
    const rootVisits = rootChildren.reduce((sum, node) => sum + node.visits, 0);
    return {
        id: 'chhattisgarh',
        label: 'छत्तीसगढ़',
        level: 0 as any, // 0 is not in HierarchyNode level type (1-5), but root might be 0? // State level
        visits: rootVisits,
        children: rootChildren
    };
};
