"use client"; // Гарантируем, что хук useState не сломается на сервере

import { useState } from "react";
import { searchVetInfo } from "../utils/api";

export default function TestPage() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");

  const handleSearch = async () => {
    if (!query.trim()) {
      setResponse("Введите запрос перед поиском");
      return;
    }

    const result = await searchVetInfo(query);
    setResponse(result);
  };

  return (
    <div style={{ padding: 20, fontFamily: "Arial, sans-serif" }}>
      <h1>Поиск ветеринарной информации</h1>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Введите запрос"
        style={{
          padding: 8,
          marginRight: 10,
          borderRadius: 4,
          border: "1px solid #ccc",
        }}
      />
      <button onClick={handleSearch} style={{ padding: 8, borderRadius: 4 }}>
        Искать
      </button>
      <div style={{ marginTop: 20 }}>
        <h3>Результат:</h3>
        <p>{response}</p>
      </div>
    </div>
  );
}
