
import React from 'react';
import { motion } from 'framer-motion';

interface Node {
  id: string;
  label: string;
  level: 1 | 2 | 3 | 4 | 5; // Dist, Assembly, Block, GP, Village
  x: number;
  y: number;
  color: string;
}

interface Link {
  source: string;
  target: string;
}

// Full Hierarchy Data: District -> Assembly -> Block -> GP -> Village
// Strictly Hindi Labels with English Numerals for counts
const NODES: Node[] = [
  // Level 1: District (जिला)
  { id: 'd1', label: 'रायगढ़ (142)', level: 1, x: 5, y: 50, color: '#8BF5E6' },
  
  // Level 2: Assembly (विधानसभा)
  { id: 'a1', label: 'खरसिया (78)', level: 2, x: 25, y: 30, color: '#3b82f6' },
  { id: 'a2', label: 'रायगढ़ शहर (64)', level: 2, x: 25, y: 70, color: '#3b82f6' },

  // Level 3: Block (विकासखंड)
  { id: 'b1', label: 'खरसिया ब्लॉक (45)', level: 3, x: 45, y: 20, color: '#a855f7' },
  { id: 'b2', label: 'तमनार (33)', level: 3, x: 45, y: 40, color: '#a855f7' },
  { id: 'b3', label: 'नगर निगम (64)', level: 3, x: 45, y: 70, color: '#a855f7' },

  // Level 4: GP / Zone (ग्राम पंचायत)
  { id: 'g1', label: 'जोबी (12)', level: 4, x: 65, y: 10, color: '#ec4899' },
  { id: 'g2', label: 'सोनबरसा (08)', level: 4, x: 65, y: 25, color: '#ec4899' },
  { id: 'g3', label: 'गांधी नगर (20)', level: 4, x: 65, y: 60, color: '#ec4899' },

  // Level 5: Village / Ward (ग्राम/वार्ड)
  { id: 'v1', label: 'ग्राम जोबी (05)', level: 5, x: 85, y: 5, color: '#fbbf24' },
  { id: 'v2', label: 'बानीपाथर (07)', level: 5, x: 85, y: 15, color: '#fbbf24' },
  { id: 'v3', label: 'वार्ड 04 (10)', level: 5, x: 85, y: 55, color: '#fbbf24' },
  { id: 'v4', label: 'वार्ड 06 (10)', level: 5, x: 85, y: 65, color: '#fbbf24' },
];

const LINKS: Link[] = [
  { source: 'd1', target: 'a1' },
  { source: 'd1', target: 'a2' },
  { source: 'a1', target: 'b1' },
  { source: 'a1', target: 'b2' },
  { source: 'a2', target: 'b3' },
  { source: 'b1', target: 'g1' },
  { source: 'b1', target: 'g2' },
  { source: 'b3', target: 'g3' },
  { source: 'g1', target: 'v1' },
  { source: 'g1', target: 'v2' },
  { source: 'g3', target: 'v3' },
  { source: 'g3', target: 'v4' },
];

// Function to convert hierarchical data to nodes and links
const convertHierarchicalDataToNodes = (data: any): { nodes: Node[], links: Link[] } => {
  const nodes: Node[] = [];
  const links: Link[] = [];
  let nodeIdCounter = 0;

  const processNode = (nodeData: any, level: number, parentId?: string, x = 50, y = 50): { id: string, visits: number } => {
    const nodeId = `node_${nodeIdCounter++}`;

    // First process children to get their visit counts and position them
    let totalVisits = nodeData.visits || 0;
    if (nodeData.children && Array.isArray(nodeData.children)) {
      const childCount = nodeData.children.length;
      const angleStep = (Math.PI * 2) / childCount;
      const radius = 15;

      nodeData.children.forEach((child: any, index: number) => {
        const angle = angleStep * index;
        const childX = x + Math.cos(angle) * radius;
        const childY = y + Math.sin(angle) * radius;
        const childResult = processNode(child, level + 1, nodeId, childX, childY);
        totalVisits += childResult.visits;
      });
    }

    // Create label after calculating total visits
    const label = totalVisits > 0 ? `${nodeData.name} (${totalVisits.toString().padStart(2, '0')})` : nodeData.name;

    // Color based on level
    const colors = ['#8BF5E6', '#3b82f6', '#a855f7', '#ec4899', '#fbbf24'];
    const color = colors[level - 1] || '#8BF5E6';

    nodes.push({
      id: nodeId,
      label,
      level: level as 1 | 2 | 3 | 4 | 5,
      x,
      y,
      color
    });

    if (parentId) {
      links.push({ source: parentId, target: nodeId });
    }

    return { id: nodeId, visits: totalVisits };
  };

  processNode(data, 1);

  return { nodes, links };
};

interface HierarchyMindMapProps {
  data?: any;
  width?: number;
  height?: number;
}

const HierarchyMindMap: React.FC<HierarchyMindMapProps> = ({
  data,
  width = 800,
  height = 600
}) => {
  const viewBoxWidth = 100;
  const viewBoxHeight = 100;

  // Convert hierarchical data to nodes and links, or use defaults
  const { nodes: dynamicNodes, links: dynamicLinks } = data ? convertHierarchicalDataToNodes(data) : { nodes: NODES, links: LINKS };

  const getNode = (id: string) => dynamicNodes.find((n: Node) => n.id === id);

  return (
    <div className="w-full h-full min-h-[350px] bg-[#0f172a] rounded-xl overflow-hidden border border-white/10 relative flex items-center justify-center group shadow-inner">
      
      {/* Background Grid */}
      <div className="absolute inset-0 opacity-10" 
           style={{
             backgroundImage: 'linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px)',
             backgroundSize: '20px 20px'
           }}>
      </div>

      {/* D3-like SVG */}
      <svg 
        className="w-full h-full" 
        viewBox={`0 0 ${viewBoxWidth} ${viewBoxHeight}`} 
        preserveAspectRatio="xMidYMid meet"
      >
        {/* Connections */}
        {dynamicLinks.map((link: Link, idx: number) => {
          const s = getNode(link.source);
          const t = getNode(link.target);
          if (!s || !t) return null;

          const midX = (s.x + t.x) / 2;
          const d = `M ${s.x} ${s.y} C ${midX} ${s.y}, ${midX} ${t.y}, ${t.x} ${t.y}`;

          return (
            <motion.path
              key={idx}
              d={d}
              fill="none"
              stroke="rgba(255, 255, 255, 0.15)"
              strokeWidth="0.3"
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 1 }}
              transition={{ duration: 1.5, delay: 0.2 }}
            />
          );
        })}

        {/* Nodes */}
        {dynamicNodes.map((node: Node, i: number) => (
          <motion.g 
            key={node.id} 
            className="cursor-pointer"
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: i * 0.05, type: "spring" }}
            whileHover={{ scale: 1.2 }}
          >
            {/* Outer Glow Pulse */}
            <circle cx={node.x} cy={node.y} r={2.5} fill={node.color} opacity="0.15" className="animate-pulse" />
            {/* Inner Core */}
            <circle cx={node.x} cy={node.y} r={1} fill={node.color} stroke="rgba(0,0,0,0.5)" strokeWidth="0.1" />
            
            {/* Hindi Label */}
            <text 
              x={node.x} 
              y={node.y + 3} 
              fill="#94a3b8" 
              fontSize="2.5" 
              fontFamily="Noto Sans Devanagari"
              fontWeight="500"
              textAnchor="middle"
              className="select-none font-hindi"
            >
              {node.label}
            </text>
          </motion.g>
        ))}
      </svg>

      {/* Hindi Legend */}
      <div className="absolute top-4 right-4 flex flex-col items-end gap-1 bg-black/40 p-2 rounded-lg backdrop-blur-sm border border-white/5">
        <div className="flex items-center gap-2 text-[10px] text-slate-300 font-hindi"><span className="w-1.5 h-1.5 rounded-full bg-[#8BF5E6]"></span> जिला</div>
        <div className="flex items-center gap-2 text-[10px] text-slate-300 font-hindi"><span className="w-1.5 h-1.5 rounded-full bg-[#3b82f6]"></span> विधानसभा</div>
        <div className="flex items-center gap-2 text-[10px] text-slate-300 font-hindi"><span className="w-1.5 h-1.5 rounded-full bg-[#a855f7]"></span> विकासखंड</div>
        <div className="flex items-center gap-2 text-[10px] text-slate-300 font-hindi"><span className="w-1.5 h-1.5 rounded-full bg-[#ec4899]"></span> पंचायत/जोन</div>
        <div className="flex items-center gap-2 text-[10px] text-slate-300 font-hindi"><span className="w-1.5 h-1.5 rounded-full bg-[#fbbf24]"></span> ग्राम/वार्ड</div>
      </div>
    </div>
  );
};

export default HierarchyMindMap;
