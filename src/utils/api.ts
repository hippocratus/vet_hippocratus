const BASE_URL = "http://127.0.0.1:9000"; // Адрес твоего бэкенда

export async function searchVetInfo(query: string): Promise<string> {
  if (!query.trim()) return "Введите корректный запрос";

  try {
    const response = await fetch(`${BASE_URL}/search/?query=${encodeURIComponent(query)}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`Ошибка запроса: ${response.status}`);
    }

    const data = await response.json();
    return data.response || "Нет данных по вашему запросу";
  } catch (error) {
    console.error("Ошибка при запросе:", error);
    return "Ошибка при подключении к серверу";
  }
}
