
import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface CustomBarChartProps {
  data: any[];
  xKey: string;
  dataKey: string;
  height?: number | string;
  barColor?: string;
}

const CustomBarChart: React.FC<CustomBarChartProps> = ({
  data,
  xKey,
  dataKey,
  height = 200,
  barColor = "#8BF5E6"
}) => {
  return (
    <div style={{ height, width: '100%' }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
          <XAxis 
            dataKey={xKey} 
            stroke="#64748b" 
            fontSize={12} 
            axisLine={false} 
            tickLine={false} 
            tick={{ fontFamily: 'Noto Sans Devanagari, sans-serif' }}
          />
          <YAxis 
            stroke="#64748b" 
            fontSize={12} 
            axisLine={false} 
            tickLine={false} 
            tick={{ fontFamily: 'sans-serif' }} // Numbers in English
          />
          <Tooltip 
            cursor={{ fill: 'rgba(255,255,255,0.05)' }} 
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
          />
          <Bar 
            dataKey={dataKey} 
            fill={barColor} 
            radius={[4, 4, 0, 0]} 
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CustomBarChart;
