export type NormalizedResponse = {
  answerMarkdown: string;
};

export function normalizeResponse(raw: unknown): NormalizedResponse {
  if (typeof raw === "string") {
    return { answerMarkdown: raw };
  }

  if (raw && typeof raw === "object") {
    const data = raw as Record<string, unknown>;

    if (typeof data.answer_markdown === "string") {
      return { answerMarkdown: data.answer_markdown };
    }

    if (typeof data.answer === "string") {
      return { answerMarkdown: data.answer };
    }

    if (typeof data.text === "string") {
      return { answerMarkdown: data.text };
    }
  }

  if (raw == null) {
    return { answerMarkdown: "" };
  }

  try {
    return { answerMarkdown: JSON.stringify(raw) };
  } catch {
    return { answerMarkdown: String(raw) };
  }
}

