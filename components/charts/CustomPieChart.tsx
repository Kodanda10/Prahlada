
import React from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';

interface CustomPieChartProps {
  data: any[];
  dataKey?: string;
  nameKey?: string;
  colors?: string[];
  width?: number | string;
  height?: number | string;
  innerRadius?: number;
  outerRadius?: number;
  centerLabel?: React.ReactNode;
  showLegend?: boolean;
}

const CustomPieChart: React.FC<CustomPieChartProps> = ({
  data,
  dataKey = "value",
  nameKey = "name",
  width = '100%',
  height = 250,
  innerRadius = 60,
  outerRadius = 80,
  centerLabel,
  showLegend = true
}) => {
  return (
    <div className="flex flex-col items-center justify-center w-full h-full">
      <div className="relative" style={{ width, height }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={innerRadius}
              outerRadius={outerRadius}
              paddingAngle={5}
              dataKey={dataKey}
              nameKey={nameKey}
            >
              {data.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={entry.fill || entry.color || '#8BF5E6'} 
                  stroke="rgba(255,255,255,0.05)"
                />
              ))}
            </Pie>
            <Tooltip 
              wrapperStyle={{ zIndex: 1000 }}
              contentStyle={{ 
                backgroundColor: 'rgba(15, 23, 42, 0.95)', 
                borderColor: 'rgba(255,255,255,0.1)', 
                borderRadius: '8px', 
                color: '#fff',
                backdropFilter: 'blur(8px)',
                boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
                fontFamily: 'Noto Sans Devanagari, sans-serif'
              }} 
              itemStyle={{ color: '#fff' }}
            />
          </PieChart>
        </ResponsiveContainer>
        
        {centerLabel && (
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center pointer-events-none font-hindi">
            {centerLabel}
          </div>
        )}
      </div>

      {showLegend && (
        <div className="flex flex-wrap gap-3 justify-center mt-2">
          {data.map((item, idx) => (
            <div key={idx} className="flex items-center gap-2 text-xs text-slate-300 font-hindi">
              <div 
                className="w-3 h-3 rounded-full shadow-[0_0_5px_rgba(0,0,0,0.3)]" 
                style={{ backgroundColor: item.fill || item.color }} 
              />
              {item[nameKey]}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CustomPieChart;
