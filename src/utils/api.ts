const BASE_URL = "http://127.0.0.1:9000"; // Адрес бекэнда

export async function searchVetInfo(query) {
  if (!query) return "Введите запрос"; // Проверка на пустой ввод

  try {
    const response = await fetch(`${BASE_URL}/search/?query=${encodeURIComponent(query)}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`Ошибка сервера: ${response.statusText}`);
    }

    const data = await response.json();
    return data.response || "Нет данных по запросу";
  } catch (error) {
    console.error("Ошибка запроса:", error);
    return "Ошибка при поиске информации";
  }
}
