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

        {/* Секция с иллюстрациями */}
        <div className="flex flex-wrap gap-4 justify-center mt-6">
          {/* Иллюстрация 1 */}
          <svg
            width="180"
            height="auto"
            viewBox="0 0 400 300"
            xmlns="http://www.w3.org/2000/svg"
          >
            <rect width="400" height="300" fill="#d3eaf2" />
            <rect
              x="140"
              y="100"
              width="120"
              height="80"
              fill="#ffd766"
              stro
