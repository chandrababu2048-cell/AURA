import React from 'react';
import CosmicTerminal from './components/CosmicTerminal';
import NewsWeatherHUD from './components/NewsWeatherHUD';
import AuraChat from './components/AuraChat';
import { Terminal } from 'lucide-react';

function App() {
  return (
    <CosmicTerminal>
      <div className="flex-grow flex flex-col justify-between max-w-7xl mx-auto w-full pt-8 pb-12 px-4 z-20">
        
        {/* Header Strip */}
        <header className="mb-12 border-b-2 border-[#FFB000]/30 pb-4 flex justify-between items-end relative">
          <div className="flex items-center gap-4">
            <div className="bg-[#FFB000]/10 p-3 border border-[#FFB000]/50 rounded animate-pulse">
              <Terminal className="text-[#FFB000] drop-shadow-[0_0_8px_rgba(255,176,0,0.8)]" size={32} />
            </div>
            <div>
              <h1 className="text-5xl font-bold text-glow tracking-widest leading-none">A U R A</h1>
              <span className="text-xl tracking-[0.3em] opacity-80 uppercase">System Active _</span>
            </div>
          </div>
          
          <div className="text-right flex flex-col items-end">
            <span className="bg-[#FFB000] text-black px-2 text-sm font-bold tracking-widest mb-1">ONLINE</span>
            <span className="tracking-widest opacity-60">Phase 1 Init</span>
          </div>
        </header>

        {/* Main HUD & Chat */}
        <div className="flex-grow flex flex-col justify-center mb-8 gap-8">
          <NewsWeatherHUD />
          <AuraChat />
        </div>

      </div>
    </CosmicTerminal>
  );
}

export default App;
