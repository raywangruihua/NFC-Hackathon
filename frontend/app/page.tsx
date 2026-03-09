"use client";

import { useEffect, useRef, useState, type CSSProperties, type ChangeEvent } from "react";
import {
  Bell,
  Bot,
  ChartCandlestick,
  Earth,
  Newspaper,
  Thermometer,
} from "lucide-react";
import styles from "./page.module.css";

type SeriesCard = {
  name: string;
  value: string;
  change: string;
  points: number[];
  xLabels?: string[];
  tone: "up" | "down";
  type: "stock" | "macro";
};

type MacroSeriesCard = SeriesCard & {
  indicatorKey: string;
};

type MarketSeriesCard = SeriesCard & {
  marketKey: string;
};

type FredCategoryOption = {
  key: string;
  label: string;
};

type FredIndicatorOption = {
  key: string;
  label: string;
  series_id: string;
};

type FredCategoriesResponse = {
  country: string;
  categories: FredCategoryOption[];
};

type FredIndicatorsResponse = {
  category: string;
  indicators: FredIndicatorOption[];
};

type FredSeriesResponse = {
  category: string | null;
  indicator: string;
  indicator_label: string;
  series_id: string | null;
  observations: Array<{ date: string; value: number }>;
  points: number[];
  latest: { date: string; value: number } | null;
  previous: { date: string; value: number } | null;
  change: {
    absolute: number;
    percent: number;
  };
};

type NewsArticle = {
  id: string;
  title: string;
  description: string;
};

type NewsResponse = {
  articles: NewsArticle[];
};

type MarketFunction =
  | "TIME_SERIES_INTRADAY"
  | "TIME_SERIES_DAILY"
  | "TIME_SERIES_DAILY_ADJUSTED"
  | "TIME_SERIES_WEEKLY"
  | "TIME_SERIES_WEEKLY_ADJUSTED"
  | "TIME_SERIES_MONTHLY"
  | "TIME_SERIES_MONTHLY_ADJUSTED";

type SymbolSearchMatch = {
  symbol: string;
  name: string;
  type: string | null;
  region: string | null;
  market_open: string | null;
  market_close: string | null;
  timezone: string | null;
  currency: string | null;
};

type SymbolSearchResponse = {
  keywords: string;
  matches: SymbolSearchMatch[];
  count: number;
};

type TimelineEvent = {
  date: string;
  title: string;
  text: string;
  source: string;
  impact: "High" | "Medium" | "Low";
};

type HeatCell = {
  topic: string;
  score: number;
};

type ChatMessage = {
  role: "user" | "assistant";
  text: string;
};

type AlertRule = {
  name: string;
  threshold: string;
  status: "Breached" | "Watching";
  detail: string;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_BASE_URL
const MAX_MACRO_GRAPHS = 8;
const MAX_MARKET_GRAPHS = 8;
const NEWS_ROTATE_MS = 6000;

const MARKET_FUNCTION_OPTIONS: Array<{ value: MarketFunction; label: string }> = [
  { value: "TIME_SERIES_INTRADAY", label: "Intraday" },
  { value: "TIME_SERIES_DAILY", label: "Daily" },
  { value: "TIME_SERIES_DAILY_ADJUSTED", label: "Daily Adjusted" },
  { value: "TIME_SERIES_WEEKLY", label: "Weekly" },
  { value: "TIME_SERIES_WEEKLY_ADJUSTED", label: "Weekly Adjusted" },
  { value: "TIME_SERIES_MONTHLY", label: "Monthly" },
  { value: "TIME_SERIES_MONTHLY_ADJUSTED", label: "Monthly Adjusted" },
];

const MARKET_ENDPOINTS: Record<MarketFunction, string> = {
  TIME_SERIES_INTRADAY: "/api/market/time-series/intraday",
  TIME_SERIES_DAILY: "/api/market/time-series/daily",
  TIME_SERIES_DAILY_ADJUSTED: "/api/market/time-series/daily-adjusted",
  TIME_SERIES_WEEKLY: "/api/market/time-series/weekly",
  TIME_SERIES_WEEKLY_ADJUSTED: "/api/market/time-series/weekly-adjusted",
  TIME_SERIES_MONTHLY: "/api/market/time-series/monthly",
  TIME_SERIES_MONTHLY_ADJUSTED: "/api/market/time-series/monthly-adjusted",
};

// Placeholder timeline data
const timelineEvents: TimelineEvent[] = [
  {
    date: "2026-02-27",
    title: "Fed signals caution on rate cuts",
    text: "Policymakers highlighted sticky services inflation and signaled they need more data before easing policy.",
    source: "FOMC Minutes",
    impact: "High",
  },
  {
    date: "2026-02-21",
    title: "Core inflation prints below estimate",
    text: "Core CPI slowed month-over-month as goods disinflation continued, reducing near-term tightening risk.",
    source: "BLS Release",
    impact: "High",
  },
  {
    date: "2026-02-15",
    title: "Manufacturing PMI re-enters expansion",
    text: "PMI moved back above 50 on stronger new orders, suggesting a rebound in industrial momentum.",
    source: "ISM",
    impact: "Medium",
  },
  {
    date: "2026-02-08",
    title: "Services inflation shows renewed pressure",
    text: "Shelter and wage-sensitive categories remained firm, increasing risk that disinflation progress stalls.",
    source: "NFP Report",
    impact: "Medium",
  },
];

// Placeholder theme heat data
const heatCells: HeatCell[] = [
  { topic: "Rate Cuts", score: 4 },
  { topic: "AI Capex", score: 10 },
  { topic: "Energy Shock", score: 20 },
  { topic: "Fiscal Risk", score: 30 },
  { topic: "China Demand", score: 40 },
  { topic: "Supply Chain", score: 50 },
  { topic: "Bank Stress", score: 60 },
  { topic: "Housing", score: 70 },
  { topic: "USD Strength", score: 9110 },
];

// Placeholder chatbot example 
const chatMessages: ChatMessage[] = [
  {
    role: "user",
    text: "What macro themes are driving tech underperformance this week?",
  },
  {
    role: "assistant",
    text: "Primary drivers are higher real yields and concerns about forward earnings multiples.",
  },
];

// Placeholder chain of thought reasoning by chatbot
const chatReasoning = [
  "Step 1: Pull latest yield curve and inflation surprise data.",
  "Step 2: Compare factor exposure for mega-cap tech vs broad market.",
  "Step 3: Rank themes by impact score and confidence.",
];

// Placeholder sources cited by chatbot when thinking
const chatSources = [
  "FRED: 10Y Real Yield",
  "BLS CPI Release",
  "SEC Filings: Selected tech names",
];

// Placeholder alerts
const alertRules: AlertRule[] = [
  {
    name: "Portfolio VaR",
    threshold: "1D VaR > 3.0%",
    status: "Breached",
    detail: "Current 1D VaR: 3.4%",
  },
  {
    name: "Energy Theme Heat",
    threshold: "Heat score > 65",
    status: "Breached",
    detail: "Current heat score: 69",
  },
  {
    name: "USD Momentum",
    threshold: "DXY weekly move > 1.2%",
    status: "Watching",
    detail: "Current weekly move: 0.8%",
  },
];

function formatXAxisDateLabel(rawDate: string) {
  const parsed = new Date(`${rawDate}T00:00:00`);
  if (Number.isNaN(parsed.getTime())) return rawDate;
  return Intl.DateTimeFormat("en-US", { month: "short", year: "2-digit" }).format(parsed);
}

function Sparkline({
  points,
  tone,
  xLabels,
}: {
  points: number[];
  tone: "up" | "down";
  xLabels?: string[];
}) {
  const width = 360;
  const height = 170;
  const padLeft = 58;
  const padRight = 16;
  const padTop = 14;
  const padBottom = 28;
  const plotWidth = width - padLeft - padRight;
  const plotHeight = height - padTop - padBottom;
  const max = Math.max(...points);
  const min = Math.min(...points);
  const spread = Math.max(max - min, 1);
  const mid = min + spread / 2;

  const path = points
    .map((point, i) => {
      const x =
        padLeft +
        (points.length > 1 ? (i / (points.length - 1)) * plotWidth : plotWidth / 2);
      const y = padTop + (1 - (point - min) / spread) * plotHeight;
      return `${i === 0 ? "M" : "L"} ${x} ${y}`;
    })
    .join(" ");

  const yTicks = [
    { value: max, y: padTop },
    { value: mid, y: padTop + plotHeight / 2 },
    { value: min, y: padTop + plotHeight },
  ];

  const hasDateLabels = Array.isArray(xLabels) && xLabels.length === points.length;
  const midpointIndex = Math.floor((points.length - 1) / 2);
  const xTicks = [
    {
      label: hasDateLabels ? formatXAxisDateLabel(xLabels[0]) : "T1",
      x: padLeft,
    },
    {
      label: hasDateLabels
        ? formatXAxisDateLabel(xLabels[midpointIndex])
        : `T${Math.ceil(points.length / 2)}`,
      x: padLeft + plotWidth / 2,
    },
    {
      label: hasDateLabels ? formatXAxisDateLabel(xLabels[points.length - 1]) : `T${points.length}`,
      x: padLeft + plotWidth,
    },
  ];

  const formatAxisValue = (value: number) =>
    Intl.NumberFormat("en-US", {
      notation: "compact",
      maximumFractionDigits: 1,
    }).format(value);

  return (
    <svg
      className={`${styles.sparkline} ${tone === "up" ? styles.sparklineUp : styles.sparklineDown}`}
      viewBox={`0 0 ${width} ${height}`}
      preserveAspectRatio="none"
      aria-hidden
    >
      {yTicks.map((tick) => (
        <line
          key={`grid-${tick.value}-${tick.y}`}
          className={styles.sparklineGrid}
          x1={padLeft}
          y1={tick.y}
          x2={width - padRight}
          y2={tick.y}
        />
      ))}
      <line
        className={styles.sparklineAxis}
        x1={padLeft}
        y1={padTop}
        x2={padLeft}
        y2={height - padBottom}
      />
      <line
        className={styles.sparklineAxis}
        x1={padLeft}
        y1={height - padBottom}
        x2={width - padRight}
        y2={height - padBottom}
      />

      <path className={styles.sparklinePath} d={path} />

      {yTicks.map((tick) => (
        <g key={`ytick-${tick.value}-${tick.y}`}>
          <line
            className={styles.sparklineTick}
            x1={padLeft - 3}
            y1={tick.y}
            x2={padLeft}
            y2={tick.y}
          />
          <text className={styles.sparklineLabel} x={padLeft - 6} y={tick.y + 3} textAnchor="end">
            {formatAxisValue(tick.value)}
          </text>
        </g>
      ))}

      {xTicks.map((tick) => (
        <g key={`xtick-${tick.label}-${tick.x}`}>
          <line
            className={styles.sparklineTick}
            x1={tick.x}
            y1={height - padBottom}
            x2={tick.x}
            y2={height - padBottom + 3}
          />
          <text
            className={styles.sparklineLabel}
            x={tick.x}
            y={height - 2}
            textAnchor="middle"
          >
            {tick.label}
          </text>
        </g>
      ))}
    </svg>
  );
}


function heatToneStyle(score: number): CSSProperties {
  /**
   * Fixed 10-step heat scale:
   * low values -> green, mid values -> yellow/orange, high values -> red.
   */
  const clamped = Math.max(0, Math.min(score, 99));
  const palette = [
    "#1a9850",
    "#4db15e",
    "#7acb68",
    "#a5da70",
    "#d0e878",
    "#f4f491",
    "#f7d26a",
    "#f9b05a",
    "#ef7e4a",
    "#d73027",
  ];
  const bucketIndex = Math.floor(clamped / palette.length);
  const fill = palette[bucketIndex];
  const textColor = bucketIndex <= 1 || bucketIndex >= 8 ? "#f5f5f5" : "#111111";

  return {
    backgroundColor: fill,
    borderColor: fill,
    color: textColor,
  };
}

function alertToneClass(status: AlertRule["status"]) {
  return status === "Breached" ? styles.alertBreached : styles.alertWatching;
}

function impactToneClass(impact: TimelineEvent["impact"]) {
  if (impact === "High") return styles.impactHigh;
  if (impact === "Medium") return styles.impactMedium;
  return styles.impactLow;
}

function toLabel(value: string) {
  const tokenMap: Record<string, string> = {
    fx: "FX",
    usd: "USD",
    eur: "EUR",
    jpy: "JPY",
    gdp: "GDP",
    cpi: "CPI",
    pce: "PCE",
    ppi: "PPI",
    pmi: "PMI",
    fed: "Fed",
    sofr: "SOFR",
    ust: "UST",
    ig: "IG",
    hy: "HY",
    oas: "OAS",
    ted: "TED",
    nfci: "NFCI",
    stlfsi: "STLFSI",
    m2: "M2",
    u6: "U6",
    wti: "WTI",
    yoy: "YoY",
    mom: "MoM",
  };

  return value
    .split("_")
    .map((token) => {
      const lowered = token.toLowerCase();
      if (tokenMap[lowered]) return tokenMap[lowered];

      if (/^\d+[a-z]+$/i.test(token)) {
        const prefix = token.replace(/[A-Za-z]/g, "");
        const suffix = token.replace(/\d/g, "").toUpperCase();
        return `${prefix}${suffix}`;
      }

      return lowered.charAt(0).toUpperCase() + lowered.slice(1);
    })
    .join(" ");
}

function formatMetricValue(value: number | null) {
  if (value === null || Number.isNaN(value)) return "N/A";
  if (Math.abs(value) >= 1000) {
    return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
  }
  return value.toFixed(2);
}

function formatPercentChange(value: number) {
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

function normalizeSeries(observations: Array<{ date: string; value: number }>) {
  const validRows = observations.filter((row) => Number.isFinite(row.value));
  if (validRows.length > 1) {
    return {
      points: validRows.map((row) => row.value),
      xLabels: validRows.map((row) => row.date),
    };
  }
  if (validRows.length === 1) {
    return {
      points: [validRows[0].value, validRows[0].value],
      xLabels: [validRows[0].date, validRows[0].date],
    };
  }
  return {
    points: [0, 0],
    xLabels: ["N/A", "N/A"],
  };
}

function toRecentMonthOptions(count = 12) {
  return Array.from({ length: count }, (_, index) => {
    const date = new Date();
    date.setMonth(date.getMonth() - index);
    const month = String(date.getMonth() + 1).padStart(2, "0");
    return `${date.getFullYear()}-${month}`;
  });
}

function extractAlphaClose(row: Record<string, string>) {
  const preferred = ["5. adjusted close", "4. close"];
  for (const key of preferred) {
    const value = row[key];
    if (!value) continue;
    const parsed = Number.parseFloat(value);
    if (Number.isFinite(parsed)) return parsed;
  }

  for (const [key, value] of Object.entries(row)) {
    if (!key.toLowerCase().includes("close")) continue;
    const parsed = Number.parseFloat(value);
    if (Number.isFinite(parsed)) return parsed;
  }

  return null;
}

function parseAlphaSeries(raw: Record<string, unknown>) {
  const seriesEntry = Object.entries(raw).find(
    ([key, value]) =>
      key.toLowerCase().includes("time series") &&
      typeof value === "object" &&
      value !== null &&
      !Array.isArray(value)
  );

  if (!seriesEntry) {
    throw new Error("No time series data found for the selected options.");
  }

  const rows = seriesEntry[1] as Record<string, Record<string, string>>;
  const normalizedRows = Object.entries(rows)
    .map(([date, row]) => {
      if (!row || typeof row !== "object") return null;
      const closeValue = extractAlphaClose(row);
      if (closeValue === null) return null;
      return { date, value: closeValue };
    })
    .filter((row): row is { date: string; value: number } => row !== null)
    .sort((left, right) => left.date.localeCompare(right.date));

  const latest = normalizedRows.length > 0 ? normalizedRows[normalizedRows.length - 1] : null;
  const previous = normalizedRows.length > 1 ? normalizedRows[normalizedRows.length - 2] : null;
  const normalizedSeries = normalizeSeries(normalizedRows);

  return {
    normalizedSeries,
    latest,
    previous,
  };
}

function extractAlphaMetaSymbol(raw: Record<string, unknown>) {
  const meta = raw["Meta Data"];
  if (!meta || typeof meta !== "object" || Array.isArray(meta)) return null;
  const symbol = (meta as Record<string, unknown>)["2. Symbol"];
  return typeof symbol === "string" && symbol ? symbol : null;
}

export default function Home() {
  const recentMonthOptions = toRecentMonthOptions(18);
  const [marketSymbolInput, setMarketSymbolInput] = useState("");
  const [marketSymbolMatches, setMarketSymbolMatches] = useState<SymbolSearchMatch[]>([]);
  const [showMarketMatches, setShowMarketMatches] = useState(false);
  const [marketFunction, setMarketFunction] = useState<MarketFunction>("TIME_SERIES_INTRADAY");
  const [marketInterval, setMarketInterval] = useState<"1min" | "5min" | "15min" | "30min" | "60min">("5min");
  const [marketAdjusted, setMarketAdjusted] = useState<"default" | "true" | "false">("default");
  const [marketExtendedHours, setMarketExtendedHours] = useState<"default" | "true" | "false">("default");
  const [marketMonth, setMarketMonth] = useState("");
  const [marketEntitlement, setMarketEntitlement] = useState<"default" | "realtime" | "delayed">("default");
  const [marketCards, setMarketCards] = useState<MarketSeriesCard[]>([]);
  const [marketLoading, setMarketLoading] = useState(false);
  const [marketError, setMarketError] = useState<string | null>(null);
  const [marketSymbolLoading, setMarketSymbolLoading] = useState(false);
  const [selectedCountry, setSelectedCountry] = useState("USA");
  const [categories, setCategories] = useState<FredCategoryOption[]>([]);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [indicators, setIndicators] = useState<FredIndicatorOption[]>([]);
  const [selectedIndicator, setSelectedIndicator] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [macroCards, setMacroCards] = useState<MacroSeriesCard[]>([]);
  const [macroLoading, setMacroLoading] = useState(false);
  const [macroError, setMacroError] = useState<string | null>(null);
  const [newsArticles, setNewsArticles] = useState<NewsArticle[]>([]);
  const [newsLoading, setNewsLoading] = useState(false);
  const [newsError, setNewsError] = useState<string | null>(null);
  const [activeNewsIndex, setActiveNewsIndex] = useState(0);
  const newsViewportRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    async function loadNews() {
      setNewsLoading(true);
      setNewsError(null);

      try {
        const response = await fetch(`${API_BASE_URL}/api/news`, {
          signal: controller.signal,
        });
        if (!response.ok) {
          throw new Error("Failed to load news.");
        }

        const data = (await response.json()) as NewsResponse;
        const nextArticles = data.articles ?? [];
        setNewsArticles(nextArticles);
        setActiveNewsIndex(0);
      } catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") return;
        setNewsArticles([]);
        setNewsError("Unable to load news.");
      } finally {
        setNewsLoading(false);
      }
    }

    void loadNews();
    return () => controller.abort();
  }, []);

  useEffect(() => {
    if (newsArticles.length < 2) return;

    const intervalId = window.setInterval(() => {
      setActiveNewsIndex((current) => {
        const nextIndex = (current + 1) % newsArticles.length;
        const viewport = newsViewportRef.current;
        if (viewport) {
          const cardHeight = viewport.clientHeight;
          viewport.scrollTo({
            top: nextIndex * cardHeight,
            behavior: "smooth",
          });
        }
        return nextIndex;
      });
    }, NEWS_ROTATE_MS);

    return () => window.clearInterval(intervalId);
  }, [newsArticles]);

  useEffect(() => {
    const viewport = newsViewportRef.current;
    if (!viewport) return;
    viewport.scrollTop = 0;
  }, [newsArticles]);

  useEffect(() => {
    const keyword = marketSymbolInput.trim();
    if (keyword.length < 1) {
      setMarketSymbolMatches([]);
      setShowMarketMatches(false);
      return;
    }

    const controller = new AbortController();
    const timeoutId = window.setTimeout(async () => {
      setMarketSymbolLoading(true);
      try {
        const response = await fetch(
          `${API_BASE_URL}/api/market/symbol-search?keywords=${encodeURIComponent(keyword)}&limit=8`,
          { signal: controller.signal }
        );
        if (!response.ok) {
          throw new Error("Failed to load symbol matches.");
        }

        const data = (await response.json()) as SymbolSearchResponse;
        const nextMatches = data.matches ?? [];
        setMarketSymbolMatches(nextMatches);
        setShowMarketMatches((current) => current && nextMatches.length > 0);
      } catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") return;
        setMarketSymbolMatches([]);
        setShowMarketMatches(false);
      } finally {
        setMarketSymbolLoading(false);
      }
    }, 280);

    return () => {
      controller.abort();
      window.clearTimeout(timeoutId);
    };
  }, [marketSymbolInput]);

  // Country selection drop down menu
  useEffect(() => {
    const controller = new AbortController();

    async function loadCategories() {
      setMacroLoading(true);
      setMacroError(null);
      try {
        const response = await fetch(
          `${API_BASE_URL}/api/macroeconomic/categories?country=${encodeURIComponent(
            selectedCountry.toLowerCase()
          )}`,
          { signal: controller.signal }
        );
        if (!response.ok) {
          throw new Error("Failed to load categories.");
        }

        const data = (await response.json()) as FredCategoriesResponse;
        const nextCategories = data.categories ?? [];
        setCategories(nextCategories);
        setSelectedCategory((current) => {
          if (nextCategories.some((option) => option.key === current)) {
            return current;
          }
          return nextCategories[0]?.key ?? "";
        });
      } catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") return;
        setCategories([]);
        setSelectedCategory("");
        setMacroError("Unable to load FRED categories.");
      } finally {
        setMacroLoading(false);
      }
    }

    void loadCategories();
    return () => controller.abort();
  }, [selectedCountry]);

  // Category selection drop down menu
  useEffect(() => {
    if (!selectedCategory) {
      setIndicators([]);
      setSelectedIndicator("");
      return;
    }

    const controller = new AbortController();

    async function loadIndicators() {
      setMacroLoading(true);
      setMacroError(null);
      try {
        const response = await fetch(
          `${API_BASE_URL}/api/macroeconomic/indicators?category=${encodeURIComponent(selectedCategory)}`,
          { signal: controller.signal }
        );
        if (!response.ok) {
          throw new Error("Failed to load indicators.");
        }

        const data = (await response.json()) as FredIndicatorsResponse;
        setIndicators(data.indicators ?? []);
      } catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") return;
        setIndicators([]);
        setMacroError("Unable to load indicators for this category.");
      } finally {
        setMacroLoading(false);
      }
    }

    void loadIndicators();
    return () => controller.abort();
  }, [selectedCategory]);

  // Indicator selection drop down menu
  const handleIndicatorSelect = (event: ChangeEvent<HTMLSelectElement>) => {
    setSelectedIndicator(event.target.value);
  };

  const handleSearchClick = async () => {
    if (!selectedIndicator || !selectedCategory) return;
    if (startDate && endDate && startDate > endDate) {
      setMacroError("Start date must be earlier than or equal to end date.");
      return;
    }

    setMacroLoading(true);
    setMacroError(null);

    try {
      const query = new URLSearchParams({
        category: selectedCategory,
        indicator: selectedIndicator,
        limit: "120",
      });
      if (startDate) query.set("start_date", startDate);
      if (endDate) query.set("end_date", endDate);

      const response = await fetch(
        `${API_BASE_URL}/api/macroeconomic/series?${query.toString()}`
      );
      if (!response.ok) {
        throw new Error("Failed to load series data.");
      }

      const data = (await response.json()) as FredSeriesResponse;
      const changePercent = data.change?.percent ?? 0;
      const normalizedSeries = normalizeSeries(data.observations ?? []);
      const nextCard: MacroSeriesCard = {
        indicatorKey: selectedIndicator,
        name: data.indicator_label || toLabel(selectedIndicator),
        value: formatMetricValue(data.latest?.value ?? null),
        change: formatPercentChange(changePercent),
        points: normalizedSeries.points,
        xLabels: normalizedSeries.xLabels,
        tone: changePercent >= 0 ? "up" : "down",
        type: "macro",
      };

      setMacroCards((previous) => {
        const withoutCurrent = previous.filter((card) => card.indicatorKey !== selectedIndicator);
        const nextCards = [...withoutCurrent, nextCard];
        if (nextCards.length <= MAX_MACRO_GRAPHS) return nextCards;
        return nextCards.slice(nextCards.length - MAX_MACRO_GRAPHS);
      });
    } catch {
      setMacroError("Unable to load series data for the selected indicator.");
    } finally {
      setMacroLoading(false);
    }
  };

  const handleMarketSymbolSelect = (match: SymbolSearchMatch) => {
    setMarketSymbolInput(match.symbol);
    setShowMarketMatches(false);
  };

  const handleMarketSearchClick = async () => {
    const symbol = marketSymbolInput.trim().toUpperCase();
    if (!symbol) {
      setMarketError("Please select or enter a symbol.");
      return;
    }

    setMarketLoading(true);
    setMarketError(null);

    try {
      const endpoint = MARKET_ENDPOINTS[marketFunction];
      const query = new URLSearchParams({ symbol });

      if (marketFunction === "TIME_SERIES_INTRADAY") {
        query.set("interval", marketInterval);
        if (marketAdjusted !== "default") query.set("adjusted", marketAdjusted);
        if (marketExtendedHours !== "default") query.set("extended_hours", marketExtendedHours);
        if (marketMonth) query.set("month", marketMonth);
        if (marketEntitlement !== "default") query.set("entitlement", marketEntitlement);
      } else if (
        marketFunction === "TIME_SERIES_DAILY" ||
        marketFunction === "TIME_SERIES_DAILY_ADJUSTED"
      ) {
        if (marketEntitlement !== "default") query.set("entitlement", marketEntitlement);
      }

      const response = await fetch(`${API_BASE_URL}${endpoint}?${query.toString()}`);
      if (!response.ok) {
        throw new Error("Failed to load market time series.");
      }

      const data = (await response.json()) as Record<string, unknown>;
      if (typeof data.error === "string") {
        throw new Error(data.error);
      }

      const { normalizedSeries, latest, previous } = parseAlphaSeries(data);
      const latestValue = latest?.value ?? null;
      const previousValue = previous?.value ?? null;
      const changePercent =
        latestValue !== null && previousValue !== null && previousValue !== 0
          ? ((latestValue - previousValue) / previousValue) * 100
          : 0;

      const resolvedSymbol = extractAlphaMetaSymbol(data) ?? symbol;
      const key = [
        resolvedSymbol,
        marketFunction,
        marketInterval,
        marketAdjusted,
        marketExtendedHours,
        marketMonth,
        marketEntitlement,
      ].join("|");
      const functionLabel =
        MARKET_FUNCTION_OPTIONS.find((option) => option.value === marketFunction)?.label ??
        marketFunction;

      const nextCard: MarketSeriesCard = {
        marketKey: key,
        name: `${resolvedSymbol} · ${functionLabel}`,
        value: formatMetricValue(latestValue),
        change: formatPercentChange(changePercent),
        points: normalizedSeries.points,
        xLabels: normalizedSeries.xLabels,
        tone: changePercent >= 0 ? "up" : "down",
        type: "stock",
      };

      setMarketCards((previousCards) => {
        const withoutCurrent = previousCards.filter((card) => card.marketKey !== key);
        const nextCards = [...withoutCurrent, nextCard];
        if (nextCards.length <= MAX_MARKET_GRAPHS) return nextCards;
        return nextCards.slice(nextCards.length - MAX_MARKET_GRAPHS);
      });
      setShowMarketMatches(false);
    } catch (error) {
      if (error instanceof Error) {
        setMarketError(error.message || "Unable to load market time series.");
      } else {
        setMarketError("Unable to load market time series.");
      }
    } finally {
      setMarketLoading(false);
    }
  };

  const handleNewsScroll = () => {
    const viewport = newsViewportRef.current;
    if (!viewport) return;
    const cardHeight = viewport.clientHeight || 1;
    const nextIndex = Math.round(viewport.scrollTop / cardHeight);
    const boundedIndex = Math.max(0, Math.min(newsArticles.length - 1, nextIndex));
    if (boundedIndex !== activeNewsIndex) {
      setActiveNewsIndex(boundedIndex);
    }
  };

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className={styles.headerInner}>
          <p className={styles.brand}>DAMMIT MACROECONOMIC TRACKER</p>
        </div>
      </header>

      <main className={styles.mainGrid}>
        <aside className={styles.sidebar}>
          <p className={styles.sidebarTitle}>Features</p>
          <ul className={styles.moduleList}>
            <li>
              <a href="#today-market" className={`${styles.moduleItem} ${styles.moduleLink}`}>
                <ChartCandlestick className={styles.moduleIcon} aria-hidden />
                <span>Market</span>
              </a>
            </li>
            <li>
              <a href="#macro-indicators" className={`${styles.moduleItem} ${styles.moduleLink}`}>
                <Earth className={styles.moduleIcon} aria-hidden />
                <span>Macro Indicators</span>
              </a>
            </li>
            <li>
              <a href="#timelines" className={`${styles.moduleItem} ${styles.moduleLink}`}>
                <Newspaper className={styles.moduleIcon} aria-hidden />
                <span>Timelines</span>
              </a>
            </li>
            <li>
              <a href="#theme-heat" className={`${styles.moduleItem} ${styles.moduleLink}`}>
                <Thermometer className={styles.moduleIcon} aria-hidden />
                <span>Theme Heat</span>
              </a>
            </li>
            <li>
              <a href="#ai-assistant" className={`${styles.moduleItem} ${styles.moduleLink}`}>
                <Bot className={styles.moduleIcon} aria-hidden />
                <span>AI Assistant</span>
              </a>
            </li>
            <li>
              <a href="#notifications" className={`${styles.moduleItem} ${styles.moduleLink}`}>
                <Bell className={styles.moduleIcon} aria-hidden />
                <span>Alerts</span>
              </a>
            </li>
          </ul>
        </aside>

        <section className={styles.contentGrid}>
          <div className={styles.stack}>
            <section id="today-market" className={styles.panel}>
              <div className={styles.panelHead}>
                <h2 className={styles.featureTitle}>Today&apos;s Market</h2>
              </div>

              <div className={styles.macroFilterRow}>
                <label className={styles.macroFilterField}>
                  <span className={styles.macroFilterLabel}>Symbol</span>
                  <div className={styles.marketSymbolWrap}>
                    <input
                      className={styles.marketSymbolInput}
                      value={marketSymbolInput}
                      onChange={(event) => {
                        setMarketSymbolInput(event.target.value);
                        setShowMarketMatches(true);
                      }}
                      onFocus={() => setShowMarketMatches(marketSymbolMatches.length > 0)}
                      placeholder="Search symbol..."
                    />
                    {showMarketMatches && marketSymbolMatches.length > 0 ? (
                      <ul className={styles.marketAutocomplete}>
                        {marketSymbolMatches.map((match) => (
                          <li key={`${match.symbol}-${match.region}`}>
                            <button
                              type="button"
                              className={styles.marketAutocompleteButton}
                              onClick={() => handleMarketSymbolSelect(match)}
                            >
                              <span>{match.symbol}</span>
                              <span className={styles.marketAutocompleteMeta}>
                                {match.name}
                              </span>
                            </button>
                          </li>
                        ))}
                      </ul>
                    ) : null}
                  </div>
                </label>

                <label className={styles.macroFilterField}>
                  <span className={styles.macroFilterLabel}>Function</span>
                  <select
                    className={styles.macroSelect}
                    value={marketFunction}
                    onChange={(event) => setMarketFunction(event.target.value as MarketFunction)}
                  >
                    {MARKET_FUNCTION_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>

                <label className={styles.macroFilterField}>
                  <span className={styles.macroFilterLabel}>Interval</span>
                  <select
                    className={styles.macroSelect}
                    value={marketInterval}
                    onChange={(event) =>
                      setMarketInterval(event.target.value as "1min" | "5min" | "15min" | "30min" | "60min")
                    }
                    disabled={marketFunction !== "TIME_SERIES_INTRADAY"}
                  >
                    <option value="1min">1min</option>
                    <option value="5min">5min</option>
                    <option value="15min">15min</option>
                    <option value="30min">30min</option>
                    <option value="60min">60min</option>
                  </select>
                </label>

                <label className={styles.macroFilterField}>
                  <span className={styles.macroFilterLabel}>Adjusted</span>
                  <select
                    className={styles.macroSelect}
                    value={marketAdjusted}
                    onChange={(event) => setMarketAdjusted(event.target.value as "default" | "true" | "false")}
                    disabled={marketFunction !== "TIME_SERIES_INTRADAY"}
                  >
                    <option value="default">Default</option>
                    <option value="true">True</option>
                    <option value="false">False</option>
                  </select>
                </label>

                <label className={styles.macroFilterField}>
                  <span className={styles.macroFilterLabel}>Extended Hours</span>
                  <select
                    className={styles.macroSelect}
                    value={marketExtendedHours}
                    onChange={(event) => setMarketExtendedHours(event.target.value as "default" | "true" | "false")}
                    disabled={marketFunction !== "TIME_SERIES_INTRADAY"}
                  >
                    <option value="default">Default</option>
                    <option value="true">True</option>
                    <option value="false">False</option>
                  </select>
                </label>

                <label className={styles.macroFilterField}>
                  <span className={styles.macroFilterLabel}>Month</span>
                  <select
                    className={styles.macroSelect}
                    value={marketMonth}
                    onChange={(event) => setMarketMonth(event.target.value)}
                    disabled={marketFunction !== "TIME_SERIES_INTRADAY"}
                  >
                    <option value="">Latest month</option>
                    {recentMonthOptions.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </label>

                <label className={styles.macroFilterField}>
                  <span className={styles.macroFilterLabel}>Entitlement</span>
                  <select
                    className={styles.macroSelect}
                    value={marketEntitlement}
                    onChange={(event) =>
                      setMarketEntitlement(event.target.value as "default" | "realtime" | "delayed")
                    }
                    disabled={
                      marketFunction !== "TIME_SERIES_INTRADAY" &&
                      marketFunction !== "TIME_SERIES_DAILY" &&
                      marketFunction !== "TIME_SERIES_DAILY_ADJUSTED"
                    }
                  >
                    <option value="default">Default</option>
                    <option value="realtime">Realtime</option>
                    <option value="delayed">Delayed</option>
                  </select>
                </label>
              </div>

              <div className={styles.macroSearchRow}>
                <button
                  type="button"
                  className={styles.macroSearchButton}
                  onClick={handleMarketSearchClick}
                  disabled={!marketSymbolInput.trim() || marketLoading}
                >
                  {marketLoading ? "Loading..." : "Search"}
                </button>
              </div>

              <p className={styles.macroStatus}>
                Selected indicators: {marketCards.length}/{MAX_MARKET_GRAPHS}
              </p>
              {marketSymbolLoading ? (
                <p className={styles.macroStatus}>Searching symbols...</p>
              ) : null}
              {marketLoading ? <p className={styles.macroStatus}>Loading market data...</p> : null}
              {marketError ? <p className={styles.macroError}>{marketError}</p> : null}

              {marketCards.length === 0 ? (
                <p className={styles.macroEmpty}>
                  Search to generate market graphs.
                </p>
              ) : (
                <div className={styles.seriesGrid}>
                  {marketCards.map((card) => (
                    <article key={card.marketKey} className={styles.seriesCard}>
                      <div className={styles.seriesTop}>
                        <div>
                          <p className={styles.seriesName}>{card.name}</p>
                        </div>
                        <div className={styles.seriesMetric}>
                          <p className={styles.seriesValue}>{card.value}</p>
                          <p
                            className={`${styles.seriesChange} ${
                              card.tone === "up" ? styles.changeUp : styles.changeDown
                            }`}
                          >
                            {card.change}
                          </p>
                        </div>
                      </div>
                      <Sparkline points={card.points} tone={card.tone} xLabels={card.xLabels} />
                    </article>
                  ))}
                </div>
              )}
            </section>

            <section id="macro-indicators" className={styles.panel}>
              <div className={styles.panelHead}>
                <h2 className={styles.featureTitle}>Today&apos;s Macroeconomic Indicators</h2>
                <span className={styles.annotation}>
                  TODO: Add global/country expansion (currently USA only)
                </span>
              </div>

              <div className={styles.macroFilterRow}>
                <label className={styles.macroFilterField}>
                  <span className={styles.macroFilterLabel}>Country</span>
                  <select
                    className={styles.macroSelect}
                    value={selectedCountry}
                    onChange={(event) => {
                      setSelectedCountry(event.target.value);
                      setMacroCards([]);
                    }}
                  >
                    <option value="USA">USA</option>
                  </select>
                </label>

                <label className={styles.macroFilterField}>
                  <span className={styles.macroFilterLabel}>Category</span>
                  <select
                    className={styles.macroSelect}
                    value={selectedCategory}
                    onChange={(event) => {
                      setSelectedCategory(event.target.value);
                      setSelectedIndicator("");
                    }}
                    disabled={categories.length === 0}
                  >
                    {categories.length === 0 ? (
                      <option value="">Loading categories...</option>
                    ) : null}
                    {categories.map((category) => (
                      <option key={category.key} value={category.key}>
                        {category.label}
                      </option>
                    ))}
                  </select>
                </label>

                <label className={styles.macroFilterField}>
                  <span className={styles.macroFilterLabel}>Indicator (max 8)</span>
                  <select
                    className={styles.macroSelect}
                    value={selectedIndicator}
                    onChange={handleIndicatorSelect}
                    disabled={!selectedCategory || indicators.length === 0}
                  >
                    <option value="">
                      {selectedCategory ? "Choose indicator..." : "Choose category first"}
                    </option>
                    {indicators.map((indicator) => (
                      <option key={indicator.key} value={indicator.key}>
                        {indicator.label}
                      </option>
                    ))}
                  </select>
                </label>

                <label className={styles.macroFilterField}>
                  <span className={styles.macroFilterLabel}>Start Date</span>
                  <input
                    type="date"
                    className={styles.macroDateInput}
                    value={startDate}
                    onChange={(event) => setStartDate(event.target.value)}
                    max={endDate || undefined}
                  />
                </label>

                <label className={styles.macroFilterField}>
                  <span className={styles.macroFilterLabel}>End Date</span>
                  <input
                    type="date"
                    className={styles.macroDateInput}
                    value={endDate}
                    onChange={(event) => setEndDate(event.target.value)}
                    min={startDate || undefined}
                  />
                </label>

              </div>

              <div className={styles.macroSearchRow}>
                <button
                  type="button"
                  className={styles.macroSearchButton}
                  onClick={handleSearchClick}
                  disabled={!selectedCategory || !selectedIndicator || macroLoading}
                >
                  {macroLoading ? "Loading..." : "Search"}
                </button>
              </div>

              <p className={styles.macroStatus}>
                Selected indicators: {macroCards.length}/{MAX_MACRO_GRAPHS}
              </p>
              {macroLoading ? <p className={styles.macroStatus}>Loading macro data...</p> : null}
              {macroError ? <p className={styles.macroError}>{macroError}</p> : null}

              {macroCards.length === 0 ? (
                <p className={styles.macroEmpty}>
                  Search to generate graphs.
                </p>
              ) : (
                <div className={styles.seriesGrid}>
                  {macroCards.map((card) => (
                    <article key={card.indicatorKey} className={styles.seriesCard}>
                      <div className={styles.seriesTop}>
                        <div>
                          <p className={styles.seriesName}>{card.name}</p>
                        </div>
                        <div className={styles.seriesMetric}>
                          <p className={styles.seriesValue}>{card.value}</p>
                          <p
                            className={`${styles.seriesChange} ${
                              card.tone === "up" ? styles.changeUp : styles.changeDown
                            }`}
                          >
                            {card.change}
                          </p>
                        </div>
                      </div>
                      <Sparkline points={card.points} tone={card.tone} xLabels={card.xLabels} />
                    </article>
                  ))}
                </div>
              )}
            </section>

            <section id="timelines" className={styles.panel}>
              <div className={styles.panelHead}>
                <h2 className={styles.featureTitle}>
                  Timelines
                </h2>
                <span className={styles.annotation}>
                  TODO: Implement timeline frontend/backend logic (High, medium, low = importance score)
                </span>
              </div>

              <div className={styles.queryRow}>
                <input
                  readOnly
                  value="inflation"
                  aria-label="Timeline topic query"
                  className={styles.queryInput}
                />
                <button type="button" className={styles.queryButton}>
                  Query Timeline
                </button>
              </div>

              <div className={styles.timelineList}>
                {timelineEvents.map((event) => (
                  <article key={`${event.date}-${event.title}`} className={styles.timelineEvent}>
                    <span className={styles.timelineDot} />
                    <div className={styles.timelineMeta}>
                      <p className={styles.timelineDate}>{event.date}</p>
                      <span className={`${styles.impactTag} ${impactToneClass(event.impact)}`}>
                        {event.impact}
                      </span>
                    </div>
                    <p className={styles.timelineTitle}>{event.title}</p>
                    <p className={styles.timelineText}>{event.text}</p>
                    <p className={styles.timelineSource}>Source: {event.source}</p>
                  </article>
                ))}
              </div>
            </section>
          </div>

          <div className={styles.stack}>
            <section id="news-feed" className={styles.panel}>
              <div className={styles.panelHead}>
                <h2 className={styles.featureTitle}>
                  Current News
                </h2>
              </div>

              <div
                ref={newsViewportRef}
                className={styles.newsViewport}
                aria-live="polite"
                onScroll={handleNewsScroll}
              >
                {newsLoading ? <p className={styles.newsStatus}>Loading news...</p> : null}
                {newsError ? <p className={styles.newsError}>{newsError}</p> : null}
                {!newsLoading && !newsError && newsArticles.length === 0 ? (
                  <p className={styles.newsStatus}>No news available.</p>
                ) : null}

                {!newsLoading && !newsError && newsArticles.length > 0 ? (
                  <div className={styles.newsTrack}>
                    {newsArticles.map((article) => (
                      <article key={article.id} className={styles.newsCard}>
                        <p className={styles.newsTitle}>{article.title}</p>
                        <p className={styles.newsDescription}>{article.description}</p>
                      </article>
                    ))}
                  </div>
                ) : null}
              </div>
            </section>

            <section id="theme-heat" className={styles.panel}>
              <div className={styles.panelHead}>
                <h2 className={styles.featureTitle}>
                  Trending Themes
                </h2>
                <span className={styles.annotation}>
                  TODO: Retrieve highest heat score themes from database.
                </span>
              </div>

              <div className={styles.heatGrid}>
                {heatCells.map((cell) => (
                  <div
                    key={cell.topic}
                    className={styles.heatCell}
                    style={heatToneStyle(cell.score)}
                  >
                    <p className={styles.heatTopic}>{cell.topic}</p>
                    <p className={styles.heatScore}>{cell.score}</p>
                  </div>
                ))}
              </div>
            </section>

            <section id="ai-assistant" className={styles.panel}>
              <div className={styles.panelHead}>
                <h2 className={styles.featureTitle}>
                  Chatbot
                </h2>
                <span className={styles.annotation}>
                  TODO: Implement RAG style chatbot (Traditonal/GraphRAG/Agentic RAG)
                </span>
              </div>

              <div className={styles.chatThread}>
                {chatMessages.map((msg, i) => (
                  <div
                    key={`${msg.role}-${i}`}
                    className={`${styles.chatBubble} ${
                      msg.role === "user" ? styles.chatUser : styles.chatAssistant
                    }`}
                  >
                    <p className={styles.chatRole}>{msg.role}</p>
                    <p className={styles.chatText}>{msg.text}</p>
                  </div>
                ))}
              </div>

              <div className={styles.chatDetail}>
                <p className={styles.subHeading}>
                  Chain of Thought
                </p>
                <ul className={styles.smallList}>
                  {chatReasoning.map((step) => (
                    <li key={step}>{step}</li>
                  ))}
                </ul>
                <p className={styles.subHeading}>
                  Sources Cited
                </p>
                <ul className={styles.sourceList}>
                  {chatSources.map((source) => (
                    <li key={source}>- {source}</li>
                  ))}
                </ul>
                <p className={styles.savedStatus}>
                  Conversation status: Saved to backend session #CH-204
                </p>
              </div>
            </section>

            <section id="notifications" className={styles.panel}>
              <div className={styles.panelHead}>
                <h2 className={styles.featureTitle}>
                  Notifications
                </h2>
                <span className={styles.annotation}>
                  TODO: Create notification and send alert when heat thresholds are exceeded
                </span>
              </div>

              <div className={styles.alertList}>
                {alertRules.map((rule) => (
                  <article key={rule.name} className={styles.alertCard}>
                    <div className={styles.alertTop}>
                      <p className={styles.alertName}>{rule.name}</p>
                      <span className={`${styles.alertBadge} ${alertToneClass(rule.status)}`}>
                        {rule.status}
                      </span>
                    </div>
                    <p className={styles.alertMeta}>Trigger: {rule.threshold}</p>
                    <p className={styles.alertDetail}>{rule.detail}</p>
                  </article>
                ))}
              </div>
            </section>
          </div>
        </section>
      </main>
    </div>
  );
}
