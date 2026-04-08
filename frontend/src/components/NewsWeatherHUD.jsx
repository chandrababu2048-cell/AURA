import React, { useState, useEffect } from 'react';
import { CloudRain, Thermometer, Wind, Globe, Cpu, MemoryStick, ShieldAlert, Loader } from 'lucide-react';
import { motion } from 'framer-motion';

const GlassPanel = ({ children, title, icon: Icon, className = "" }) => (
  <motion.div 
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5 }}
    className={`bg-black/20 backdrop-blur-md border border-[#FFB000]/30 rounded-lg p-4 shadow-[0_0_15px_rgba(255,176,0,0.1)] relative overflow-hidden ${className}`}
  >
    {/* Decorative corner brackets */}
    <div className="absolute top-0 left-0 w-2 h-2 border-t-2 border-l-2 border-[#FFB000]"></div>
    <div className="absolute top-0 right-0 w-2 h-2 border-t-2 border-r-2 border-[#FFB000]"></div>
    <div className="absolute bottom-0 left-0 w-2 h-2 border-b-2 border-l-2 border-[#FFB000]"></div>
    <div className="absolute bottom-0 right-0 w-2 h-2 border-b-2 border-r-2 border-[#FFB000]"></div>
    
    <div className="flex items-center gap-2 mb-3 border-b border-[#FFB000]/20 pb-2">
      {Icon && <Icon size={18} className="text-[#FFB000]" />}
      <h3 className="text-xl tracking-widest uppercase text-glow font-bold">{title}</h3>
    </div>
    <div className="text-lg">
      {children}
    </div>
  </motion.div>
);

const NewsWeatherHUD = () => {
  const [time, setTime] = useState(new Date().toLocaleTimeString());
  const [weather, setWeather] = useState(null);
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date().toLocaleTimeString()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const fetchHUDData = async () => {
      try {
        const [weatherRes, newsRes] = await Promise.all([
          fetch('http://localhost:8000/weather'),
          fetch('http://localhost:8000/news')
        ]);
        
        if (weatherRes.ok) {
           const wData = await weatherRes.json();
           setWeather(wData);
        }
        
        if (newsRes.ok) {
           const nData = await newsRes.json();
           if (nData.data) {
             const lines = nData.data.split('\n').filter(l => l.startsWith('- ')).map(l => l.substring(2));
             setNews(lines);
           }
        }
      } catch (error) {
        console.error("Failed to fetch HUD data:", error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchHUDData();
    const refreshInterval = setInterval(fetchHUDData, 300000); // refresh every 5 mins
    return () => clearInterval(refreshInterval);
  }, []);

  return (
    <div className="w-full grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* Planetary Weather */}
      <GlassPanel title="Local Atmos" icon={Globe}>
        {loading ? (
            <div className="flex justify-center items-center h-24"><Loader className="animate-spin text-[#FFB000]" /></div>
        ) : weather && weather.success ? (
            <>
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <div className="text-5xl font-bold text-glow mb-1">{Math.round(weather.temp)}°F</div>
                    <div className="text-sm tracking-widest uppercase opacity-70">{weather.city}</div>
                  </div>
                  <CloudRain size={48} className="text-[#FFB000] opacity-80 drop-shadow-[0_0_8px_rgba(255,176,0,0.8)]" />
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm tracking-wider">
                  <div className="flex items-center gap-2">
                    <Thermometer size={16} />
                    <span>Feels Like: {Math.round(weather.feels_like)}°</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Wind size={16} />
                    <span>Wind: {weather.wind} mph</span>
                  </div>
                </div>
            </>
        ) : (
            <div className="text-sm opacity-60">Atmos Sensors Offline</div>
        )}
      </GlassPanel>

      {/* Global Intel (News) */}
      <GlassPanel title="Global Intel" icon={ShieldAlert} className="md:col-span-2">
        <div className="flex flex-col gap-3 h-full justify-center">
            {loading ? (
                <div className="flex justify-center items-center h-24"><Loader className="animate-spin text-[#FFB000]" /></div>
            ) : news.length > 0 ? (
              news.map((headline, idx) => (
                <div key={idx} className="flex flex-col border-l-2 border-[#FFB000]/40 pl-3 group hover:bg-[#FFB000]/5 transition-colors p-1 rounded-r cursor-pointer">
                  <div className="text-lg leading-tight group-hover:text-glow transition-all">
                    {headline}
                  </div>
                </div>
              ))
            ) : (
                <div className="text-sm opacity-60">Global Comms Offline</div>
            )}
        </div>
      </GlassPanel>

      {/* System Telemetry Placeholder */}
      <GlassPanel title="Terminal Telemetry" icon={Cpu} className="md:col-span-3 lg:col-span-1">
        <div className="space-y-4">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span>CPU Core Load</span>
              <span className="animate-pulse">42%</span>
            </div>
            <div className="h-1.5 w-full bg-black/40 border border-[#FFB000]/30 overflow-hidden">
              <div className="h-full bg-[#FFB000] shadow-[0_0_8px_rgba(255,176,0,0.8)] w-[42%]"></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span>Memory Allocation</span>
              <span>16GB / 32GB</span>
            </div>
            <div className="h-1.5 w-full bg-black/40 border border-[#FFB000]/30 overflow-hidden">
              <div className="h-full bg-[#FFB000] shadow-[0_0_8px_rgba(255,176,0,0.8)] w-[50%]"></div>
            </div>
          </div>
          <div className="pt-2 flex items-center justify-between border-t border-[#FFB000]/20 text-sm">
            <span>SYS_TIME</span>
            <span className="text-xl tracking-widest text-glow">{time}</span>
          </div>
        </div>
      </GlassPanel>
    </div>
  );
};

export default NewsWeatherHUD;
