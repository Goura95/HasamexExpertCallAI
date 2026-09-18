"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
  Activity,
  ArrowUpRight,
  BarChart3,
  BrainCircuit,
  CheckCircle2,
  ChevronDown,
  Clock3,
  FileSearch,
  Globe2,
  Layers3,
  MessageSquareText,
  Network,
  Search,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  Upload,
  Users,
  X,
} from "lucide-react";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

type Expert = {
  name: string;
  role: string;
  market: string;
  transcript_id: string;
};

type Evidence = {
  segment_id: string;
  expert: string;
  role: string;
  market: string;
  speaker: string;
  timestamp: string;
  quote?: string;
  text?: string;
  similarity_score?: number;
};

type GuideAnswer = {
  market: string;
  evidence: Evidence[];
};

type GuideItem = {
  id: string;
  question: string;
  answers: GuideAnswer[];
};

type Theme = {
  id: string;
  theme: string;
  description: string;
  evidence: Evidence[];
};

type Difference = {
  id?: string;
  topic: string;
  summary: string;
  evidence: Evidence[];
};

type Transcript = Evidence;

type AskResponse = {
  question: string;
  answer: string;
  evidence: Evidence[];
};

type UploadResponse = {
  message: string;
  experts: number;
  segments: number;
  searchable_expert_segments: number;
  markets: string[];
};

const marketStyles: Record<
  string,
  {
    flag: string;
    gradient: string;
    soft: string;
    border: string;
    text: string;
  }
> = {
  France: {
    flag: "🇫🇷",
    gradient:
      "from-blue-500/20 via-indigo-500/10 to-transparent",
    soft: "bg-blue-500/10",
    border: "border-blue-400/20",
    text: "text-blue-300",
  },

  Germany: {
    flag: "🇩🇪",
    gradient:
      "from-amber-500/20 via-orange-500/10 to-transparent",
    soft: "bg-amber-500/10",
    border: "border-amber-400/20",
    text: "text-amber-300",
  },

  "United Kingdom": {
    flag: "🇬🇧",
    gradient:
      "from-violet-500/20 via-purple-500/10 to-transparent",
    soft: "bg-violet-500/10",
    border: "border-violet-400/20",
    text: "text-violet-300",
  },
};

function getMarketStyle(market: string) {
  return (
    marketStyles[market] || {
      flag: "🌍",
      gradient: "from-cyan-500/20 to-transparent",
      soft: "bg-cyan-500/10",
      border: "border-cyan-400/20",
      text: "text-cyan-300",
    }
  );
}

function getEvidenceText(evidence: Evidence) {
  return evidence.quote || evidence.text || "";
}

function EvidenceCard({
  evidence,
  compact = false,
}: {
  evidence: Evidence;
  compact?: boolean;
}) {
  const style = getMarketStyle(evidence.market);

  return (
    <div
      className={`group rounded-2xl border ${style.border} bg-white/[0.035] p-4 transition-all duration-300 hover:-translate-y-0.5 hover:bg-white/[0.06]`}
    >
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span
            className={`rounded-lg ${style.soft} px-2.5 py-1 text-xs font-semibold ${style.text}`}
          >
            {style.flag} {evidence.market}
          </span>

          <span className="text-xs text-slate-500">
            •
          </span>

          <span className="text-sm font-medium text-slate-300">
            {evidence.expert}
          </span>
        </div>

        <div className="flex items-center gap-1.5 rounded-lg bg-white/5 px-2.5 py-1 text-xs font-medium text-slate-300">
          <Clock3 size={13} />
          {evidence.timestamp}
        </div>
      </div>

      {!compact && (
        <p className="mt-2 text-xs text-slate-500">
          {evidence.role}
        </p>
      )}

      <div className="mt-4 flex gap-3">
        <span
          className={`mt-0.5 shrink-0 text-lg ${style.text}`}
        >
          “
        </span>

        <p className="text-sm leading-6 text-slate-300">
          {getEvidenceText(evidence)}

          <span
            className={`ml-0.5 ${style.text}`}
          >
            ”
          </span>
        </p>
      </div>

      <div className="flex items-center gap-2 text-[11px] text-slate-600">
        <span>
          Source: {evidence.market}
        </span>

        <span>•</span>

        <span>
          {evidence.timestamp}
        </span>
      </div>
    </div>
  );
}

function MetricCard({
  icon,
  label,
  value,
  detail,
  gradient,
}: {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  detail: string;
  gradient: string;
}) {
  return (
    <div className="relative overflow-hidden rounded-3xl border border-white/10 bg-white/[0.045] p-5 backdrop-blur-xl">
      <div
        className={`absolute -right-8 -top-8 h-28 w-28 rounded-full bg-gradient-to-br ${gradient} blur-2xl`}
      />

      <div className="relative">
        <div className="mb-5 flex items-center justify-between">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/5 text-slate-300">
            {icon}
          </div>

          <span className="rounded-full bg-emerald-400/10 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-emerald-300">
            Live
          </span>
        </div>

        <div className="text-3xl font-bold tracking-tight text-white">
          {value}
        </div>

        <div className="mt-1 text-sm font-medium text-slate-300">
          {label}
        </div>

        <div className="mt-2 text-xs text-slate-500">
          {detail}
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  const [activeTab, setActiveTab] = useState("Overview");

  const [experts, setExperts] = useState<Expert[]>([]);
  const [transcripts, setTranscripts] = useState<
    Transcript[]
  >([]);
  const [guide, setGuide] = useState<GuideItem[]>([]);
  const [themes, setThemes] = useState<Theme[]>([]);
  const [differences, setDifferences] = useState<
    Difference[]
  >([]);

  const [loading, setLoading] = useState(true);

  const [selectedGuide, setSelectedGuide] = useState("q1");

  const [expandedTheme, setExpandedTheme] = useState<
    string | null
  >(null);

  const [askQuestion, setAskQuestion] = useState("");
  const [askLoading, setAskLoading] = useState(false);
  const [askResult, setAskResult] =
    useState<AskResponse | null>(null);

  const [searchText, setSearchText] = useState("");
  const [marketFilter, setMarketFilter] = useState("All");

  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [uploadError, setUploadError] = useState(false);

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  async function loadData(showLoader = false) {
    if (showLoader) {
      setLoading(true);
    }

    try {
      const [
        expertsResponse,
        transcriptsResponse,
        guideResponse,
        themesResponse,
        differencesResponse,
      ] = await Promise.all([
        fetch(`${API_BASE}/api/experts`),
        fetch(`${API_BASE}/api/transcripts`),
        fetch(`${API_BASE}/api/guide`),
        fetch(`${API_BASE}/api/themes`),
        fetch(`${API_BASE}/api/differences`),
      ]);

      if (!expertsResponse.ok) {
        throw new Error("Failed to load experts");
      }

      if (!transcriptsResponse.ok) {
        throw new Error("Failed to load transcripts");
      }

      if (!guideResponse.ok) {
        throw new Error("Failed to load guide");
      }

      if (!themesResponse.ok) {
        throw new Error("Failed to load themes");
      }

      if (!differencesResponse.ok) {
        throw new Error("Failed to load differences");
      }

      const [
        expertsData,
        transcriptsData,
        guideData,
        themesData,
        differencesData,
      ] = await Promise.all([
        expertsResponse.json(),
        transcriptsResponse.json(),
        guideResponse.json(),
        themesResponse.json(),
        differencesResponse.json(),
      ]);

      setExperts(expertsData);
      setTranscripts(transcriptsData);
      setGuide(guideData);
      setThemes(themesData);
      setDifferences(differencesData);

      if (guideData.length > 0) {
        setSelectedGuide((current) =>
          guideData.some(
            (item: GuideItem) => item.id === current
          )
            ? current
            : guideData[0].id
        );
      }
    } catch (error) {
      console.error(
        "Failed to load Hasamex data:",
        error
      );

      setUploadError(true);

      setUploadMessage(
        "Unable to load the analysis service. Make sure the FastAPI backend is running."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const timer = window.setTimeout(() => {
      loadData(true);
    }, 0);

    return () => {
      window.clearTimeout(timer);
    };
  }, []);

  async function handleUpload(
    event: React.ChangeEvent<HTMLInputElement>
  ) {
    const files = event.target.files;

    if (!files || files.length === 0) {
      return;
    }

    setUploading(true);
    setUploadMessage("");
    setUploadError(false);

    try {
      if (files.length !== 3) {
        throw new Error(
          "Please select exactly 3 transcript files."
        );
      }

      const formData = new FormData();

      Array.from(files).forEach((file) => {
        formData.append("files", file);
      });

      const response = await fetch(
        `${API_BASE}/api/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response
        .json()
        .catch(() => null);

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            data?.message ||
            "Transcript upload failed."
        );
      }

      const result = data as UploadResponse;

      setUploadMessage(
        result.message ||
          `Successfully loaded ${result.experts} expert transcripts.`
      );

      setUploadError(false);

      await loadData(false);

      setActiveTab("Overview");
      setAskResult(null);
      setSearchText("");
      setMarketFilter("All");
      setExpandedTheme(null);
    } catch (error) {
      console.error(
        "Transcript upload error:",
        error
      );

      setUploadError(true);

      setUploadMessage(
        error instanceof Error
          ? error.message
          : "Transcript upload failed."
      );
    } finally {
      setUploading(false);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  }

  const filteredTranscripts = useMemo(() => {
    return transcripts.filter((item) => {
      const matchesMarket =
        marketFilter === "All" ||
        item.market === marketFilter;

      const searchable =
        `${item.expert} ${item.market} ${getEvidenceText(
          item
        )} ${item.timestamp}`.toLowerCase();

      return (
        matchesMarket &&
        searchable.includes(searchText.toLowerCase())
      );
    });
  }, [transcripts, marketFilter, searchText]);

  async function handleAsk(questionOverride?: string) {
    const question = (
      questionOverride || askQuestion
    ).trim();

    if (!question) {
      return;
    }

    setAskLoading(true);
    setAskResult(null);

    try {
      const response = await fetch(
        `${API_BASE}/api/ask`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question,
            top_k: 6,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response
          .json()
          .catch(() => null);

        throw new Error(
          errorData?.detail || "Ask API failed"
        );
      }

      const data: AskResponse = await response.json();

      setAskResult(data);
      setAskQuestion(question);
    } catch (error) {
      console.error(error);

      setAskResult({
        question,
        answer:
          error instanceof Error
            ? error.message
            : "Unable to reach the analysis service. Please make sure the FastAPI backend is running.",
        evidence: [],
      });
    } finally {
      setAskLoading(false);
    }
  }

  const selectedGuideItem =
    guide.find((item) => item.id === selectedGuide) ||
    guide[0];

  const quickQuestions = [
    "What are the main barriers to robotic surgery adoption?",
    "How important are hospital budgets and ROI?",
    "How do purchase timelines differ across markets?",
    "What adoption trend do experts expect over the next 3–5 years?",
  ];

  const tabs = [
    {
      name: "Overview",
      icon: <BarChart3 size={17} />,
    },
    {
      name: "Interview Guide",
      icon: <Layers3 size={17} />,
    },
    {
      name: "Evidence",
      icon: <FileSearch size={17} />,
    },
    {
      name: "Themes",
      icon: <Network size={17} />,
    },
    {
      name: "Compare",
      icon: <Globe2 size={17} />,
    },
    {
      name: "Ask the Calls",
      icon: <MessageSquareText size={17} />,
    },
  ];

  const markets = Array.from(
    new Set(experts.map((expert) => expert.market))
  );

  return (
    <main className="min-h-screen overflow-x-hidden bg-[#060816] text-white">
      {/* Ambient background */}
      <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute left-[8%] top-[-10%] h-[500px] w-[500px] rounded-full bg-blue-600/15 blur-[140px]" />

        <div className="absolute right-[5%] top-[15%] h-[450px] w-[450px] rounded-full bg-violet-600/15 blur-[140px]" />

        <div className="absolute bottom-[-10%] left-[40%] h-[450px] w-[450px] rounded-full bg-cyan-500/10 blur-[140px]" />
      </div>

      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-white/10 bg-[#060816]/80 backdrop-blur-2xl">
        <div className="mx-auto flex max-w-[1500px] items-center justify-between px-5 py-4 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="relative flex h-11 w-11 items-center justify-center overflow-hidden rounded-2xl bg-gradient-to-br from-blue-500 via-violet-500 to-cyan-400 shadow-lg shadow-blue-500/20">
              <BrainCircuit size={23} />

              <div className="absolute inset-0 bg-white/10" />
            </div>

            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-bold tracking-tight">
                  ExpertCall AI
                </h1>

                <span className="rounded-full border border-blue-400/20 bg-blue-400/10 px-2 py-0.5 text-[9px] font-bold uppercase tracking-widest text-blue-300">
                  AI Intelligence
                </span>
              </div>

              <p className="hidden text-xs text-slate-500 sm:block">
                European robotic surgery market intelligence
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/5 px-3 py-1.5 text-xs text-emerald-300 sm:flex">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
              Evidence engine online
            </div>

            {/* Hidden file input */}
            <input
              ref={fileInputRef}
              type="file"
              accept=".txt,text/plain"
              multiple
              onChange={handleUpload}
              className="hidden"
            />

            {/* Upload button */}
            <button
              type="button"
              onClick={() =>
                fileInputRef.current?.click()
              }
              disabled={uploading}
              className="hidden items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-medium text-slate-300 transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-50 md:flex"
            >
              {uploading ? (
                <Activity
                  size={14}
                  className="animate-spin"
                />
              ) : (
                <Upload size={14} />
              )}

              {uploading
                ? "Processing..."
                : "Upload transcripts"}
            </button>

            {/* Mobile upload icon */}
            <button
              type="button"
              onClick={() =>
                fileInputRef.current?.click()
              }
              disabled={uploading}
              className="flex h-9 w-9 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-slate-300 transition hover:bg-white/10 disabled:opacity-50 md:hidden"
              title="Upload transcripts"
            >
              {uploading ? (
                <Activity
                  size={15}
                  className="animate-spin"
                />
              ) : (
                <Upload size={15} />
              )}
            </button>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-[1500px] px-5 py-7 lg:px-8 lg:py-9">
        {/* Upload status */}
        {uploadMessage && (
          <div
            className={`mb-5 flex items-start justify-between gap-4 rounded-2xl border p-4 ${
              uploadError
                ? "border-red-400/20 bg-red-400/5"
                : "border-emerald-400/20 bg-emerald-400/5"
            }`}
          >
            <div className="flex items-start gap-3">
              {uploadError ? (
                <X
                  size={18}
                  className="mt-0.5 shrink-0 text-red-300"
                />
              ) : (
                <CheckCircle2
                  size={18}
                  className="mt-0.5 shrink-0 text-emerald-300"
                />
              )}

              <div>
                <p
                  className={`text-sm font-medium ${
                    uploadError
                      ? "text-red-300"
                      : "text-emerald-300"
                  }`}
                >
                  {uploadMessage}
                </p>

                {!uploadError && (
                  <p className="mt-1 text-xs text-slate-500">
                    The active transcript dataset and evidence
                    engine have been refreshed.
                  </p>
                )}
              </div>
            </div>

            <button
              type="button"
              onClick={() => {
                setUploadMessage("");
                setUploadError(false);
              }}
              className="rounded-lg p-1 text-slate-500 transition hover:bg-white/5 hover:text-white"
            >
              <X size={15} />
            </button>
          </div>
        )}

        {/* Hero */}
        <section className="relative overflow-hidden rounded-[32px] border border-white/10 bg-gradient-to-br from-blue-500/[0.10] via-violet-500/[0.07] to-cyan-500/[0.06] p-7 shadow-2xl shadow-black/20 lg:p-10">
          <div className="absolute right-[-80px] top-[-100px] h-72 w-72 rounded-full bg-blue-500/10 blur-3xl" />

          <div className="absolute bottom-[-100px] left-[35%] h-72 w-72 rounded-full bg-violet-500/10 blur-3xl" />

          <div className="relative grid gap-8 lg:grid-cols-[1.5fr_1fr] lg:items-end">
            <div>
              <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-medium text-slate-300">
                <Sparkles
                  size={14}
                  className="text-cyan-300"
                />
                Evidence-grounded transcript intelligence
              </div>

              <h2 className="max-w-3xl text-4xl font-bold leading-[1.08] tracking-[-0.03em] sm:text-5xl lg:text-6xl">
                Turn expert calls into
                <span className="block bg-gradient-to-r from-blue-300 via-violet-300 to-cyan-300 bg-clip-text text-transparent">
                  decision-ready intelligence.
                </span>
              </h2>

              <p className="mt-5 max-w-2xl text-base leading-7 text-slate-400">
                Analyze three European expert interviews, surface
                recurring themes, compare market perspectives, and
                trace every insight back to its original transcript
                timestamp.
              </p>

              <div className="mt-7 flex flex-wrap gap-3">
                <button
                  type="button"
                  onClick={() =>
                    setActiveTab("Ask the Calls")
                  }
                  className="group flex items-center gap-2 rounded-xl bg-gradient-to-r from-blue-500 to-violet-500 px-5 py-3 text-sm font-semibold shadow-xl shadow-blue-500/20 transition hover:scale-[1.02]"
                >
                  <MessageSquareText size={17} />

                  Ask the Calls

                  <ArrowUpRight
                    size={16}
                    className="transition group-hover:translate-x-0.5 group-hover:-translate-y-0.5"
                  />
                </button>

                <button
                  type="button"
                  onClick={() => setActiveTab("Themes")}
                  className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-5 py-3 text-sm font-semibold text-slate-200 transition hover:bg-white/10"
                >
                  <Network size={17} />
                  Explore Themes
                </button>

                <button
                  type="button"
                  onClick={() =>
                    setActiveTab("Interview Guide")
                  }
                  className="flex items-center gap-2 rounded-xl border border-cyan-400/20 bg-cyan-400/5 px-5 py-3 text-sm font-semibold text-cyan-200 transition hover:bg-cyan-400/10"
                >
                  <Layers3 size={17} />
                  Open Interview Guide
                </button>
              </div>
            </div>

            <div className="rounded-3xl border border-white/10 bg-black/20 p-5 backdrop-blur-xl">
              <div className="mb-4 flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-widest text-slate-500">
                  Research coverage
                </span>

                <ShieldCheck
                  size={18}
                  className="text-emerald-300"
                />
              </div>

              <div className="space-y-4">
                {experts.map((expert) => {
                  const style = getMarketStyle(
                    expert.market
                  );

                  return (
                    <div
                      key={expert.transcript_id}
                      className="flex items-center justify-between"
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className={`flex h-9 w-9 items-center justify-center rounded-xl ${style.soft} text-lg`}
                        >
                          {style.flag}
                        </div>

                        <div>
                          <div className="text-sm font-semibold text-white">
                            {expert.market}
                          </div>

                          <div className="text-xs text-slate-500">
                            {expert.name}
                          </div>
                        </div>
                      </div>

                      <CheckCircle2
                        size={16}
                        className="text-emerald-300"
                      />
                    </div>
                  );
                })}
              </div>

              {experts.length === 0 && (
                <div className="rounded-xl border border-dashed border-white/10 p-5 text-center text-xs text-slate-500">
                  No transcripts loaded.
                </div>
              )}
            </div>
          </div>
        </section>

        {/* Navigation */}
        <div className="mt-7 overflow-x-auto pb-1">
          <nav className="flex min-w-max gap-1 rounded-2xl border border-white/10 bg-white/[0.035] p-1.5">
            {tabs.map((tab) => {
              const active = activeTab === tab.name;

              return (
                <button
                  type="button"
                  key={tab.name}
                  onClick={() =>
                    setActiveTab(tab.name)
                  }
                  className={`flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium transition ${
                    active
                      ? "bg-white/10 text-white shadow-lg"
                      : "text-slate-500 hover:bg-white/5 hover:text-slate-200"
                  }`}
                >
                  {tab.icon}
                  {tab.name}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Loading */}
        {loading ? (
          <div className="mt-8 rounded-3xl border border-white/10 bg-white/[0.035] p-12 text-center">
            <Activity
              className="mx-auto animate-pulse text-blue-300"
              size={30}
            />

            <p className="mt-4 text-sm text-slate-400">
              Loading expert intelligence...
            </p>
          </div>
        ) : (
          <>
            {/* Overview */}
            {activeTab === "Overview" && (
              <section className="mt-8 space-y-7">
                <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                  <MetricCard
                    icon={<Users size={20} />}
                    label="Expert Interviews"
                    value={experts.length}
                    detail="Cross-market expert perspectives"
                    gradient="from-blue-500 to-cyan-400"
                  />

                  <MetricCard
                    icon={<Globe2 size={20} />}
                    label="European Markets"
                    value={markets.length}
                    detail={
                      markets.length > 0
                        ? markets.join(" • ")
                        : "No markets loaded"
                    }
                    gradient="from-violet-500 to-fuchsia-400"
                  />

                  <MetricCard
                    icon={<FileSearch size={20} />}
                    label="Transcript Segments"
                    value={transcripts.length}
                    detail="Timestamped source evidence"
                    gradient="from-cyan-500 to-blue-400"
                  />

                  <MetricCard
                    icon={<TrendingUp size={20} />}
                    label="Key Themes"
                    value={themes.length}
                    detail="Evidence-backed patterns"
                    gradient="from-emerald-500 to-cyan-400"
                  />
                </div>

                <div className="grid gap-6 lg:grid-cols-[1.25fr_0.75fr]">
                  <div className="rounded-3xl border border-white/10 bg-white/[0.035] p-6">
                    <div className="mb-6 flex items-center justify-between">
                      <div>
                        <p className="text-xs font-bold uppercase tracking-widest text-blue-300">
                          Interview intelligence
                        </p>

                        <h3 className="mt-1 text-xl font-bold">
                          Six questions. Three market perspectives.
                        </h3>
                      </div>

                      <button
                        type="button"
                        onClick={() =>
                          setActiveTab("Interview Guide")
                        }
                        className="rounded-xl border border-white/10 bg-white/5 p-2.5 text-slate-300 hover:bg-white/10"
                      >
                        <ArrowUpRight size={17} />
                      </button>
                    </div>

                    <div className="space-y-3">
                      {guide.map((item, index) => (
                        <button
                          type="button"
                          key={item.id}
                          onClick={() => {
                            setSelectedGuide(item.id);
                            setActiveTab("Interview Guide");
                          }}
                          className="group flex w-full items-center gap-4 rounded-2xl border border-white/5 bg-black/10 p-4 text-left transition hover:border-blue-400/20 hover:bg-white/[0.045]"
                        >
                          <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500/20 to-violet-500/20 text-xs font-bold text-blue-300">
                            {String(index + 1).padStart(
                              2,
                              "0"
                            )}
                          </span>

                          <span className="flex-1 text-sm text-slate-300">
                            {item.question}
                          </span>

                          <ChevronDown
                            size={16}
                            className="-rotate-90 text-slate-600 transition group-hover:text-slate-300"
                          />
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="rounded-3xl border border-white/10 bg-gradient-to-br from-white/[0.06] to-white/[0.02] p-6">
                    <div className="flex items-center gap-2">
                      <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-400/10">
                        <ShieldCheck
                          size={19}
                          className="text-emerald-300"
                        />
                      </div>

                      <div>
                        <p className="text-sm font-semibold">
                          Evidence-first AI
                        </p>

                        <p className="text-xs text-slate-500">
                          Hallucination controls enabled
                        </p>
                      </div>
                    </div>

                    <div className="mt-7 space-y-4">
                      {[
                        "Answers grounded in retrieved transcript evidence",
                        "Exact quotes preserved from source transcripts",
                        "Original timestamps retained",
                        "Insufficient evidence returns no supporting citations",
                      ].map((item) => (
                        <div
                          key={item}
                          className="flex gap-3 text-sm leading-6 text-slate-400"
                        >
                          <CheckCircle2
                            size={16}
                            className="mt-1 shrink-0 text-emerald-300"
                          />

                          {item}
                        </div>
                      ))}
                    </div>

                    <div className="mt-7 rounded-2xl border border-blue-400/10 bg-blue-400/5 p-4">
                      <div className="flex items-center gap-2 text-xs font-semibold text-blue-300">
                        <Sparkles size={14} />
                        Architecture principle
                      </div>

                      <p className="mt-2 text-sm leading-6 text-slate-400">
                        The LLM synthesizes evidence. The transcript
                        remains the source of truth.
                      </p>
                    </div>
                  </div>
                </div>

                <div>
                  <div className="mb-4 flex items-end justify-between">
                    <div>
                      <p className="text-xs font-bold uppercase tracking-widest text-violet-300">
                        Market pulse
                      </p>

                      <h3 className="mt-1 text-xl font-bold">
                        Expert perspectives
                      </h3>
                    </div>
                  </div>

                  <div className="grid gap-4 lg:grid-cols-3">
                    {experts.map((expert) => {
                      const style = getMarketStyle(
                        expert.market
                      );

                      return (
                        <div
                          key={expert.transcript_id}
                          className={`relative overflow-hidden rounded-3xl border ${style.border} bg-gradient-to-br ${style.gradient} p-6`}
                        >
                          <div className="flex items-start justify-between">
                            <div>
                              <span className="text-3xl">
                                {style.flag}
                              </span>

                              <h4 className="mt-4 text-lg font-bold">
                                {expert.market}
                              </h4>

                              <p className="mt-1 text-sm text-slate-400">
                                {expert.name}
                              </p>
                            </div>

                            <span
                              className={`rounded-full ${style.soft} px-2.5 py-1 text-[10px] font-bold uppercase tracking-widest ${style.text}`}
                            >
                              Expert call
                            </span>
                          </div>

                          <p className="mt-6 text-sm leading-6 text-slate-400">
                            {expert.role}
                          </p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </section>
            )}

            {/* Interview Guide */}
            {activeTab === "Interview Guide" && (
              <section className="mt-8 grid gap-6 lg:grid-cols-[330px_1fr]">
                <div className="rounded-3xl border border-white/10 bg-white/[0.035] p-4">
                  <p className="px-3 py-2 text-xs font-bold uppercase tracking-widest text-slate-500">
                    Interview guide
                  </p>

                  <div className="space-y-1">
                    {guide.map((item, index) => (
                      <button
                        type="button"
                        key={item.id}
                        onClick={() =>
                          setSelectedGuide(item.id)
                        }
                        className={`w-full rounded-2xl p-4 text-left transition ${
                          selectedGuide === item.id
                            ? "bg-gradient-to-r from-blue-500/15 to-violet-500/10 text-white"
                            : "text-slate-400 hover:bg-white/5"
                        }`}
                      >
                        <div className="flex gap-3">
                          <span className="text-xs font-bold text-blue-300">
                            {String(index + 1).padStart(
                              2,
                              "0"
                            )}
                          </span>

                          <span className="text-sm leading-5">
                            {item.question}
                          </span>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                <div className="rounded-3xl border border-white/10 bg-white/[0.035] p-6">
                  {selectedGuideItem && (
                    <>
                      <div className="border-b border-white/10 pb-6">
                        <p className="text-xs font-bold uppercase tracking-widest text-blue-300">
                          Interview question
                        </p>

                        <h2 className="mt-2 text-2xl font-bold">
                          {selectedGuideItem.question}
                        </h2>
                      </div>

                      <div className="mt-6 grid gap-5 xl:grid-cols-3">
                        {selectedGuideItem.answers.map(
                          (answer) => {
                            const style = getMarketStyle(
                              answer.market
                            );

                            return (
                              <div
                                key={answer.market}
                                className={`rounded-2xl border ${style.border} bg-gradient-to-br ${style.gradient} p-5`}
                              >
                                <div className="flex items-center gap-3">
                                  <span className="text-2xl">
                                    {style.flag}
                                  </span>

                                  <div>
                                    <h3 className="font-bold">
                                      {answer.market}
                                    </h3>

                                    <p className="text-xs text-slate-500">
                                      Source evidence
                                    </p>
                                  </div>
                                </div>

                                <div className="mt-5 space-y-3">
                                  {answer.evidence.length >
                                  0 ? (
                                    answer.evidence.map(
                                      (
                                        evidence,
                                        evidenceIndex
                                      ) => (
                                        <EvidenceCard
                                          key={`${evidence.segment_id}-${evidence.timestamp}-${evidenceIndex}`}
                                          evidence={evidence}
                                          compact
                                        />
                                      )
                                    )
                                  ) : (
                                    <div className="rounded-xl border border-dashed border-white/10 p-4 text-sm text-slate-500">
                                      No direct evidence available
                                      for this question.
                                    </div>
                                  )}
                                </div>
                              </div>
                            );
                          }
                        )}
                      </div>
                    </>
                  )}

                  {!selectedGuideItem && (
                    <div className="rounded-2xl border border-dashed border-white/10 p-10 text-center text-sm text-slate-500">
                      No interview guide data available.
                    </div>
                  )}
                </div>
              </section>
            )}

            {/* Evidence */}
            {activeTab === "Evidence" && (
              <section className="mt-8">
                <div className="mb-6 rounded-3xl border border-white/10 bg-white/[0.035] p-5">
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                    <div>
                      <p className="text-xs font-bold uppercase tracking-widest text-cyan-300">
                        Source explorer
                      </p>

                      <h2 className="mt-1 text-xl font-bold">
                        Transcript evidence
                      </h2>

                      <p className="mt-1 text-xs text-slate-500">
                        Searchable source material with preserved
                        timestamps and speaker metadata.
                      </p>
                    </div>

                    <div className="flex flex-col gap-2 sm:flex-row">
                      <div className="relative">
                        <Search
                          size={16}
                          className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-600"
                        />

                        <input
                          value={searchText}
                          onChange={(event) =>
                            setSearchText(
                              event.target.value
                            )
                          }
                          placeholder="Search evidence..."
                          className="w-full rounded-xl border border-white/10 bg-black/20 py-2.5 pl-9 pr-4 text-sm text-white outline-none placeholder:text-slate-600 focus:border-blue-400/40 sm:w-64"
                        />
                      </div>

                      <select
                        value={marketFilter}
                        onChange={(event) =>
                          setMarketFilter(
                            event.target.value
                          )
                        }
                        className="rounded-xl border border-white/10 bg-[#0b1022] px-4 py-2.5 text-sm text-slate-300 outline-none"
                      >
                        <option>All</option>

                        {markets.map((market) => (
                          <option
                            key={market}
                            value={market}
                          >
                            {market}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>

                <div className="grid gap-4">
                  {filteredTranscripts
                    .filter(
                      (transcript) =>
                        transcript.speaker !== "Interviewer"
                    )
                    .map((transcript, index) => (
                      <EvidenceCard
                        key={`${transcript.segment_id || "evidence"}-${transcript.market || "market"}-${transcript.timestamp || "time"}-${index}`}
                        evidence={transcript}
                      />
                    ))}

                  {filteredTranscripts.filter(
                    (transcript) =>
                      transcript.speaker !== "Interviewer"
                  ).length === 0 && (
                    <div className="rounded-3xl border border-dashed border-white/10 p-12 text-center">
                      <Search
                        size={28}
                        className="mx-auto text-slate-600"
                      />

                      <p className="mt-4 text-sm text-slate-400">
                        No matching transcript evidence found.
                      </p>

                      <button
                        type="button"
                        onClick={() => {
                          setSearchText("");
                          setMarketFilter("All");
                        }}
                        className="mt-4 rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-xs text-slate-300 hover:bg-white/10"
                      >
                        Clear filters
                      </button>
                    </div>
                  )}
                </div>
              </section>
            )}

            {/* Themes */}
            {activeTab === "Themes" && (
              <section className="mt-8">
                <div className="mb-7">
                  <p className="text-xs font-bold uppercase tracking-widest text-violet-300">
                    Cross-transcript synthesis
                  </p>

                  <h2 className="mt-1 text-2xl font-bold">
                    What appears across the calls
                  </h2>

                  <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                    Themes are grounded in specific transcript
                    segments rather than generated as unsupported
                    summaries.
                  </p>
                </div>

                {themes.length > 0 ? (
                  <div className="grid gap-4 md:grid-cols-2">
                    {themes.map((theme, index) => {
                      const expanded =
                        expandedTheme === theme.id;

                      return (
                        <div
                          key={theme.id}
                          className="rounded-3xl border border-white/10 bg-white/[0.035] p-6 transition hover:border-violet-400/20"
                        >
                          <button
                            type="button"
                            onClick={() =>
                              setExpandedTheme(
                                expanded
                                  ? null
                                  : theme.id
                              )
                            }
                            className="w-full text-left"
                          >
                            <div className="flex items-start justify-between gap-4">
                              <div className="flex gap-4">
                                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500/20 to-violet-500/20 text-sm font-bold text-violet-300">
                                  {String(index + 1).padStart(
                                    2,
                                    "0"
                                  )}
                                </div>

                                <div>
                                  <h3 className="font-bold text-white">
                                    {theme.theme}
                                  </h3>

                                  <p className="mt-2 text-sm leading-6 text-slate-500">
                                    {theme.description}
                                  </p>
                                </div>
                              </div>

                              <ChevronDown
                                size={18}
                                className={`shrink-0 text-slate-600 transition ${
                                  expanded
                                    ? "rotate-180"
                                    : ""
                                }`}
                              />
                            </div>
                          </button>

                          {expanded && (
                            <div className="mt-5 space-y-3 border-t border-white/10 pt-5">
                              {theme.evidence.map(
                                (
                                  evidence,
                                  evidenceIndex
                                ) => (
                                  <EvidenceCard
                                    key={`${evidence.segment_id}-${evidence.timestamp}-${evidenceIndex}`}
                                    evidence={evidence}
                                    compact
                                  />
                                )
                              )}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="rounded-3xl border border-dashed border-white/10 p-12 text-center text-sm text-slate-500">
                    No themes available.
                  </div>
                )}
              </section>
            )}

            {/* Compare */}
            {activeTab === "Compare" && (
              <section className="mt-8">
                <div className="mb-7">
                  <p className="text-xs font-bold uppercase tracking-widest text-amber-300">
                    Market comparison
                  </p>

                  <h2 className="mt-1 text-2xl font-bold">
                    Different perspectives across Europe
                  </h2>

                  <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
                    The comparison highlights differences in
                    emphasis and expectations expressed by the
                    three experts.
                  </p>
                </div>

                {differences.length > 0 ? (
                  <div className="space-y-5">
                    {differences.map(
                      (difference, index) => (
                        <div
                          key={
                            difference.id ||
                            `difference-${difference.topic}-${index}`
                          }
                          className="rounded-3xl border border-white/10 bg-white/[0.035] p-6"
                        >
                          <div className="flex gap-4">
                            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-amber-500/20 to-violet-500/20 text-sm font-bold text-amber-300">
                              {String(index + 1).padStart(
                                2,
                                "0"
                              )}
                            </div>

                            <div className="flex-1">
                              <h3 className="text-lg font-bold">
                                {difference.topic}
                              </h3>

                              <p className="mt-2 max-w-4xl text-sm leading-7 text-slate-400">
                                {difference.summary}
                              </p>
                            </div>
                          </div>

                          <div className="mt-6 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                            {difference.evidence.map(
                              (
                                evidence,
                                evidenceIndex
                              ) => (
                                <EvidenceCard
                                  key={`${evidence.segment_id}-${evidence.timestamp}-${evidenceIndex}`}
                                  evidence={evidence}
                                  compact
                                />
                              )
                            )}
                          </div>
                        </div>
                      )
                    )}
                  </div>
                ) : (
                  <div className="rounded-3xl border border-dashed border-white/10 p-12 text-center text-sm text-slate-500">
                    No comparison data available.
                  </div>
                )}
              </section>
            )}

            {/* Ask the Calls */}
            {activeTab === "Ask the Calls" && (
              <section className="mt-8">
                <div className="mx-auto max-w-5xl">
                  <div className="mb-7 text-center">
                    <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500/20 via-violet-500/20 to-cyan-400/20">
                      <Sparkles
                        size={26}
                        className="text-blue-300"
                      />
                    </div>

                    <p className="mt-5 text-xs font-bold uppercase tracking-widest text-blue-300">
                      Cross-transcript intelligence
                    </p>

                    <h2 className="mt-2 text-3xl font-bold">
                      Ask the expert calls
                    </h2>

                    <p className="mx-auto mt-3 max-w-2xl text-sm leading-6 text-slate-500">
                      Ask a question across all three interviews.
                      Answers are generated from retrieved transcript
                      evidence.
                    </p>
                  </div>

                  <div className="rounded-[28px] border border-white/10 bg-gradient-to-br from-white/[0.06] to-white/[0.025] p-4 shadow-2xl shadow-blue-900/10">
                    <div className="flex gap-3">
                      <textarea
                        value={askQuestion}
                        onChange={(event) =>
                          setAskQuestion(
                            event.target.value
                          )
                        }
                        onKeyDown={(event) => {
                          if (
                            event.key === "Enter" &&
                            !event.shiftKey
                          ) {
                            event.preventDefault();
                            handleAsk();
                          }
                        }}
                        placeholder="Ask something about the three expert interviews..."
                        rows={3}
                        className="min-h-[100px] flex-1 resize-none bg-transparent px-2 py-2 text-sm leading-6 text-white outline-none placeholder:text-slate-600"
                      />

                      <button
                        type="button"
                        onClick={() => handleAsk()}
                        disabled={
                          askLoading ||
                          !askQuestion.trim()
                        }
                        className="self-end rounded-2xl bg-gradient-to-r from-blue-500 to-violet-500 p-3.5 shadow-lg shadow-blue-500/20 transition hover:scale-[1.03] disabled:cursor-not-allowed disabled:opacity-40"
                      >
                        {askLoading ? (
                          <Activity
                            size={19}
                            className="animate-spin"
                          />
                        ) : (
                          <ArrowUpRight size={19} />
                        )}
                      </button>
                    </div>
                  </div>

                  <div className="mt-5 flex flex-wrap justify-center gap-2">
                    {quickQuestions.map(
                      (question) => (
                        <button
                          type="button"
                          key={question}
                          onClick={() =>
                            handleAsk(question)
                          }
                          className="rounded-full border border-white/10 bg-white/[0.035] px-3.5 py-2 text-xs text-slate-400 transition hover:border-blue-400/20 hover:bg-blue-400/5 hover:text-slate-200"
                        >
                          {question}
                        </button>
                      )
                    )}
                  </div>

                  {askResult && (
                    <div className="mt-8 space-y-5">
                      <div className="rounded-3xl border border-blue-400/15 bg-gradient-to-br from-blue-500/[0.08] to-violet-500/[0.04] p-6">
                        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-blue-300">
                          <BrainCircuit size={15} />
                          AI synthesis
                        </div>

                        <div className="mt-5 whitespace-pre-wrap text-sm leading-7 text-slate-300">
                          {askResult.answer}
                        </div>
                      </div>

                      <div className="rounded-3xl border border-white/10 bg-white/[0.035] p-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="flex items-center gap-2">
                              <ShieldCheck
                                size={17}
                                className="text-emerald-300"
                              />

                              <h3 className="font-bold">
                                Evidence trace
                              </h3>
                            </div>

                            <p className="mt-1 text-xs text-slate-500">
                              Source material used to ground the
                              response
                            </p>
                          </div>

                          <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-slate-500">
                            {askResult.evidence.length}{" "}
                            sources
                          </span>
                        </div>

                        {askResult.evidence.length > 0 ? (
                          <div className="mt-5 grid gap-3">
                            {askResult.evidence.map(
                              (
                                evidence,
                                evidenceIndex
                              ) => (
                                <EvidenceCard
                                  key={`${evidence.segment_id}-${evidence.timestamp}-${evidenceIndex}`}
                                  evidence={evidence}
                                />
                              )
                            )}
                          </div>
                        ) : (
                          <div className="mt-5 rounded-2xl border border-dashed border-emerald-400/20 bg-emerald-400/[0.03] p-7 text-center">
                            <ShieldCheck
                              size={25}
                              className="mx-auto text-emerald-300"
                            />

                            <p className="mt-3 text-sm font-semibold text-slate-300">
                              No supporting evidence found
                            </p>

                            <p className="mt-1 text-xs text-slate-500">
                              The system did not expose related
                              retrieval results as evidence.
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </section>
            )}
          </>
        )}

        {/* Footer */}
        <footer className="mt-12 border-t border-white/10 py-7">
          <div className="flex flex-col gap-3 text-xs text-slate-600 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-2">
              <ShieldCheck size={14} />
              Evidence-grounded AI • Transcript source of truth
            </div>

            <div>
              Hasamex Technical Case Study • ExpertCall AI
            </div>
          </div>
        </footer>
      </div>
    </main>
  );
}