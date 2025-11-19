// RAG Chatbot Frontend
import { useState, useEffect } from 'react';
import Background from './components/ShaderBackground';
import ChatInterface from './components/ChatInterface';

function App() {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Show loading for 2.5 seconds
    const timer = setTimeout(() => {
      setLoading(false);
    }, 2500);
    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return (
      <div className="fixed inset-0 bg-white flex items-center justify-center z-50">
        <div className="text-center">
          <img 
            src="/dog.gif" 
            alt="Loading..." 
            className="w-64 h-64 object-contain mx-auto mb-4 drop-shadow-2xl"
          />
          <p className="text-gray-800 text-xl font-semibold animate-pulse">Loading RAG Assistant...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen w-full overflow-hidden text-white font-sans">
      <Background />
      
      {/* Header with Logos */}
      <header className="fixed top-0 left-0 right-0 z-50 p-6 flex justify-between items-center pointer-events-none">
        <div className="pointer-events-auto group relative w-24 h-24 rounded-full bg-white backdrop-blur-md border-2 border-orange-500/30 flex items-center justify-center transition-all duration-500 hover:scale-150 hover:z-50 overflow-hidden cursor-pointer shadow-[0_0_15px_rgba(255,87,34,0.3)] hover:shadow-[0_0_30px_rgba(255,87,34,0.6)]">
           <img src="/celebal_logo.png" alt="Celebal Technologies" className="absolute inset-0 w-full h-full object-contain p-1" />
        </div>
        
        <div className="pointer-events-auto group relative w-24 h-24 rounded-full bg-white backdrop-blur-md border-2 border-pink-500/30 flex items-center justify-center transition-all duration-500 hover:scale-150 hover:z-50 overflow-hidden cursor-pointer shadow-[0_0_15px_rgba(236,64,122,0.3)] hover:shadow-[0_0_30px_rgba(236,64,122,0.6)]">
           <img src="/mbm_logo.png" alt="MBM University Jodhpur" className="absolute inset-0 w-full h-full object-contain p-1" />
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 flex items-center justify-center min-h-screen p-4 pt-24 pb-16">
        <ChatInterface />
      </main>

      {/* Footer */}
      <footer className="fixed bottom-0 left-0 right-0 z-50 p-4 text-center text-white/30 text-sm backdrop-blur-sm bg-black/20">
        <p className="font-mono tracking-wider hover:text-white/60 transition-colors">Project made by - AARYAN , MBM University , CSE , 23UCSE4002</p>
      </footer>
    </div>
  );
}

export default App;
