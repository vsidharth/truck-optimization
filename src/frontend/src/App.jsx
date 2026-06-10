import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import axios from 'axios';
import L from 'leaflet';

// Fix Leaflet's default marker asset icon rendering anomalies within React environments
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom Node Pin Markers for Visual Distinction
const truckIcon = new L.Icon({
  iconUrl: 'https://maps.google.com/mapfiles/ms/icons/truck.png',
  iconSize: [32, 32],
});
const requestIcon = new L.Icon({
  iconUrl: 'https://maps.google.com/mapfiles/ms/icons/red-dot.png',
  iconSize: [32, 32],
});

export default function App() {
  const [rawData, setRawData] = useState({ trucks: [], requests: [] });
  const [optimizationData, setOptimizationData] = useState(null);
  const [selectedStrategy, setSelectedStrategy] = useState('milp_solver');
  const [activeTruckId, setActiveTruckId] = useState(null); // NEW: Track highlighted truck
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      axios.get('http://127.0.0.1:8000/api/data'),
      axios.get('http://127.0.0.1:8000/api/optimize')
    ]).then(([resData, resOpt]) => {
      setRawData(resData.data);
      setOptimizationData(resOpt.data);
      setLoading(false);
    }).catch(err => {
      console.error("API link failure:", err);
      setLoading(false);
    });
  }, []);

  // NEW: Reset active focus filter automatically if the algorithm strategy is toggled
  useEffect(() => {
    setActiveTruckId(null);
  }, [selectedStrategy]);

  if (loading || !optimizationData) {
    return <div style={{ padding: '24px', fontSize: '18px' }}>🚀 Simulating Fleet Dispatch Matrix Channels...</div>;
  }

  const currentResult = optimizationData.results[selectedStrategy];
  const truckMap = new Map(rawData.trucks.map(t => [t.id, t]));
  const requestMap = new Map(rawData.requests.map(r => [r.id, r]));

  // Helper utility to track how many orders are assigned to each truck dynamically
  const getTruckOrderCount = (truckId) => {
    return currentResult.assignments.filter(a => a.truck_id === truckId).length;
  };

  return (
    <div className="dashboard-container">
      {/* LEFT SIDEBAR: METRICS INTERFACE */}
      <div className="sidebar">
        <h2 style={{ margin: '0 0 4px 0' }}>Truck Optimization Engine</h2>
        <p style={{ color: '#6b7280', fontSize: '14px', margin: '0 0 24px 0' }}>Track C – Applied Logistics Optimization</p>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ fontWeight: 'bold', display: 'block', marginBottom: '8px' }}>Select Strategy View:</label>
          <select 
            style={{ width: '100%', padding: '10px', borderRadius: '6px', fontSize: '14px' }}
            value={selectedStrategy} 
            onChange={(e) => setSelectedStrategy(e.target.value)}
          >
            <option value="milp_solver">Global MILP Solver (PuLP)</option>
            <option value="regret_heuristic">Look-Ahead Regret Heuristic</option>
          </select>
        </div>

        {/* ISOLATION FILTER BANNER NOTIFICATION */}
        {activeTruckId && (
          <div style={{ padding: '12px', background: '#fff7ed', border: '1px solid #ffedd5', borderRadius: '6px', marginBottom: '16px', fontSize: '13px' }}>
            🔍 Filtering map view for <strong>{activeTruckId}</strong> ({getTruckOrderCount(activeTruckId)} orders allocated).
            <button 
              onClick={() => setActiveTruckId(null)} 
              style={{ display: 'block', marginTop: '6px', background: '#f97316', color: 'white', border: 'none', padding: '4px 8px', borderRadius: '4px', cursor: 'pointer', fontSize: '11px' }}
            >
              Reset View / Show All
            </button>
          </div>
        )}

        {/* SIDE-BY-SIDE METRIC BOXES */}
        <div className={`metric-card ${selectedStrategy === 'milp_solver' ? 'active-card' : ''}`}>
          <h3>Mathematical MILP Solver</h3>
          <p>📍 <strong>Total Distance:</strong> {optimizationData.results.milp_solver.total_distance_km} km</p>
          <p>⏱️ <strong>Solver Runtime:</strong> {optimizationData.results.milp_solver.runtime_ms.toFixed(1)} ms</p>
          <p>✅ <strong>Constraint Fulfillment:</strong> {optimizationData.results.milp_solver.constraint_satisfaction_rate}%</p>
        </div>

        <div className={`metric-card ${selectedStrategy === 'regret_heuristic' ? 'active-card' : ''}`}>
          <h3>Regret Heuristic Baseline</h3>
          <p>📍 <strong>Total Distance:</strong> {optimizationData.results.regret_heuristic.total_distance_km} km</p>
          <p>⏱️ <strong>Heuristic Runtime:</strong> {optimizationData.results.regret_heuristic.runtime_ms.toFixed(1)} ms</p>
          <p>✅ <strong>Constraint Fulfillment:</strong> {optimizationData.results.regret_heuristic.constraint_satisfaction_rate}%</p>
        </div>

        <div className="metric-card" style={{ backgroundColor: '#f0fdf4', borderColor: '#bbf7d0' }}>
          <h4 style={{ color: '#166534', margin: '0 0 8px 0' }}>📈 Strategy Delta Efficiency</h4>
          <p style={{ fontSize: '14px', lineHeight: '1.4' }}>{optimizationData.analysis.explanation}</p>
        </div>
      </div>

      {/* RIGHT PANE: INTERACTIVE MAP VIEW */}
      <div className="map-pane">
        <MapContainer center={[12.9716, 77.5946]} zoom={11} style={{ height: '100%', width: '100%' }}>
          <TileLayer
            attribution='© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* Draw Truck Markers with Interactive Event Triggers */}
          {rawData.trucks.map(truck => {
            const isFocused = activeTruckId === truck.id;
            const orderCount = getTruckOrderCount(truck.id);

            return (
              <Marker 
                key={truck.id} 
                position={[truck.lat, truck.lng]} 
                icon={truckIcon}
                eventHandlers={{
                  click: () => {
                    // NEW: Toggle focus state on node selection click
                    setActiveTruckId(prev => prev === truck.id ? null : truck.id);
                  },
                }}
              >
                <Popup>
                  <strong>{isFocused ? "⭐ Focus Mode: " : "🚛 "} {truck.id}</strong><br />
                  Hub: {truck.initial_hub}<br />
                  Capacity: {truck.max_capacity} kg<br />
                  Cold Chain: {truck.is_refrigerated ? "✅ Yes" : "❌ No"}<br />
                  <span style={{ color: '#2563eb', fontWeight: 'bold' }}>Active Shift Allocations: {orderCount}</span>
                </Popup>
              </Marker>
            );
          })}

          {/* Draw Order Request Markers */}
          {rawData.requests.map(req => (
            <Marker key={req.id} position={[req.lat, req.lng]} icon={requestIcon}>
              <Popup>
                <strong>📦 {req.id}</strong><br />
                Weight: {req.weight} kg<br />
                Needs Refrigeration: {req.requires_refrigeration ? "❄️ Yes" : "❌ No"}
              </Popup>
            </Marker>
          ))}

          {/* Modified Line Rendering Vector Loop Layer */}
          {currentResult.assignments.map((assign, idx) => {
            // NEW FILTER LAYER: If a specific truck is selected, skip rendering any lines belonging to other trucks
            if (activeTruckId && assign.truck_id !== activeTruckId) {
              return null;
            }

            const tk = truckMap.get(assign.truck_id);
            const rq = requestMap.get(assign.request_id);
            if (!tk || !rq) return null;

            return (
              <Polyline 
                key={idx} 
                positions={[[tk.lat, tk.lng], [rq.lat, rq.lng]]} 
                color={selectedStrategy === 'milp_solver' ? '#2563eb' : '#dc2626'} 
                weight={activeTruckId ? 4 : 2} // Bold the lines if we are looking at an isolated chain
                dashArray={selectedStrategy === 'milp_solver' ? null : "5, 5"}
              />
            );
          })}
        </MapContainer>
      </div>
    </div>
  );
}