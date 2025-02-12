const BASE_URL = "http://127.0.0.1:9000"; // Адрес твоего бэкенда

export async function searchVetInfo(query: string) {
  if (!query) return "Ошибка: Пустой запрос";

  try {
    const response = await fetch(`${BASE_URL}/search/?query=${encodeURIComponent(query)}`, {
      method: "GET",
    });

    if (!response.ok) {
      throw new Error(`Ошибка запроса: ${response.statusText}`);
    }

    const data = await response.json();
    return data.response || "Нет данных.";
  } catch (error) {
    console.error("Ошибка API:", error);
    return "Ошибка при получении данных.";
  }
}
