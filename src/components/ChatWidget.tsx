"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { searchVetInfo } from "@/utils/api";
import { normalizeResponse } from "@/utils/normalizeResponse";

type MessageRole = "user" | "assistant";
type GroupId = "pet" | "farm" | "wild";
type RegionId = "EU" | "US" | "LATAM" | "OTHER";
type Lang = "en" | "de" | "pt-BR";

type SpeciesId =
  | "dog"
  | "cat"
  | "bird_companion"
  | "fish_ornamental"
  | "reptile"
  | "rodent"
  | "rabbit"
  | "ferret"
  | "minipig"
  | "horse"
  | "other"
  | "cattle"
  | "sheep"
  | "goat"
  | "pig"
  | "poultry_farm"
  | "fish_aquaculture"
  | "mammal"
  | "bird_wild"
  | "reptile_amphibian";

type Message = {
  id: string;
  role: MessageRole;
  content: string;
  created_at: number;
};

type ChatStorage = {
  meta: {
    session_id: string;
    updated_at: number;
  };
  messages: Message[];
};

type IntakeStorage = {
  group: GroupId | "";
  species: SpeciesId | "";
  region: RegionId | "";
};

const CHAT_STORAGE_KEY = "vethipocratus_chat_v1";
const LANG_STORAGE_KEY = "vethipocratus_lang_v1";
const INTAKE_STORAGE_KEY = "vethipocratus_intake_v1";

const SPECIES_BY_GROUP: Record<GroupId, SpeciesId[]> = {
  pet: [
    "dog",
    "cat",
    "bird_companion",
    "fish_ornamental",
    "reptile",
    "rodent",
    "rabbit",
    "ferret",
    "minipig",
    "horse",
    "other",
  ],
  farm: [
    "cattle",
    "sheep",
    "goat",
    "pig",
    "poultry_farm",
    "fish_aquaculture",
    "horse",
    "rabbit",
    "minipig",
    "other",
  ],
  wild: ["mammal", "bird_wild", "reptile_amphibian", "other"],
};

const REGION_OPTIONS: RegionId[] = ["EU", "US", "LATAM", "OTHER"];

const strings = {
  en: {
    title: "Veterinary Intake Chat",
    language: "Language",
    reset: "Reset",
    selectType: "Select animal type",
    selectSpecies: "Select species",
    selectRegion: "Select region",
    group_pet: "Pet",
    group_farm: "Farm",
    group_wild: "Wild",
    region_EU: "European Union (EU)",
    region_US: "United States (US)",
    region_LATAM: "Latin America (LATAM)",
    region_OTHER: "Other",
    dog: "Dog",
    cat: "Cat",
    bird_companion: "Companion bird",
    fish_ornamental: "Ornamental fish",
    reptile: "Reptile",
    rodent: "Rodent",
    rabbit: "Rabbit",
    ferret: "Ferret",
    minipig: "Mini pig",
    horse: "Horse",
    other: "Other",
    cattle: "Cattle",
    sheep: "Sheep",
    goat: "Goat",
    pig: "Pig",
    poultry_farm: "Poultry",
    fish_aquaculture: "Aquaculture (fish farming)",
    mammal: "Mammal",
    bird_wild: "Wild bird",
    reptile_amphibian: "Reptile / amphibian",
    contextReady: "Context selected. You can start chatting.",
    contextPending: "Complete intake to start chat.",
    sessionLabel: "Session",
    copyLastAnswer: "Copy last answer",
    newChat: "New chat",
    emptyState: "Send a message to start.",
    placeholder: "Type your question...",
    send: "Send",
    typing: "Assistant is typing...",
    retry: "Retry",
    error: "Failed to retrieve data. Please try again.",
  },
  de: {
    title: "Veterinär-Chat mit Intake",
    language: "Sprache",
    reset: "Zurücksetzen",
    selectType: "Tierart wählen",
    selectSpecies: "Art auswählen",
    selectRegion: "Region wählen",
    group_pet: "Haustier",
    group_farm: "Nutztiere",
    group_wild: "Wildtier",
    region_EU: "Europäische Union (EU)",
    region_US: "USA",
    region_LATAM: "Lateinamerika",
    region_OTHER: "Sonstiges",
    dog: "Hund",
    cat: "Katze",
    bird_companion: "Ziervogel",
    fish_ornamental: "Zierfisch",
    reptile: "Reptil",
    rodent: "Nagetiere",
    rabbit: "Kaninchen",
    ferret: "Frettchen",
    minipig: "Minischwein",
    horse: "Pferd",
    other: "Sonstiges",
    cattle: "Rinder",
    sheep: "Schaf",
    goat: "Ziege",
    pig: "Schwein",
    poultry_farm: "Geflügel (Landwirtschaft)",
    fish_aquaculture: "Fischzucht (Aquakultur)",
    mammal: "Säugetier",
    bird_wild: "Wildvogel",
    reptile_amphibian: "Reptil / Amphibie",
    contextReady: "Kontext gewählt. Chat kann starten.",
    contextPending: "Bitte Intake abschließen, um zu chatten.",
    sessionLabel: "Sitzung",
    copyLastAnswer: "Letzte Antwort kopieren",
    newChat: "Neuer Chat",
    emptyState: "Senden Sie eine Nachricht, um zu starten.",
    placeholder: "Frage eingeben...",
    send: "Senden",
    typing: "Assistent schreibt...",
    retry: "Erneut versuchen",
    error: "Abruf fehlgeschlagen. Bitte erneut versuchen.",
  },
  "pt-BR": {
    title: "Chat Veterinário com Triagem",
    language: "Idioma",
    reset: "Redefinir",
    selectType: "Escolha o tipo de animal",
    selectSpecies: "Escolha a espécie",
    selectRegion: "Escolha a região",
    group_pet: "Animal de estimação",
    group_farm: "Animal de produção",
    group_wild: "Animal selvagem",
    region_EU: "União Europeia (UE)",
    region_US: "Estados Unidos (EUA)",
    region_LATAM: "América Latina",
    region_OTHER: "Outro",
    dog: "Cão",
    cat: "Gato",
    bird_companion: "Ave de companhia",
    fish_ornamental: "Peixe ornamental",
    reptile: "Réptil",
    rodent: "Roedor",
    rabbit: "Coelho",
    ferret: "Furão",
    minipig: "Miniporco",
    horse: "Cavalo",
    other: "Outro",
    cattle: "Bovino",
    sheep: "Ovelha",
    goat: "Cabra",
    pig: "Porco",
    poultry_farm: "Aves de criação",
    fish_aquaculture: "Piscicultura",
    mammal: "Mamífero",
    bird_wild: "Ave silvestre",
    reptile_amphibian: "Réptil / anfíbio",
    contextReady: "Contexto selecionado. Você já pode conversar.",
    contextPending: "Conclua a triagem para começar o chat.",
    sessionLabel: "Sessão",
    copyLastAnswer: "Copiar última resposta",
    newChat: "Novo chat",
    emptyState: "Envie uma mensagem para começar.",
    placeholder: "Digite sua pergunta...",
    send: "Enviar",
    typing: "Assistente digitando...",
    retry: "Tentar novamente",
    error: "Falha ao buscar dados. Tente novamente.",
  },
};

function createId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) return crypto.randomUUID();
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function loadChatState(): ChatStorage {
  const fallback: ChatStorage = { meta: { session_id: createId(), updated_at: Date.now() }, messages: [] };
  if (typeof window === "undefined") return fallback;
  try {
    const raw = window.localStorage.getItem(CHAT_STORAGE_KEY);
    if (!raw) return fallback;
    const parsed = JSON.parse(raw) as ChatStorage;
    if (!parsed?.meta?.session_id || !Array.isArray(parsed?.messages)) return fallback;
    return parsed;
  } catch {
    return fallback;
  }
}

function saveChatState(sessionId: string, messages: Message[]): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(
    CHAT_STORAGE_KEY,
    JSON.stringify({ meta: { session_id: sessionId, updated_at: Date.now() }, messages }),
  );
}

function loadLang(): Lang {
  if (typeof window === "undefined") return "en";
  const raw = window.localStorage.getItem(LANG_STORAGE_KEY);
  return raw === "de" || raw === "pt-BR" || raw === "en" ? raw : "en";
}

function loadIntake(): IntakeStorage {
  if (typeof window === "undefined") return { group: "", species: "", region: "" };
  try {
    const raw = window.localStorage.getItem(INTAKE_STORAGE_KEY);
    if (!raw) return { group: "", species: "", region: "" };
    const parsed = JSON.parse(raw) as IntakeStorage;
    return {
      group: parsed?.group ?? "",
      species: parsed?.species ?? "",
      region: parsed?.region ?? "",
    };
  } catch {
    return { group: "", species: "", region: "" };
  }
}

function isTransportError(text: string): boolean {
  return text.includes("Ошибка при подключении") || text.includes("Failed to retrieve data");
}

function buildPrompt(userText: string, group: GroupId, species: SpeciesId, region: RegionId | ""): string {
  const context = `[CONTEXT]\ngroup=${group}\nspecies=${species}\nregion=${region}\n[/CONTEXT]`;
  return `${context}\n\n${userText}`;
}

function OptionButton({
  active,
  label,
  onClick,
}: {
  active: boolean;
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-2xl border px-4 py-3 text-left text-sm transition ${
        active
          ? "border-teal-500 bg-teal-100 text-teal-900 shadow-sm"
          : "border-teal-100 bg-white text-slate-700 hover:border-teal-300"
      }`}
    >
      {label}
    </button>
  );
}

export default function ChatWidget() {
  const [sessionId, setSessionId] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [lastFailedUserId, setLastFailedUserId] = useState<string | null>(null);
  const [lang, setLang] = useState<Lang>("en");
  const [group, setGroup] = useState<GroupId | "">("");
  const [species, setSpecies] = useState<SpeciesId | "">("");
  const [region, setRegion] = useState<RegionId | "">("");
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const chat = loadChatState();
    const intake = loadIntake();
    setSessionId(chat.meta.session_id);
    setMessages(chat.messages);
    setLang(loadLang());
    setGroup(intake.group);
    setSpecies(intake.species);
    setRegion(intake.region);
  }, []);

  useEffect(() => {
    if (sessionId) saveChatState(sessionId, messages);
  }, [messages, sessionId]);

  useEffect(() => {
    if (typeof window !== "undefined") {
      window.localStorage.setItem(LANG_STORAGE_KEY, lang);
    }
  }, [lang]);

  useEffect(() => {
    if (typeof window !== "undefined") {
      window.localStorage.setItem(INTAKE_STORAGE_KEY, JSON.stringify({ group, species, region }));
    }
  }, [group, species, region]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading, error]);

  const t = strings[lang];
  const speciesOptions = group ? SPECIES_BY_GROUP[group] : [];
  const needsRegion = group === "farm" || group === "wild";
  const chatEnabled = Boolean(group && species && (!needsRegion || region));

  const lastAssistantAnswer = useMemo(() => {
    for (let i = messages.length - 1; i >= 0; i -= 1) if (messages[i].role === "assistant") return messages[i].content;
    return "";
  }, [messages]);

  const executeRequest = async (visibleUserText: string) => {
    if (!group || !species) return;
    const payloadText = buildPrompt(visibleUserText, group, species, needsRegion ? region : "");

    setLoading(true);
    setError("");

    try {
      const rawResult = await searchVetInfo(payloadText);
      const normalized = normalizeResponse(rawResult);
      const content = normalized.answerMarkdown || "(empty response)";

      if (isTransportError(content)) {
        setError(t.error);
        return;
      }

      setMessages((prev) => [
        ...prev,
        { id: createId(), role: "assistant", content, created_at: Date.now() },
      ]);
      setLastFailedUserId(null);
    } catch (requestError) {
      console.error("Error fetching data:", requestError);
      setError(t.error);
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async () => {
    const trimmed = query.trim();
    if (!trimmed || loading || !chatEnabled) return;

    const userMessage: Message = { id: createId(), role: "user", content: trimmed, created_at: Date.now() };
    setMessages((prev) => [...prev, userMessage]);
    setLastFailedUserId(userMessage.id);
    setQuery("");
    await executeRequest(trimmed);
  };

  const handleRetry = async () => {
    if (loading || !lastFailedUserId) return;
    const userMessage = messages.find((msg) => msg.id === lastFailedUserId && msg.role === "user");
    if (!userMessage) return;
    await executeRequest(userMessage.content);
  };

  const clearChat = () => {
    setSessionId(createId());
    setMessages([]);
    setQuery("");
    setError("");
    setLastFailedUserId(null);
    if (typeof window !== "undefined") window.localStorage.removeItem(CHAT_STORAGE_KEY);
  };

  const handleResetAll = () => {
    clearChat();
    setGroup("");
    setSpecies("");
    setRegion("");
    if (typeof window !== "undefined") window.localStorage.removeItem(INTAKE_STORAGE_KEY);
  };

  const handleNewChat = () => clearChat();

  const handleCopyLastAnswer = async () => {
    if (!lastAssistantAnswer || typeof navigator === "undefined" || !navigator.clipboard) return;
    try {
      await navigator.clipboard.writeText(lastAssistantAnswer);
    } catch (copyError) {
      console.error("Clipboard copy failed:", copyError);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-teal-50 via-emerald-50 to-white px-3 py-4 sm:px-6">
      <div className="mx-auto flex h-[calc(100vh-2rem)] w-full max-w-[470px] flex-col overflow-hidden rounded-[28px] border border-teal-100 bg-white shadow-[0_12px_40px_rgba(13,148,136,0.15)]">
        <header className="sticky top-0 z-10 border-b border-teal-100 bg-white/95 px-4 py-3 backdrop-blur">
          <div className="flex items-center justify-between gap-2">
            <h1 className="text-base font-semibold text-teal-900">{t.title}</h1>
            <button
              type="button"
              onClick={handleResetAll}
              className="rounded-full border border-teal-200 px-3 py-1.5 text-xs font-medium text-teal-900 hover:bg-teal-50"
            >
              {t.reset}
            </button>
          </div>
          <div className="mt-2 flex items-center justify-between">
            <p className="text-xs text-slate-500">
              {t.sessionLabel}: {sessionId.slice(0, 8)}
            </p>
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-500">{t.language}</span>
              <select
                value={lang}
                onChange={(event) => setLang(event.target.value as Lang)}
                className="rounded-lg border border-teal-200 bg-white px-2 py-1 text-xs text-slate-700"
              >
                <option value="en">EN</option>
                <option value="de">DE</option>
                <option value="pt-BR">pt-BR</option>
              </select>
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto px-4 py-3">
          <section className="rounded-2xl border border-teal-100 bg-teal-50/60 p-3 shadow-sm">
            <h2 className="mb-2 text-sm font-semibold text-teal-900">{t.selectType}</h2>
            <div className="grid grid-cols-1 gap-2">
              <OptionButton
                active={group === "pet"}
                label={t.group_pet}
                onClick={() => {
                  setGroup("pet");
                  setSpecies("");
                  setRegion("");
                }}
              />
              <OptionButton
                active={group === "farm"}
                label={t.group_farm}
                onClick={() => {
                  setGroup("farm");
                  setSpecies("");
                  setRegion("");
                }}
              />
              <OptionButton
                active={group === "wild"}
                label={t.group_wild}
                onClick={() => {
                  setGroup("wild");
                  setSpecies("");
                  setRegion("");
                }}
              />
            </div>
          </section>

          {group && (
            <section className="mt-3 rounded-2xl border border-teal-100 bg-white p-3 shadow-sm">
              <h2 className="mb-2 text-sm font-semibold text-teal-900">{t.selectSpecies}</h2>
              <div className="grid grid-cols-1 gap-2">
                {speciesOptions.map((item) => (
                  <OptionButton key={item} active={species === item} label={t[item]} onClick={() => setSpecies(item)} />
                ))}
              </div>
            </section>
          )}

          {group && needsRegion && (
            <section className="mt-3 rounded-2xl border border-teal-100 bg-white p-3 shadow-sm">
              <h2 className="mb-2 text-sm font-semibold text-teal-900">{t.selectRegion}</h2>
              <div className="grid grid-cols-1 gap-2">
                {REGION_OPTIONS.map((item) => (
                  <OptionButton
                    key={item}
                    active={region === item}
                    label={t[`region_${item}` as keyof typeof t] as string}
                    onClick={() => setRegion(item)}
                  />
                ))}
              </div>
            </section>
          )}

          <section className="mt-3 rounded-2xl border border-teal-100 bg-white p-3 shadow-sm">
            <div className="mb-2 flex items-center justify-between gap-2">
              <p className="text-xs text-slate-500">{chatEnabled ? t.contextReady : t.contextPending}</p>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={handleCopyLastAnswer}
                  disabled={!lastAssistantAnswer}
                  className="rounded-full border border-slate-200 px-2.5 py-1 text-[11px] text-slate-600 disabled:opacity-40"
                >
                  {t.copyLastAnswer}
                </button>
                <button
                  type="button"
                  onClick={handleNewChat}
                  className="rounded-full border border-slate-200 px-2.5 py-1 text-[11px] text-slate-600"
                >
                  {t.newChat}
                </button>
              </div>
            </div>

            <div className="max-h-[36vh] min-h-[180px] overflow-y-auto rounded-xl bg-slate-50 p-3">
              {messages.length === 0 ? (
                <p className="text-sm text-slate-500">{t.emptyState}</p>
              ) : (
                <div className="space-y-2">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`max-w-[92%] rounded-2xl px-3 py-2 text-sm ${
                        message.role === "user"
                          ? "ml-auto bg-teal-600 text-white"
                          : "mr-auto bg-white text-slate-800 shadow-sm"
                      }`}
                    >
                      <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                    </div>
                  ))}
                </div>
              )}

              {loading && (
                <div className="mt-2 mr-auto inline-flex items-center gap-2 rounded-2xl bg-white px-3 py-2 text-sm text-slate-700 shadow-sm">
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-400 border-t-transparent" />
                  {t.typing}
                </div>
              )}

              {error && (
                <div className="mt-3 rounded-xl border border-rose-200 bg-rose-50 p-2.5 text-xs text-rose-700">
                  <p>{error}</p>
                  <button
                    type="button"
                    onClick={handleRetry}
                    disabled={loading || !lastFailedUserId}
                    className="mt-2 rounded-full bg-rose-600 px-3 py-1 text-xs text-white disabled:opacity-50"
                  >
                    {t.retry}
                  </button>
                </div>
              )}
              <div ref={endRef} />
            </div>

            <div className="mt-2 flex items-end gap-2">
              <textarea
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();
                    void handleSend();
                  }
                }}
                placeholder={t.placeholder}
                rows={2}
                disabled={!chatEnabled || loading}
                className="min-h-[46px] flex-1 resize-none rounded-2xl border border-teal-200 bg-white px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-teal-300 disabled:cursor-not-allowed disabled:bg-slate-100"
              />
              <button
                type="button"
                onClick={() => void handleSend()}
                disabled={!chatEnabled || loading || !query.trim()}
                className="rounded-2xl bg-teal-600 px-4 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-teal-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {t.send}
              </button>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
