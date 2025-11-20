
import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface CustomLineChartProps {
  data: any[];
  xKey: string;
  dataKey: string;
  height?: number | string;
  lineColor?: string;
}

const CustomLineChart: React.FC<CustomLineChartProps> = ({
  data,
  xKey,
  dataKey,
  height = 300,
  lineColor = "#22d3ee"
}) => {
  return (
    <div style={{ height, width: '100%' }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
          <XAxis 
            dataKey={xKey} 
            stroke="#94a3b8" 
            tick={{ fill: '#94a3b8', fontFamily: 'Noto Sans Devanagari, sans-serif' }} 
            axisLine={false} 
            tickLine={false} 
          />
          <YAxis 
            stroke="#94a3b8" 
            tick={{ fill: '#94a3b8' }} 
            axisLine={false} 
            tickLine={false} 
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'rgba(15, 23, 42, 0.9)', 
              border: '1px solid rgba(255,255,255,0.1)', 
              borderRadius: '8px', 
              color: '#fff',
              backdropFilter: 'blur(4px)',
              fontFamily: 'Noto Sans Devanagari, sans-serif'
            }}
          />
          <Line 
            type="monotone" 
            dataKey={dataKey} 
            stroke={lineColor} 
            strokeWidth={3} 
            dot={{ r: 4, fill: '#0f172a', stroke: lineColor, strokeWidth: 2 }} 
            activeDot={{ r: 6, fill: lineColor }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CustomLineChart;
