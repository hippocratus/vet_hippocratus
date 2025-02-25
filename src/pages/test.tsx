"use client";

import React, { useState } from "react";
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
    <div className="flex flex-col items-center min-h-screen bg-gradient-to-r from-blue-200 via-purple-200 to-pink-200 p-8">
      {/* Основной контейнер */}
      <div className="bg-white shadow-2xl rounded-3xl p-10 max-w-4xl w-full text-center">
        <h1 className="text-4xl font-extrabold text-gray-800">
          Veterinary Information Portal
        </h1>
        <p className="text-lg text-gray-600 mt-3">
          Find comprehensive veterinary information at your fingertips.
        </p>

        {/* Блок с SVG-иллюстрациями */}
        <div className="flex flex-wrap justify-center gap-6 mt-8">
          {/* Иллюстрация 1 */}
          <div className="bg-blue-100 p-4 rounded-lg shadow-lg">
            <svg
              width="180"
              height="180"
              viewBox="0 0 400 300"
              xmlns="http://www.w3.org/2000/svg"
            >
              <rect width="400" height="300" fill="#d3eaf2" />
              <polygon points="140,100 200,60 260,100" fill="#a66e3a" />
              <circle cx="80" cy="80" r="20" fill="#f3d9c2" />
            </svg>
          </div>

          {/* Иллюстрация 2 */}
          <div className="bg-purple-100 p-4 rounded-lg shadow-lg">
            <svg
              width="180"
              height="180"
              viewBox="0 0 400 300"
              xmlns="http://www.w3.org/2000/svg"
            >
              <rect width="400" height="300" fill="#f0e6f6" />
              <polygon points="120,90 200,40 280,90" fill="#c76e3a" />
              <circle cx="70" cy="70" r="20" fill="#f3d9c2" />
            </svg>
          </div>

          {/* Иллюстрация 3 */}
          <div className="bg-green-100 p-4 rounded-lg shadow-lg">
            <svg
              width="180"
              height="180"
              viewBox="0 0 400 300"
              xmlns="http://www.w3.org/2000/svg"
            >
              <rect width="400" height="300" fill="#e6f7d4" />
              <polygon points="130,110 200,70 270,110" fill="#9e6b3a" />
              <circle cx="90" cy="90" r="20" fill="#f3d9c2" />
            </svg>
          </div>
        </div>

        {/* Поле поиска */}
        <div className="flex flex-col md:flex-row gap-4 mt-8">
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

        {/* Блок с результатами */}
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
