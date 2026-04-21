import React, { useState } from 'react';
import { ShieldAlert, Activity, Crosshair, Server } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

//temp data 
const mockData = [
  { time: '10:00',risk: 0.2 },
  { time: '10:05',risk: 0.2 },
  { time: '10:10',risk: 1.0 },
  { time: '10:15',risk: 0.2 },
  { time: '10:20',risk: 0.2 },
];

export default function App() {
  const [currentThreshold, setCurrentThreshold] = useState(1.0);

  return (
    <div className="min-h-screen bg-slate-900 p-8 text-slate-100 font-sans">
      
      {/* header */}
      <header className="mb-8 flex justify-between items-center border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
            <ShieldAlert className="text-emerald-500" size={32} />
            Fraud Checking Center
          </h1>
          <p className="text-slate-400 mt-1">Engine Status: Active</p>
        </div>
        <div className="flex items-center gap-2 bg-slate-800 px-4 py-2 rounded-lg border border-slate-700">
          <Server size={18} className="text-blue-400" />
          <span className="text-sm font-medium">Julia Optimizer: Online</span>
        </div>
      </header>

      {/* Metrics*/}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        
        {/* Metric 1 Threshold */}
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-lg relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-10">
            <Crosshair size={64} />
          </div>
          <h3 className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">Optimal Threshold (θ)</h3>
          <div className="text-5xl font-bold text-white mb-2">{currentThreshold.toFixed(2)}</div>
          <p className="text-xs text-emerald-400">Locked via Redis</p>
        </div>

        {/* Metric 2 Live Risk Pulse*/}
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-lg">
          <h3 className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">Live Scored Volume</h3>
          <div className="text-5xl font-bold text-white mb-2">1,000</div>
          <p className="text-xs text-blue-400">Transactions processed this cycle</p>
        </div>

        {/* Metric 3 threat Detection */}
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-lg">
          <h3 className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">Syndicate Intercepts</h3>
          <div className="text-5xl font-bold text-red-500 mb-2">10</div>
          <p className="text-xs text-red-400">High-Risk anomalies flagged</p>
        </div>
      </div>

      {/* Main chart section */}
      <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-lg">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <Activity className="text-blue-500" />
            Live Risk Pulse
          </h2>
        </div>
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={mockData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="time" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" domain={[0, 1.2]} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e293b', borderColor: '#475569', color: '#f8fafc' }}
                itemStyle={{ color: '#38bdf8' }}
              />
              <Line 
                type="monotone" 
                dataKey="risk" 
                stroke="#3b82f6" 
                strokeWidth={3}
                dot={{ r: 4, fill: '#3b82f6', strokeWidth: 2, stroke: '#1e293b' }}
                activeDot={{ r: 6, fill: '#ef4444', stroke: '#1e293b' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

    </div>
  );
}