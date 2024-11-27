import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { TrendingUp, Timer, CircleSlash } from 'lucide-react';

const data = [
  { time: '12:00', temp: 245, room: 21 },
  { time: '12:30', temp: 256, room: 22 },
  { time: '13:00', temp: 238, room: 22 },
  { time: '13:30', temp: 242, room: 21 },
  { time: '14:00', temp: 248, room: 21 },
];

export default function HWAMStatsCard() {
  return (
    <div className="bg-white rounded-lg shadow-lg p-4 w-full max-w-xl mx-auto">
      <h2 className="text-xl font-semibold mb-4">Statistiques HWAM</h2>

      {/* Temperature Chart */}
      <div className="mb-6">
        <div className="mb-4">
          <LineChart width={500} height={200} data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="temp" 
              name="Température poêle" 
              stroke="#f97316" 
            />
            <Line 
              type="monotone" 
              dataKey="room" 
              name="Température pièce" 
              stroke="#3b82f6" 
            />
          </LineChart>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="flex items-center mb-2">
            <TrendingUp className="h-5 w-5 text-green-500 mr-2" />
            <span className="text-sm font-medium">Efficacité</span>
          </div>
          <span className="text-xl font-bold">92%</span>
        </div>
        
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="flex items-center mb-2">
            <Timer className="h-5 w-5 text-blue-500 mr-2" />
            <span className="text-sm font-medium">Temps actif</span>
          </div>
          <span className="text-xl font-bold">4h30</span>
        </div>

        <div className="bg-gray-50 rounded-lg p-3">
          <div className="flex items-center mb-2">
            <CircleSlash className="h-5 w-5 text-orange-500 mr-2" />
            <span className="text-sm font-medium">Ouvertures</span>
          </div>
          <span className="text-xl font-bold">3</span>
        </div>
      </div>

      {/* Details List */}
      <div className="mt-4 space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Température max (24h)</span>
          <span className="font-medium">320°C</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Température min (24h)</span>
          <span className="font-medium">180°C</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Moyenne O₂</span>
          <span className="font-medium">20%</span>
        </div>
      </div>
    </div>
  );
}
