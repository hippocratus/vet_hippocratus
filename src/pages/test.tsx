"use client";

import { useState } from "react";
import { searchVetInfo } from "@/utils/api";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Loader } from "lucide-react";
import { motion } from "framer-motion";

export default function TestPage() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setResponse("");

    try {
      const result = await searchVetInfo(query);
      setResponse(result);
    } catch (error) {
      console.error("Error fetching data:", error);
      setResponse("Error retrieving data. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-6">
      <div className="max-w-2xl w-full bg-white shadow-lg rounded-lg p-6">
        <h1 className="text-2xl font-semibold text-gray-800 text-center">Veterinary Information Search</h1>
        <div className="mt-4 flex gap-2">
          <Input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your query..."
            className="w-full border-gray-300 rounded-lg p-3"
          />
          <Button onClick={handleSearch} disabled={loading} className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg">
            {loading ? <Loader className="animate-spin" /> : "Search"}
          </Button>
        </div>

        {response && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="mt-6"
          >
            <Card>
              <CardContent className="p-4">
                <h3 className="text-lg font-semibold">Result:</h3>
                <p className="text-gray-700 mt-2">{response}</p>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>
    </div>
  );
}
