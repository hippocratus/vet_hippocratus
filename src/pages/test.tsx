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
    <div className="flex flex-col items-center min-h-screen bg-gray-100 p-6">
      <div className="bg-white shadow-lg rounded-xl p-6 w-full max-w-2xl">
        <h1 className="text-2xl font-bold text-gray-800 text-center">
          Veterinary Information Search
        </h1>
        <p className="text-gray-500 text-center mt-2">
          Find veterinary-related information quickly and easily.
        </p>

        <div className="flex flex-col md:flex-row mt-6">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your query..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleSearch}
            className="mt-3 md:mt-0 md:ml-3 bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition flex items-center"
            disabled={loading}
          >
            {loading ? (
              <span className="animate-spin border-2 border-white border-t-transparent rounded-full w-5 h-5"></span>
            ) : (
              "Search"
            )}
          </button>
        </div>

        <div className="mt-6 bg-gray-50 p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-800">Result:</h3>
          <p className="text-gray-600 mt-2 whitespace-pre-wrap">{response || "No results yet"}</p>
        </div>
      </div>
    </div>
  );
}
