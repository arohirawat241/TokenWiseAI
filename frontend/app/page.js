"use client";

import { useState } from "react";
import axios from "axios";

export default function Home() {
  // Initialize with an empty object to prevent "property does not exist" errors
  const [result, setResult] = useState({}); 
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleOptimize = async () => {
    if (!prompt.trim()) return;
    
    setLoading(true);
    setError("");

    try {
      const response = await axios.post("http://localhost:8000/optimize", {
        prompt: prompt,
        system_prompt: "You are a helpful AI assistant.",
        model: "gpt-4o",
        model_limit: 128000,
      });
      setResult(response.data);
    } catch (err) {
      setError("Failed to connect to backend. Is the Python server running on port 8000?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-950 text-gray-100 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <header className="mb-10">
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <span className="text-yellow-400 text-4xl"></span> LLM Token Optimizer
          </h1>
          <p className="text-gray-400 mt-2">
            Intelligent middleware to minimize LLM costs and latency.
          </p>
        </header>

        {/* Stats Cards */}
        {result.original_tokens && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <StatCard label="Original Tokens" value={result.original_tokens} icon="📉" />
            <StatCard label="Optimized Tokens" value={result.optimized_tokens} icon="⚡" />
            <StatCard label="Compression" value={`${result.compression_percentage}%`} icon="📉" highlight />
            <StatCard label="Cost Saved" value={`$${result.estimated_cost_saved}`} icon="" />
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Input Section */}
          <div className="bg-gray-900 p-6 rounded-xl border border-gray-800">
            <h2 className="text-lg font-semibold mb-4 text-gray-300">Input Prompt</h2>
            <textarea
              className="w-full h-64 bg-gray-950 border border-gray-700 rounded-lg p-4 text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none font-mono text-sm"
              placeholder="Paste your bloated prompt here..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            />
            <button
              onClick={handleOptimize}
              disabled={loading || !prompt.trim()}
              className="mt-4 w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white font-semibold py-3 rounded-lg transition flex justify-center items-center gap-2"
            >
              {loading ? "⏳ Optimizing..." : "⚡ Optimize Prompt"}
            </button>
            {error && <p className="text-red-500 mt-2 text-sm">{error}</p>}
          </div>

          {/* Output Section */}
          <div className="bg-gray-900 p-6 rounded-xl border border-gray-800">
            <h2 className="text-lg font-semibold mb-4 text-gray-300">
              Optimization Result {result.strategy_used && <span className="text-xs bg-green-900 text-green-300 px-2 py-1 rounded ml-2">{result.strategy_used}</span>}
            </h2>
            
            <div className="bg-gray-950 rounded-lg p-4 h-64 overflow-y-auto border border-gray-700 text-gray-300 font-mono text-sm whitespace-pre-wrap">
              {result.optimized_prompt ? (
                result.optimized_prompt
              ) : (
                <span className="text-gray-600">
                  Optimized prompt will appear here...
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}

// Simple stat card component
function StatCard({ label, value, icon, highlight = false }) {
  return (
    <div
      className={`p-4 rounded-xl border ${highlight
        ? "bg-green-950/30 border-green-800"
        : "bg-gray-900 border-gray-800"}`}
    >
      <div className="flex items-center gap-3">
        <span className="text-2xl" aria-hidden="true">{icon}</span>
        <div>
          <p className="text-sm text-gray-400">{label}</p>
          <p className="text-xl font-semibold text-gray-100">{value}</p>
        </div>
      </div>
    </div>
  );
}