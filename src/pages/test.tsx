"use client";

import { useState } from "react";
import { searchVetInfo } from "@/utils/api"; // <-- ВАЖНО: абсолютный импорт

export default function TestPage() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");

  const handleSearch = async () => {
    if (!query.trim()) return; // Проверка на пустую строку

    try {
      const result = await searchVetInfo(query);
      setResponse(result);
    } catch (error) {
      console.error("Ошибка при запросе:", error);
      setResponse("Ошибка при получении данных");
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Поиск ветеринарной информации</h1>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Введите запрос"
      />
      <button onClick={handleSearch}>Искать</button>
      <div>
        <h3>Результат:</h3>
        <p>{response}</p>
      </div>
    </div>
  );
}
