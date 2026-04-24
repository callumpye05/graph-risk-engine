import React, { useState, useEffect } from 'react';
import { ShieldAlert, Activity, Crosshair, Server, Radio } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'; //for graphs later

export default function App() {
  const [transactions, setTransactions] = useState([]);
  const [threshold, setThreshold] = useState(1.0);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    
    const socket = new WebSocket('ws://127.0.0.1:8000/ws/pulse');

    socket.onopen = () => setIsConnected(true);
    socket.onclose = () => setIsConnected(false);

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setTransactions(prev => [data, ...prev]); 
      
      //if the data contains a threshold update ( for later)
      // setThreshold(data.new_theta); 
    };

    return () => socket.close();
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 p-8 text-slate-100 font-sans">
      
      {/*connection status */}
      <header className="mb-8 flex justify-between items-center border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
            <ShieldAlert className={isConnected ? "text-emerald-500" : "text-red-500"} size={32} />
            Risk Intelligence Center
          </h1>
          <p className="text-slate-400 mt-1">
            {isConnected ? "Live Pulse Active" : "Connection Lost - Attempting Reconnect..."}
          </p>
        </div>
        <div className="flex gap-4">
          <div className="flex items-center gap-2 bg-slate-800 px-4 py-2 rounded-lg border border-slate-700">
             <Radio size={18} className={isConnected ? "animate-pulse text-emerald-400" : "text-slate-500"} />
             <span className="text-sm font-medium">WS Relay</span>
          </div>
        </div>
      </header>

      {/* Metrics Row (Dynamic) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-lg">
          <h3 className="text-slate-400 text-sm font-medium uppercase mb-2">Optimal Threshold</h3>
          <div className="text-5xl font-bold text-white">{threshold.toFixed(2)}</div>
        </div>
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-lg">
          <h3 className="text-slate-400 text-sm font-medium uppercase mb-2">Total Monitored</h3>
          <div className="text-5xl font-bold text-blue-400">{transactions.length}</div>
        </div>
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-lg">
          <h3 className="text-slate-400 text-sm font-medium uppercase mb-2">Threats Detected</h3>
          <div className="text-5xl font-bold text-red-500">
            {transactions.filter(t => t.risk > 0.8).length}
          </div>
        </div>
      </div>

      {/* live feed*/}
      <div className="bg-slate-800 rounded-xl border border-slate-700 shadow-lg overflow-hidden">
        <div className="p-4 border-b border-slate-700 bg-slate-800/50">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Activity className="text-blue-500" size={20} /> Real-Time Signal Stream
          </h2>
        </div>
        
        {/* Scroll of transactions*/}
        <div className="overflow-auto max-h-[600px] scrollbar-thin scrollbar-thumb-slate-600">
          <table className="w-full text-left border-collapse">
            <thead className="sticky top-0 bg-slate-800 z-10 shadow-md">
              <tr className="text-slate-500 text-sm border-b border-slate-700">
                <th className="p-4 font-medium">Account ID</th>
                <th className="p-4 font-medium">Amount</th>
                <th className="p-4 font-medium">Risk Score</th>
                <th className="p-4 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((tx, idx) => (
                <tr key={idx} className="border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors">
                  <td className="p-4 font-mono text-sm">{tx.account_id}</td>
                  <td className="p-4">${tx.amount?.toLocaleString()}</td>
                  <td className="p-4">
                    <div className="w-full bg-slate-700 rounded-full h-2 max-w-[100px]">
                      <div 
                        className={`h-2 rounded-full ${tx.risk > 0.8 ? 'bg-red-500' :'bg-emerald-500'}`}
                        style={{ width: `${Math.min(tx.risk * 100,100)}%` }}
                      ></div>
                    </div>
                  </td>
                  <td className="p-4 text-xs font-bold uppercase tracking-widest">
                    {tx.risk > 0.8 ? (
                      <span className="text-red-400">Flagged</span>
                    ) : (
                      <span className="text-emerald-400">Safe</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}