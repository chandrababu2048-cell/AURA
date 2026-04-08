import React from 'react';
import GalaxyBackground from './GalaxyBackground';

const CosmicTerminal = ({ children }) => {
  return (
    <div className="relative min-h-screen w-full bg-[#050505] text-[#FFB000] font-vt323 antialiased scanlines selection:bg-[#FFB000] selection:text-[#050505]">
      <GalaxyBackground />
      
      {/* HUD Layer superimposed over the galaxy background */}
      <div className="relative z-10 w-full min-h-screen flex flex-col p-6 pointer-events-none">
        {/* We use pointer-events-none on wrapper so you can click through empty space, 
            but all child content must repoint to auto */}
        <div className="pointer-events-auto h-full flex flex-col flex-grow">
          {children}
        </div>
      </div>
    </div>
  );
};

export default CosmicTerminal;
