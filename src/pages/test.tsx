"use client";

import { useState } from "react";
import { searchVetInfo } from "@/utils/api";

export default function TestPage() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const result = await searchVetInfo(query);
      setResponse(result);
    } catch (error) {
      console.error("Error fetching data:", error);
      setResponse("Failed to retrieve data.");
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-200 via-purple-200 to-pink-200 flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl shadow-2xl p-8 max-w-4xl w-full">
        <h1 className="text-4xl font-extrabold text-center text-gray-800 mb-4">
          Veterinary Information Portal
        </h1>
        <p className="text-lg text-center text-gray-600 mb-8">
          Discover comprehensive veterinary information at your fingertips.
        </p>

        {/* Секция с SVG-иллюстрациями */}
        <div className="flex flex-wrap justify-center gap-6 mb-8">
          {/* Иллюстрация 1 */}
          <svg
            width="180"
            height="180"
            viewBox="0 0 400 300"
            xmlns="http://www.w3.org/2000/svg"
            className="rounded-xl shadow-lg"
          >
            <rect width="400" height="300" fill="#d3eaf2" />
            <rect
              x="140"
              y="100"
              width="120"
              height="80"
              fill="#ffd766"
              stroke="#444"
              strokeWidth="2"
            />
            <polygon points="140,100 200,60 260,100" fill="#a66e3a" />
            <circle cx="80" cy="80" r="20" fill="#f3d9c2" />
            <rect x="70" y="100" width="20" height="40" fill="#ffffff" />
            <rect x="66" y="100" width="28" height="10" fill="#ffffff" />
            <line x1="70" y1="140" x2="70" y2="150" stroke="#000" strokeWidth="2" />
            <line x1="90" y1="140" x2="90" y2="150" stroke="#000" strokeWidth="2" />
            <line x1="66" y1="110" x2="55" y2="100" stroke="#000" strokeWidth="2" />
            <line x1="94" y1="110" x2="105" y2="100" stroke="#000" strokeWidth="2" />
            <circle
              cx="220"
              cy="170"
              r="20"
              fill="#ffffff"
              stroke="#444"
              strokeWidth="2"
            />
            <circle
              cx="220"
              cy="195"
              r="15"
              fill="#ffffff"
              stroke="#444"
              strokeWidth="2"
            />
            <circle cx="215" cy="168" r="4" fill="#000" />
            <ellipse
              cx="225"
              cy="168"
              rx="2"
              ry="4"
              fill="#000"
              transform="rotate(20 225 168)"
            />
            <line x1="220" y1="185" x2="220" y2="205" stroke="#444" strokeWidth="2" />
            <line x1="230" y1="185" x2="230" y2="205" stroke="#444" strokeWidth="2" />
            <line x1="210" y1="200" x2="210" y2="215" stroke="#444" strokeWidth="2" />
            <line x1="220" y1="200" x2="220" y2="215" stroke="#444" strokeWidth="2" />
            <circle
              cx="270"
              cy="170"
              r="15"
              fill="#666"
              stroke="#444"
              strokeWidth="2"
            />
            <polygon points="265,157 260,150 270,155" fill="#444" />
            <polygon points="275,157 280,150 270,155" fill="#444" />
            <circle
              cx="270"
              cy="190"
              r="12"
              fill="#666"
              stroke="#444"
              strokeWidth="2"
            />
            <line x1="270" y1="178" x2="270" y2="185" stroke="#000" strokeWidth="2" />
            <line x1="265" y1="180" x2="275" y2="180" stroke="#000" strokeWidth="2" />
            <line x1="265" y1="195" x2="265" y2="205" stroke="#444" strokeWidth="2" />
            <line x1="275" y1="195" x2="275" y2="205" stroke="#444" strokeWidth="2" />
            <line x1="282" y1="190" x2="290" y2="185" stroke="#444" strokeWidth="2" />
          </svg>

          {/* Иллюстрация 2 */}
          <svg
            width="180"
            height="180"
            viewBox="0 0 400 300"
            xmlns="http://www.w3.org/2000/svg"
            className="rounded-xl shadow-lg"
          >
            <rect width="400" height="300" fill="#f0e6f6" />
            <rect
              x="120"
              y="90"
              width="160"
              height="90"
              fill="#ffae42"
              stroke="#444"
              strokeWidth="2"
            />
            <polygon points="120,90 200,40 280,90" fill="#c76e3a" />
            <circle cx="70" cy="70" r="20" fill="#f3d9c2" />
            <rect x="60" y="90" width="20" height="40" fill="#ffffff" />
            <rect x="56" y="90" width="28" height="10" fill="#ffffff" />
            <line x1="60" y1="130" x2="60" y2="140" stroke="#000" strokeWidth="2" />
            <line x1="80" y1="130" x2="80" y2="140" stroke="#000" strokeWidth="2" />
            <line x1="56" y1="100" x2="45" y2="110" stroke="#000" strokeWidth="2" />
            <line x1="84" y1="100" x2="95" y2="90" stroke="#000" strokeWidth="2" />
            <circle
              cx="230"
              cy="180"
              r="20"
              fill="#ffc"
              stroke="#444"
              strokeWidth="2"
            />
            <circle
              cx="230"
              cy="205"
              r="15"
              fill="#ffc"
              stroke="#444"
              strokeWidth="2"
            />
            <circle cx="225" cy="178" r="4" fill="#000" />
            <ellipse
              cx="235"
              cy="178"
              rx="2"
              ry="4"
              fill="#000"
              transform="rotate(20 235 178)"
            />
            <line x1="230" y1="195" x2="230" y2="215" stroke="#444" strokeWidth="2" />
            <line x1="240" y1="195" x2="240" y2="215" stroke="#444" strokeWidth="2" />
            <line x1="220" y1="210" x2="220" y2="225" stroke="#444" strokeWidth="2" />
            <line x1="230" y1="210" x2="230" y2="225" stroke="#444" strokeWidth="2" />
            <circle
              cx="280"
              cy="180"
              r="15"
              fill="#333"
              stroke="#444"
              strokeWidth="2"
            />
            <polygon points="275,167 270,160 280,165" fill="#444" />
            <polygon points="285,167 290,160 280,165" fill="#444" />
            <circle
              cx="280"
              cy="200"
              r="12"
              fill="#333"
              stroke="#444"
              strokeWidth="2"
            />
            <line x1="280" y1="188" x2="280" y2="195" stroke="#000" strokeWidth="2" />
            <line x1="275" y1="190" x2="285" y2="190" stroke="#000" strokeWidth="2" />
            <line x1="275" y1="205" x2="275" y2="215" stroke="#444" strokeWidth="2" />
            <line x1="285" y1="205" x2="285" y2="215" stroke="#444" strokeWidth="2" />
            <line x1="292" y1="200" x2="300" y2="195" stroke="#444" strokeWidth="2" />
          </svg>

          {/* Иллюстрация 3 */}
          <svg
            width="180"
            height="180"
            viewBox="0 0 400 300"
            xmlns="http://www.w3.org/2000/svg"
            className="rounded-xl shadow-lg"
          >
            <rect width="400" height="300" fill="#e6f7d4" />
            <rect
              x="130"
              y="110"
              width="140"
              height="70"
              fill="#ffe680"
              stroke="#444"
              strokeWidth="2"
            />
            <polygon points="130,110 200,70 270,110" fill="#9e6b3a" />
            <circle cx="90" cy="90" r="20" fill="#f3d9c2" />
            <rect x="80" y="110" width="20" height="40" fill="#ffffff" />
            <rect x="76" y="110" width="28" height="10" fill="#ffffff" />
            <line x1="80" y1="150" x2="80" y2="160" stroke="#000" strokeWidth="2" />
            <line x1="100" y1="150" x2="100" y2="160" stroke="#000" strokeWidth="2" />
            <line x1="76" y1="120" x2="65" y2="115" stroke="#000" strokeWidth="2" />
            <line x1="104" y1="120" x2="115" y2="125" stroke="#000" strokeWidth="2" />
            <circle
              cx="210"
              cy="170"
              r="20"
              fill="#d2a679"
              stroke="#444"
              strokeWidth="2"
            />
            <circle
              cx="210"
              cy="195"
              r="15"
              fill="#d2a679"
              stroke="#444"
              strokeWidth="2"
            />
            <circle cx="205" cy="168" r="4" fill="#000" />
            <ellipse
              cx="215"
              cy="168"
              rx="2"
              ry="4"
              fill="#000"
              transform="rotate(20 215 168)"
            />
            <line x1="210" y1="185" x2="210" y2="205" stroke="#444" strokeWidth="2" />
            <line x1="220" y1="185" x2="220" y2="205" stroke="#444" strokeWidth="2" />
            <line x1="200" y1="200" x2="200" y2="215" stroke="#444" strokeWidth="2" />
            <line x1="210" y1="200" x2="210" y2="215" stroke="#444" strokeWidth="2" />
            <circle
              cx="260"
              cy="170"
              r="15"
              fill="#888"
              stroke="#444"
              strokeWidth="2"
            />
            <polygon points="255,157 250,150 260,155" fill="#444" />
            <polygon points="265,157 270,150 260,155" fill="#444" />
            <circle
              cx="260"
              cy="190"
              r="12"
              fill="#888"
              stroke="#444"
              strokeWidth="2"
            />
            <line x1="260" y1="178" x2="260" y2="185" stroke="#000" strokeWidth="2" />
            <line x1="255" y1="180" x2="265" y2="180" stroke="#000" strokeWidth="2" />
            <line x1="255" y1="195" x2="255" y2="205" stroke="#444" strokeWidth="2" />
            <line x1="265" y1="195" x2="265" y2="205" stroke="#444" strokeWidth="2" />
            <line x1="272" y1="190" x2="280" y2="185" stroke="#444" strokeWidth="2" />
          </svg>
        </div>

        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your query..."
            className="flex-1 px-5 py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-4 focus:ring-blue-300 transition"
          />
          <button
            onClick={handleSearch}
            className="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-8 py-3 rounded-full shadow-md hover:from-blue-600 hover:to-purple-600 transition flex items-center justify-center"
            disabled={loading}
          >
            {loading ? (
              <span className="animate-spin border-4 border-white border-t-transparent rounded-full w-6 h-6"></span>
            ) : (
              "Search"
            )}
          </button>
        </div>

        <div className="bg-gray-100 rounded-xl p-6 shadow-inner mt-8">
          <h3 className="text-2xl font-semibold text-gray-800 mb-2">Result:</h3>
          <p className="text-gray-700 whitespace-pre-wrap">
            {response || "No results yet"}
          </p>
        </div>
      </div>
    </div>
  );
}
