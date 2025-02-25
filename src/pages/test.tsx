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
    <div className="min-h-screen bg-gradient-to-br from-green-200 via-blue-200 to-purple-200 flex items-center justify-center p-4">
      <div className="max-w-lg w-full bg-white rounded-3xl shadow-xl p-8">
        <h1 className="text-3xl font-bold text-center text-gray-800 mb-2">
          Veterinary Information Portal
        </h1>
        <p className="text-gray-500 text-center mb-6">
          Find comprehensive veterinary information at your fingertips.
        </p>

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

        <div className="bg-gray-50 rounded-xl p-6 shadow-inner">
          <h3 className="text-xl font-semibold text-gray-800 mb-2">Result:</h3>
          <p className="text-gray-600 whitespace-pre-wrap">
            {response || "No results yet"}
          </p>
        </div>
      </div>
    </div>
  );
}
