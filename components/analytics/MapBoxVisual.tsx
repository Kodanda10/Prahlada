import React, { useRef, useEffect, useState, useCallback } from 'react';
import Map, { Marker, Popup, NavigationControl, ScaleControl, FullscreenControl, Layer, Source } from 'react-map-gl';
import type { MapRef, ViewState } from 'react-map-gl';
import { MapPin, Navigation2, Layers, Loader2, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import 'mapbox-gl/dist/mapbox-gl.css';

interface LocationData {
  id: string;
  lat: number;
  lng: number;
  label: string;
  type: 'urban' | 'rural' | 'unknown';
  hierarchy_path: string[];
  visit_count: number;
  event_type?: string;
  date?: string;
}

interface MapBoxVisualProps {
  locations?: LocationData[];
  apiKey?: string;
}

const MAPBOX_TOKEN = import.meta.env.VITE_NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN || import.meta.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN || 'pk.eyJ1IjoicGluYWsxMCIsImEiOiJjbWhuN3FscHEwMDFnMmpzaHNhanNnZ29iIn0.2_5cTwOMzj_bS_OQ8Oj47w';

// Chhattisgarh center coordinates
const INITIAL_VIEW_STATE: Partial<ViewState> = {
  longitude: 82.15,
  latitude: 21.25,
  zoom: 7,
  pitch: 45,
  bearing: 0,
};

const MapBoxVisual: React.FC<MapBoxVisualProps> = ({ locations = [], apiKey = MAPBOX_TOKEN }) => {
  const mapRef = useRef<MapRef>(null);
  const [viewState, setViewState] = useState(INITIAL_VIEW_STATE);
  const [selectedLocation, setSelectedLocation] = useState<LocationData | null>(null);
  const [hoveredLocation, setHoveredLocation] = useState<LocationData | null>(null);
  const [mapStyle, setMapStyle] = useState<'dark' | 'satellite'>('dark');
  const [showClusters, setShowClusters] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const [mapLoaded, setMapLoaded] = useState(false);

  // Generate GeoJSON for clustering
  const geojsonData = {
    type: 'FeatureCollection' as const,
    features: locations.map((loc) => ({
      type: 'Feature' as const,
      properties: {
        id: loc.id,
        label: loc.label,
        type: loc.type,
        visit_count: loc.visit_count,
        event_type: loc.event_type || '',
        hierarchy_path: loc.hierarchy_path.join(' > '),
      },
      geometry: {
        type: 'Point' as const,
        coordinates: [loc.lng, loc.lat],
      },
    })),
  };

  // Cluster layer configuration
  const clusterLayer = {
    id: 'clusters',
    type: 'circle' as const,
    source: 'locations',
    filter: ['has', 'point_count'],
    paint: {
      'circle-color': [
        'step',
        ['get', 'point_count'],
        '#8BF5E6',
        10,
        '#6366f1',
        30,
        '#a855f7',
        50,
        '#ec4899',
      ],
      'circle-radius': ['step', ['get', 'point_count'], 20, 10, 30, 30, 40, 50, 50],
      'circle-opacity': 0.8,
      'circle-stroke-width': 2,
      'circle-stroke-color': '#ffffff',
    },
  };

  const clusterCountLayer = {
    id: 'cluster-count',
    type: 'symbol' as const,
    source: 'locations',
    filter: ['has', 'point_count'],
    layout: {
      'text-field': '{point_count_abbreviated}',
      'text-font': ['DIN Offc Pro Medium', 'Arial Unicode MS Bold'],
      'text-size': 14,
    },
    paint: {
      'text-color': '#0f172a',
    },
  };

  const unclusteredPointLayer = {
    id: 'unclustered-point',
    type: 'circle' as const,
    source: 'locations',
    filter: ['!', ['has', 'point_count']],
    paint: {
      'circle-color': [
        'match',
        ['get', 'type'],
        'urban',
        '#a855f7',
        'rural',
        '#8BF5E6',
        '#64748b',
      ],
      'circle-radius': [
        'interpolate',
        ['linear'],
        ['get', 'visit_count'],
        1,
        8,
        10,
        16,
        50,
        24,
      ],
      'circle-stroke-width': 2,
      'circle-stroke-color': '#ffffff',
      'circle-opacity': 0.9,
    },
  };

  // Heatmap layer for density visualization
  const heatmapLayer = {
    id: 'heatmap',
    type: 'heatmap' as const,
    source: 'locations',
    maxzoom: 15,
    paint: {
      'heatmap-weight': ['interpolate', ['linear'], ['get', 'visit_count'], 0, 0, 50, 1],
      'heatmap-intensity': ['interpolate', ['linear'], ['zoom'], 0, 1, 15, 3],
      'heatmap-color': [
        'interpolate',
        ['linear'],
        ['heatmap-density'],
        0,
        'rgba(0, 0, 255, 0)',
        0.2,
        'rgb(139, 245, 230)',
        0.4,
        'rgb(99, 102, 241)',
        0.6,
        'rgb(168, 85, 247)',
        0.8,
        'rgb(236, 72, 153)',
      ],
      'heatmap-radius': ['interpolate', ['linear'], ['zoom'], 0, 2, 15, 20],
      'heatmap-opacity': ['interpolate', ['linear'], ['zoom'], 7, 0.7, 15, 0],
    },
  };

  const handleClusterClick = useCallback((event: any) => {
    const feature = event.features?.[0];
    if (!feature) return;

    const clusterId = feature.properties.cluster_id;
    const mapboxSource = mapRef.current?.getSource('locations') as any;

    mapboxSource?.getClusterExpansionZoom(clusterId, (err: any, zoom: number) => {
      if (err) return;

      mapRef.current?.easeTo({
        center: feature.geometry.coordinates,
        zoom,
        duration: 500,
      });
    });
  }, []);

  const mapStyles = {
    dark: 'mapbox://styles/mapbox/dark-v11',
    satellite: 'mapbox://styles/mapbox/satellite-streets-v12',
  };

  useEffect(() => {
    // Simulate initial loading
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1500);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="relative w-full h-full min-h-[500px] rounded-xl overflow-hidden border border-white/10 shadow-2xl">
      {/* Loading Overlay */}
      <AnimatePresence>
        {isLoading && (
          <motion.div
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
            className="absolute inset-0 z-50 bg-[#0f172a] flex items-center justify-center"
          >
            <div className="text-center space-y-4">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
              >
                <Loader2 size={48} className="text-[#8BF5E6] mx-auto" />
              </motion.div>
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="text-sm text-slate-300 font-hindi"
              >
                मानचित्र लोड हो रहा है...
              </motion.div>
              <motion.div
                initial={{ scaleX: 0 }}
                animate={{ scaleX: 1 }}
                transition={{ duration: 1.5, ease: 'easeInOut' }}
                className="w-48 h-1 bg-gradient-to-r from-[#8BF5E6] via-purple-500 to-pink-500 rounded-full mx-auto"
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <Map
        ref={mapRef}
        {...viewState}
        onMove={(evt) => setViewState(evt.viewState)}
        onLoad={() => setMapLoaded(true)}
        mapboxAccessToken={apiKey}
        mapStyle={mapStyles[mapStyle]}
        style={{ width: '100%', height: '100%' }}
        interactiveLayerIds={showClusters ? ['clusters', 'unclustered-point'] : ['unclustered-point']}
        onClick={(e) => {
          const feature = e.features?.[0];
          if (feature?.layer.id === 'clusters') {
            handleClusterClick(e);
          }
        }}
        onMouseEnter={(e) => {
          const feature = e.features?.[0];
          if (feature && feature.layer.id === 'unclustered-point') {
            const loc = locations.find((l) => l.id === feature.properties.id);
            if (loc) setHoveredLocation(loc);
          }
        }}
        onMouseLeave={() => setHoveredLocation(null)}
      >
        {/* Data Source */}
        {mapLoaded && (
          <Source
            id="locations"
            type="geojson"
            data={geojsonData}
            cluster={showClusters}
            clusterMaxZoom={14}
            clusterRadius={50}
          >
            {showClusters && (
              <>
                <Layer {...heatmapLayer} />
                <Layer {...clusterLayer} />
                <Layer {...clusterCountLayer} />
              </>
            )}
            <Layer {...unclusteredPointLayer} />
          </Source>
        )}

        {/* Individual Markers (for non-clustered view) */}
        {!showClusters &&
          mapLoaded &&
          locations.map((location, index) => (
            <Marker
              key={location.id}
              longitude={location.lng}
              latitude={location.lat}
              anchor="bottom"
              onClick={(e) => {
                e.originalEvent.stopPropagation();
                setSelectedLocation(location);
              }}
            >
              <motion.div
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: index * 0.02, type: 'spring', stiffness: 300 }}
                whileHover={{ scale: 1.2 }}
                className="cursor-pointer"
              >
                <div className="relative flex flex-col items-center">
                  <motion.div
                    animate={{
                      scale: [1, 1.5, 1],
                      opacity: [0.7, 0, 0.7],
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                      ease: 'easeInOut',
                    }}
                    className={`absolute inset-0 rounded-full ${location.type === 'urban' ? 'bg-purple-500' : 'bg-[#8BF5E6]'
                      }`}
                  />
                  <div
                    className={`relative z-10 w-8 h-8 rounded-full flex items-center justify-center shadow-lg border-2 border-white ${location.type === 'urban'
                        ? 'bg-purple-600 text-white'
                        : 'bg-[#8BF5E6] text-black'
                      }`}
                  >
                    <MapPin size={16} fill="currentColor" />
                  </div>
                </div>
              </motion.div>
            </Marker>
          ))}

        {/* Popup for selected location */}
        {selectedLocation && (
          <Popup
            longitude={selectedLocation.lng}
            latitude={selectedLocation.lat}
            anchor="top"
            onClose={() => setSelectedLocation(null)}
            closeButton={true}
            closeOnClick={false}
            className="custom-popup"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-[#0f172a]/95 backdrop-blur-xl border border-white/10 rounded-lg p-4 min-w-[250px]"
            >
              <div className="text-sm font-bold text-[#8BF5E6] mb-2 font-hindi flex items-center gap-2">
                <Zap size={14} className="text-[#8BF5E6]" />
                {selectedLocation.label}
              </div>
              <div className="text-xs text-slate-300 space-y-1">
                <div className="flex justify-between">
                  <span className="text-slate-500">प्रकार:</span>
                  <span className="font-medium">
                    {selectedLocation.type === 'urban' ? 'शहरी' : 'ग्रामीण'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">दौरे:</span>
                  <motion.span
                    initial={{ scale: 1 }}
                    animate={{ scale: [1, 1.1, 1] }}
                    transition={{ duration: 0.5 }}
                    className="font-medium text-[#8BF5E6]"
                  >
                    {selectedLocation.visit_count}
                  </motion.span>
                </div>
                {selectedLocation.event_type && (
                  <div className="flex justify-between">
                    <span className="text-slate-500">घटना:</span>
                    <span className="font-medium font-hindi">
                      {selectedLocation.event_type}
                    </span>
                  </div>
                )}
                <div className="mt-2 pt-2 border-t border-white/10">
                  <div className="text-[10px] text-slate-400 font-hindi">
                    {selectedLocation.hierarchy_path.join(' > ')}
                  </div>
                </div>
              </div>
            </motion.div>
          </Popup>
        )}

        {/* Hover Tooltip */}
        <AnimatePresence>
          {hoveredLocation && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-black/80 backdrop-blur-md border border-white/20 rounded-lg px-4 py-2 pointer-events-none z-50"
            >
              <div className="text-xs text-white font-hindi">
                {hoveredLocation.label} ({hoveredLocation.visit_count} दौरे)
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Controls */}
        <NavigationControl position="top-right" />
        <ScaleControl position="bottom-right" />
        <FullscreenControl position="top-right" />

        {/* Custom Control Panel */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          className="absolute top-4 left-4 bg-black/60 backdrop-blur-md border border-white/10 rounded-lg p-3 space-y-2"
        >
          <div className="flex items-center gap-2 text-xs font-bold text-slate-200 font-hindi">
            <MapPin size={14} className="text-[#8BF5E6]" />
            रायगढ़ जिला कवरेज
          </div>
          <div className="text-[10px] text-slate-400">
            कुल स्थान: {locations.length}
          </div>
          <div className="flex gap-2 mt-2">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setMapStyle(mapStyle === 'dark' ? 'satellite' : 'dark')}
              className="px-2 py-1 bg-white/10 hover:bg-white/20 rounded text-[10px] text-white transition-colors flex items-center gap-1"
            >
              <Layers size={12} />
              {mapStyle === 'dark' ? 'Satellite' : 'Dark'}
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowClusters(!showClusters)}
              className={`px-2 py-1 rounded text-[10px] text-white transition-colors ${showClusters ? 'bg-[#8BF5E6] text-black' : 'bg-white/10 hover:bg-white/20'
                }`}
            >
              Cluster
            </motion.button>
          </div>
        </motion.div>

        {/* Legend */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.7 }}
          className="absolute bottom-4 left-4 bg-black/60 backdrop-blur-md border border-white/10 rounded-lg p-3 space-y-2"
        >
          <div className="text-[10px] font-bold text-slate-200 mb-2 font-hindi">
            किंवदंती
          </div>
          <motion.div
            whileHover={{ x: 5 }}
            className="flex items-center gap-2 text-[10px] text-slate-300"
          >
            <div className="w-3 h-3 rounded-full bg-[#8BF5E6]" />
            <span className="font-hindi">ग्रामीण</span>
          </motion.div>
          <motion.div
            whileHover={{ x: 5 }}
            className="flex items-center gap-2 text-[10px] text-slate-300"
          >
            <div className="w-3 h-3 rounded-full bg-purple-600" />
            <span className="font-hindi">शहरी</span>
          </motion.div>
        </motion.div>
      </Map>
    </div>
  );
};

export default MapBoxVisual;
