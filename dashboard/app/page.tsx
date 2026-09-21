"use client";
import { useState, useEffect } from "react";

const SAMPLE_TRANSCRIPT = "Great question! I'd be glad to help you with that. It is important to note that the current setup is super slow right now. As an AI language model, I think we should just move to PostgreSQL. In conclusion, what do you guys think?";

export default function Dashboard() {
  const [transcript, setTranscript] = useState("");
  const [kept, setKept] = useState("");
  const [dropped, setDropped] = useState("");
  const [noiseScore, setNoiseScore] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    const processTranscript = async () => {
      if (!transcript.trim()) {
        setKept("");
        setDropped("");
        setNoiseScore(0);
        return;
      }

      setIsProcessing(true);
      const res = await fetch("/api/extract", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transcript }),
      });

      if (res.ok) {
        const data = await res.json();
        setKept(data.kept);
        setDropped(data.dropped);
        setNoiseScore(data.noiseScore);
      }
      setIsProcessing(false);
    };

    const timeoutId = setTimeout(() => processTranscript(), 600);
    return () => clearTimeout(timeoutId);
  }, [transcript]);

  return (
    <div className="min-h-screen bg-gray-950 text-gray-200 p-8 font-sans">
      <div className="max-w-7xl mx-auto space-y-6">
        
        <header className="flex items-center justify-between border-b border-gray-800 pb-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-white">SIPA Signal</h1>
            <p className="text-gray-400 text-sm mt-1">AI Transcript Noise Extractor</p>
          </div>
          <div className="flex items-center space-x-3 bg-gray-900 px-4 py-2 rounded-lg border border-gray-800">
            <span className="text-gray-400 font-medium">Noise Score:</span>
            <span className={`text-2xl font-mono font-bold ${noiseScore > 50 ? 'text-red-400' : 'text-emerald-400'}`}>
              {noiseScore}%
            </span>
          </div>
        </header>

        <div className="flex space-x-4">
          <button 
            onClick={() => setTranscript(SAMPLE_TRANSCRIPT)}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold rounded-md transition-colors"
          >
            Load Noisy Sample
          </button>
          <button 
            onClick={() => setTranscript("")}
            className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 text-sm font-semibold rounded-md transition-colors"
          >
            Clear
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-2 relative">
            <label htmlFor="transcript-input" className="text-sm font-semibold text-gray-400 uppercase tracking-wider block">
              Raw AI Transcript
            </label>
            <textarea 
              id="transcript-input"
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
              placeholder="Paste noisy AI transcript here..."
              className="w-full h-[500px] bg-gray-900 border border-gray-700 rounded-lg p-4 text-gray-200 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 focus:outline-none resize-none leading-relaxed"
            />
          </div>

          <div className="space-y-6">
            <div className="space-y-2 relative">
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold text-emerald-400 uppercase tracking-wider">Signal (Kept)</span>
                {isProcessing && <span className="text-xs text-emerald-500 animate-pulse">Processing...</span>}
              </div>
              <div className="w-full h-[235px] bg-gray-900 border border-emerald-900/50 rounded-lg p-4 text-gray-100 overflow-y-auto leading-relaxed">
                {kept || (!transcript ? <span className="text-gray-600 italic">Clean signal will appear here...</span> : null)}
              </div>
            </div>

            <div className="space-y-2 relative">
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold text-red-400 uppercase tracking-wider">Noise (Dropped)</span>
                {isProcessing && <span className="text-xs text-red-500 animate-pulse">Processing...</span>}
              </div>
              <div className="w-full h-[235px] bg-gray-900 border border-red-900/50 rounded-lg p-4 text-gray-500 line-through overflow-y-auto leading-relaxed whitespace-pre-wrap">
                
                {/* State 1: We found noise and dropped it */}
                {dropped && <span>{dropped}</span>}

                {/* State 2: We processed the text, found no noise, and the transcript is not empty */}
                {!dropped && transcript && !isProcessing && (
                  <span className="text-emerald-500/80 font-medium italic no-underline block mt-2">✨ Zero filler detected. Pure signal!</span>
                )}

                {/* State 3: Waiting for input or currently processing */}
                {!dropped && (!transcript || isProcessing) && (
                  <span className="text-gray-600 italic no-underline">Filtered filler will appear here...</span>
                )}

              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}