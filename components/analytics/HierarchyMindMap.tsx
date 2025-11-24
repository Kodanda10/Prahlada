import React, { useRef, useEffect, useState, useCallback } from 'react';
import * as d3 from 'd3';
import { motion, AnimatePresence } from 'framer-motion';
import { ZoomIn, ZoomOut, Maximize2, Minimize2, RefreshCw } from 'lucide-react';

interface HierarchyNode {
  id: string;
  label: string;
  level: 1 | 2 | 3 | 4 | 5; // District, Assembly, Block, GP, Village
  visits: number;
  children?: HierarchyNode[];
  parent?: string;
}

interface D3Node extends d3.SimulationNodeDatum {
  id: string;
  label: string;
  level: number;
  visits: number;
  color: string;
  radius: number;
}

interface D3Link extends d3.SimulationLinkDatum<D3Node> {
  source: string | D3Node;
  target: string | D3Node;
}

interface HierarchyMindMapProps {
  data?: HierarchyNode;
  width?: number;
  height?: number;
}

const LEVEL_COLORS = {
  1: '#8BF5E6', // District - Neon Cyan
  2: '#3b82f6', // Assembly - Blue
  3: '#a855f7', // Block - Purple
  4: '#ec4899', // GP/Zone - Pink
  5: '#fbbf24', // Village/Ward - Amber
};

const LEVEL_LABELS_HI = {
  1: 'जिला',
  2: 'विधानसभा',
  3: 'विकासखंड',
  4: 'पंचायत/जोन',
  5: 'ग्राम/वार्ड',
};

const HierarchyMindMap: React.FC<HierarchyMindMapProps> = ({
  data,
  width = 800,
  height = 600,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedNode, setSelectedNode] = useState<D3Node | null>(null);
  const [hoveredNode, setHoveredNode] = useState<D3Node | null>(null);
  const [transform, setTransform] = useState({ k: 1, x: 0, y: 0 });
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Convert hierarchical data to flat nodes and links
  const convertToD3Data = useCallback((rootNode: HierarchyNode): { nodes: D3Node[]; links: D3Link[] } => {
    const nodes: D3Node[] = [];
    const links: D3Link[] = [];

    const traverse = (node: HierarchyNode, level: number, parentId?: string) => {
      const d3Node: D3Node = {
        id: node.id,
        label: `${node.label} (${node.visits.toString().padStart(2, '0')})`,
        level,
        visits: node.visits,
        color: LEVEL_COLORS[level as keyof typeof LEVEL_COLORS] || '#64748b',
        radius: Math.max(8, Math.min(20, 8 + node.visits / 5)),
      };

      nodes.push(d3Node);

      if (parentId) {
        links.push({ source: parentId, target: node.id });
      }

      if (node.children) {
        node.children.forEach((child) => traverse(child, level + 1, node.id));
      }
    };

    traverse(rootNode, 1);
    return { nodes, links };
  }, []);

  // Default demo data
  const defaultData: HierarchyNode = {
    id: 'd1',
    label: 'रायगढ़',
    level: 1,
    visits: 142,
    children: [
      {
        id: 'a1',
        label: 'खरसिया',
        level: 2,
        visits: 78,
        children: [
          {
            id: 'b1',
            label: 'खरसिया ब्लॉक',
            level: 3,
            visits: 45,
            children: [
              {
                id: 'g1',
                label: 'जोबी',
                level: 4,
                visits: 12,
                children: [
                  { id: 'v1', label: 'ग्राम जोबी', level: 5, visits: 5 },
                  { id: 'v2', label: 'बानीपाथर', level: 5, visits: 7 },
                ],
              },
              { id: 'g2', label: 'सोनबरसा', level: 4, visits: 8 },
            ],
          },
          { id: 'b2', label: 'तमनार', level: 3, visits: 33 },
        ],
      },
      {
        id: 'a2',
        label: 'रायगढ़ शहर',
        level: 2,
        visits: 64,
        children: [
          {
            id: 'b3',
            label: 'नगर निगम',
            level: 3,
            visits: 64,
            children: [
              {
                id: 'g3',
                label: 'गांधी नगर',
                level: 4,
                visits: 20,
                children: [
                  { id: 'v3', label: 'वार्ड 04', level: 5, visits: 10 },
                  { id: 'v4', label: 'वार्ड 06', level: 5, visits: 10 },
                ],
              },
            ],
          },
        ],
      },
    ],
  };

  const { nodes, links } = data ? convertToD3Data(data) : convertToD3Data(defaultData);

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const container = svg.append('g').attr('class', 'zoom-container');

    // Zoom behavior
    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.3, 3])
      .on('zoom', (event) => {
        container.attr('transform', event.transform);
        setTransform({ k: event.transform.k, x: event.transform.x, y: event.transform.y });
      });

    svg.call(zoom as any);

    // Force simulation
    const simulation = d3
      .forceSimulation(nodes)
      .force(
        'link',
        d3
          .forceLink<D3Node, D3Link>(links)
          .id((d) => d.id)
          .distance(100)
          .strength(0.5)
      )
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius((d: any) => d.radius + 10))
      .force('x', d3.forceX(width / 2).strength(0.05))
      .force('y', d3.forceY(height / 2).strength(0.05));

    // Create links
    const link = container
      .append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke', 'rgba(255, 255, 255, 0.15)')
      .attr('stroke-width', 2)
      .attr('stroke-opacity', 0.6);

    // Create node groups
    const node = container
      .append('g')
      .attr('class', 'nodes')
      .selectAll('g')
      .data(nodes)
      .join('g')
      .attr('cursor', 'pointer')
      .call(
        d3
          .drag<SVGGElement, D3Node>()
          .on('start', (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on('drag', (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on('end', (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          }) as any
      )
      .on('click', (event, d) => {
        event.stopPropagation();
        setSelectedNode(d);
      })
      .on('mouseenter', (event, d) => setHoveredNode(d))
      .on('mouseleave', () => setHoveredNode(null));

    // Outer glow (pulse effect)
    node
      .append('circle')
      .attr('r', (d) => d.radius + 6)
      .attr('fill', (d) => d.color)
      .attr('opacity', 0.15)
      .attr('class', 'pulse-ring');

    // Main node circle
    node
      .append('circle')
      .attr('r', (d) => d.radius)
      .attr('fill', (d) => d.color)
      .attr('stroke', 'rgba(255, 255, 255, 0.3)')
      .attr('stroke-width', 2)
      .attr('filter', 'url(#glow)');

    // Node labels
    node
      .append('text')
      .text((d) => d.label)
      .attr('text-anchor', 'middle')
      .attr('dy', (d) => d.radius + 18)
      .attr('fill', '#94a3b8')
      .attr('font-size', '12px')
      .attr('font-weight', '500')
      .attr('font-family', 'Noto Sans Devanagari, sans-serif')
      .attr('class', 'select-none');

    // Add glow filter
    const defs = svg.append('defs');
    const filter = defs.append('filter').attr('id', 'glow');
    filter
      .append('feGaussianBlur')
      .attr('stdDeviation', '3')
      .attr('result', 'coloredBlur');
    const feMerge = filter.append('feMerge');
    feMerge.append('feMergeNode').attr('in', 'coloredBlur');
    feMerge.append('feMergeNode').attr('in', 'SourceGraphic');

    // Update positions on tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      node.attr('transform', (d) => `translate(${d.x},${d.y})`);
    });

    // Pulse animation for glow rings
    const pulseAnimation = () => {
      container
        .selectAll('.pulse-ring')
        .transition()
        .duration(1500)
        .attr('r', (d: any) => d.radius + 10)
        .attr('opacity', 0)
        .transition()
        .duration(0)
        .attr('r', (d: any) => d.radius + 6)
        .attr('opacity', 0.15)
        .on('end', pulseAnimation);
    };
    pulseAnimation();

    return () => {
      simulation.stop();
    };
  }, [nodes, links, width, height]);

  const toggleFullscreen = () => {
    if (!containerRef.current) return;
    
    if (!document.fullscreenElement) {
      containerRef.current.requestFullscreen().catch(err => {
        console.error(`Error attempting to enable fullscreen: ${err.message}`);
      });
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  const handleReset = () => {
    if (svgRef.current) {
      const svg = d3.select(svgRef.current);
      svg
        .transition()
        .duration(750)
        .call(
          d3.zoom<SVGSVGElement, unknown>().transform as any,
          d3.zoomIdentity
        );
    }
  };

  const handleZoomIn = () => {
    if (svgRef.current) {
      const svg = d3.select(svgRef.current);
      svg.transition().duration(300).call(d3.zoom<SVGSVGElement, unknown>().scaleBy as any, 1.3);
    }
  };

  const handleZoomOut = () => {
    if (svgRef.current) {
      const svg = d3.select(svgRef.current);
      svg.transition().duration(300).call(d3.zoom<SVGSVGElement, unknown>().scaleBy as any, 0.7);
    }
  };

  return (
    <div 
      ref={containerRef}
      className={`relative w-full h-full min-h-[500px] bg-[#0f172a] rounded-xl overflow-hidden border border-white/10 shadow-2xl transition-all duration-500 ${isFullscreen ? 'fixed inset-0 z-[100] rounded-none border-0' : ''}`}
    >
      {/* Background Grid */}
      <div
        className="absolute inset-0 opacity-10"
        style={{
          backgroundImage:
            'linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px)',
          backgroundSize: '20px 20px',
        }}
      />

      {/* SVG Canvas */}
      <svg ref={svgRef} width={isFullscreen ? window.innerWidth : width} height={isFullscreen ? window.innerHeight : height} className="w-full h-full" />

      {/* Control Panel */}
      <div className="absolute top-4 left-4 bg-black/60 backdrop-blur-md border border-white/10 rounded-lg p-3 space-y-2">
        <div className="text-xs font-bold text-slate-200 mb-2 font-hindi">
          पदानुक्रम दृश्य
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleZoomIn}
            className="p-2 bg-white/10 hover:bg-white/20 rounded text-white transition-colors"
            title="Zoom In"
          >
            <ZoomIn size={14} />
          </button>
          <button
            onClick={handleZoomOut}
            className="p-2 bg-white/10 hover:bg-white/20 rounded text-white transition-colors"
            title="Zoom Out"
          >
            <ZoomOut size={14} />
          </button>
          <button
            onClick={handleReset}
            className="p-2 bg-white/10 hover:bg-white/20 rounded text-white transition-colors"
            title="Reset View"
          >
            <RefreshCw size={14} />
          </button>
          <button
            onClick={toggleFullscreen}
            className="p-2 bg-white/10 hover:bg-white/20 rounded text-white transition-colors"
            title={isFullscreen ? "Exit Fullscreen" : "Enter Fullscreen"}
          >
            {isFullscreen ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
          </button>
        </div>
        <div className="text-[10px] text-slate-400">
          Zoom: {transform.k.toFixed(2)}x
        </div>
      </div>

      {/* Legend */}
      <div className="absolute top-4 right-4 bg-black/60 backdrop-blur-md border border-white/10 rounded-lg p-3 space-y-2">
        <div className="text-[10px] font-bold text-slate-200 mb-2 font-hindi">
          किंवदंती
        </div>
        {Object.entries(LEVEL_LABELS_HI).map(([level, label]) => (
          <div key={level} className="flex items-center gap-2 text-[10px] text-slate-300">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: LEVEL_COLORS[parseInt(level) as keyof typeof LEVEL_COLORS] }}
            />
            <span className="font-hindi">{label}</span>
          </div>
        ))}
      </div>

      {/* Selected Node Info Panel */}
      <AnimatePresence>
        {selectedNode && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-black/80 backdrop-blur-xl border border-white/20 rounded-lg p-4 min-w-[300px] shadow-2xl"
          >
            <div className="flex justify-between items-start mb-2">
              <div className="text-sm font-bold text-[#8BF5E6] font-hindi">
                {selectedNode.label}
              </div>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-slate-400 hover:text-white transition-colors"
              >
                ✕
              </button>
            </div>
            <div className="space-y-1 text-xs text-slate-300">
              <div className="flex justify-between">
                <span className="text-slate-500">स्तर:</span>
                <span className="font-medium font-hindi">
                  {LEVEL_LABELS_HI[selectedNode.level as keyof typeof LEVEL_LABELS_HI]}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">दौरे:</span>
                <span className="font-medium text-[#8BF5E6]">
                  {selectedNode.visits}
                </span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Hover Tooltip */}
      <AnimatePresence>
        {hoveredNode && !selectedNode && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-black/80 backdrop-blur-md border border-white/20 rounded-lg px-4 py-2 pointer-events-none z-50"
          >
            <div className="text-xs text-white font-hindi">
              {hoveredNode.label}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Instructions */}
      <div className="absolute bottom-4 right-4 bg-black/40 backdrop-blur-sm border border-white/10 rounded-lg px-3 py-2 text-[10px] text-slate-400 max-w-[200px]">
        <div className="font-hindi">
          • खींचें: नोड्स को स्थानांतरित करें
        </div>
        <div className="font-hindi">
          • क्लिक: विवरण देखें
        </div>
        <div className="font-hindi">
          • स्क्रॉल: ज़ूम इन/आउट
        </div>
      </div>
    </div>
  );
};

export default HierarchyMindMap;
