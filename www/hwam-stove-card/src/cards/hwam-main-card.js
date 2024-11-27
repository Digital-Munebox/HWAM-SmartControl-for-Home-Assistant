import { useState } from 'react';
import { CircleSlash, Flame, Thermometer, Wind, AlertTriangle, Moon } from 'lucide-react';

export default function HWAMCard() {
  const [burnLevel, setBurnLevel] = useState(3);

  return (
    <div className="flex flex-col bg-white rounded-lg shadow-lg p-4 w-full max-w-md mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <Flame className="h-6 w-6 text-orange-500 mr-2" />
          <h2 className="text-xl font-semibold">HWAM Smart Control</h2>
        </div>
        <div className="flex items-center">
          <Moon className="h-5 w-5 text-gray-500" />
          <span className="text-sm ml-1">Mode nuit</span>
        </div>
      </div>

      {/* Main Temperature Display */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-orange-50 rounded-lg p-4 flex flex-col items-center">
          <Thermometer className="h-8 w-8 text-orange-500 mb-2" />
          <span className="text-2xl font-bold">245°C</span>
          <span className="text-sm text-gray-600">Température poêle</span>
        </div>
        <div className="bg-blue-50 rounded-lg p-4 flex flex-col items-center">
          <Thermometer className="h-8 w-8 text-blue-500 mb-2" />
          <span className="text-2xl font-bold">21°C</span>
          <span className="text-sm text-gray-600">Température pièce</span>
        </div>
      </div>

      {/* Burn Level Control */}
      <div className="mb-6">
        <label className="text-sm font-medium text-gray-700 mb-2 block">
          Niveau de combustion
        </label>
        <input
          type="range"
          min="0"
          max="5"
          value={burnLevel}
          onChange={(e) => setBurnLevel(Number(e.target.value))}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
        />
        <div className="flex justify-between text-sm text-gray-600 mt-1">
          <span>0</span>
          <span>1</span>
          <span>2</span>
          <span>3</span>
          <span>4</span>
          <span>5</span>
        </div>
      </div>

      {/* Status Indicators */}
      <div className="grid grid-cols-3 gap-2">
        <div className="flex flex-col items-center bg-gray-50 rounded p-2">
          <Wind className="h-6 w-6 text-blue-500 mb-1" />
          <span className="text-sm">20% O₂</span>
        </div>
        <div className="flex flex-col items-center bg-gray-50 rounded p-2">
          <Flame className="h-6 w-6 text-orange-500 mb-1" />
          <span className="text-sm">Combustion</span>
        </div>
        <div className="flex flex-col items-center bg-gray-50 rounded p-2">
          <CircleSlash className="h-6 w-6 text-red-500 mb-1" />
          <span className="text-sm">Porte fermée</span>
        </div>
      </div>

      {/* Alerts */}
      <div className="mt-4 flex items-center justify-between text-sm">
        <div className="flex items-center text-orange-500">
          <AlertTriangle className="h-4 w-4 mr-1" />
          <span>Rechargement nécessaire</span>
        </div>
        <span className="text-gray-500">1h30</span>
      </div>
    </div>
  );
}
