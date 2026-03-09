"use client";

import { useEffect, useState, type CSSProperties, type ChangeEvent } from "react";
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
  process.env.NEXT_PUBLIC_BACKEND_BASE_URL ?? "http://localhost:8000";
const MAX_MACRO_GRAPHS = 8;

// Place holder market data
const marketSeriesCards: SeriesCard[] = [
  {
    name: "S&P 500",
    value: "5,148.42",
    change: "+0.72%",
    points: [38, 42, 41, 46, 44, 50, 52],
    tone: "up",
    type: "stock",
  },
  {
    name: "AAPL",
    value: "4.21%",
    change: "-0.08%",
    points: [55, 54, 52, 51, 49, 48, 47],
    tone: "down",
    type: "macro",
  },
  {
    name: "NVDA",
    value: "3.1%",
    change: "-0.20%",
    points: [60, 58, 57, 55, 54, 52, 50],
    tone: "down",
    type: "macro",
  },
  {
    name: "TSLA",
    value: "3.9%",
    change: "+0.10%",
    points: [42, 41, 43, 45, 44, 46, 47],
    tone: "up",
    type: "macro",
  },
];

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
/*
const heatCells: HeatCell[] = [
  { topic: "Rate Cuts", score: 88 },
  { topic: "AI Capex", score: 73 },
  { topic: "Energy Shock", score: 66 },
  { topic: "Fiscal Risk", score: 54 },
  { topic: "China Demand", score: 49 },
  { topic: "Supply Chain", score: 0 },
  { topic: "Bank Stress", score: 61 },
  { topic: "Housing", score: 47 },
  { topic: "USD Strength", score: 52 },
];
*/



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
   * Generate heat tone colour for heat map based on heat score.
   */
  const clamped = Math.max(0, Math.min(100, score));
  const hue = 120 - (clamped / 100) * 120;
  const darkFill = `hsl(${hue}, 62%, 23%)`;
  const border = `hsl(${hue}, 68%, 34%)`;

  return {
    backgroundColor: darkFill,
    borderColor: border,
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

export default function Home() {
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
  const [heatCells, setHeatCells] = useState<HeatCell[]>([]);
  const [heatLoading, setHeatLoading] = useState(false);
  const [heatError, setHeatError] = useState<string | null>(null);

  // Country selection drop down menu
  useEffect(() => {
    const controller = new AbortController();

    async function loadCategories() {
      setMacroLoading(true);
      setMacroError(null);
      try {
        const response = await fetch(
          `${API_BASE_URL}/api/fred/categories?country=${encodeURIComponent(
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
          `${API_BASE_URL}/api/fred/indicators?category=${encodeURIComponent(selectedCategory)}`,
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

  

  useEffect(() => {
    const controller = new AbortController();

    async function loadHottestThemes() {
      setHeatLoading(true);
      setHeatError(null);

      try {
        const response = await fetch(`${API_BASE_URL}/api/themes/hottest?limit=9`, {
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error("Failed to load hottest themes.");
        }

        const data = (await response.json()) as Array<{ topic: string; score: number }>;
        const normalized = data.map((item) => ({
          topic: item.topic,
          score: Math.max(0, Math.min(100, Number(item.score) || 0)),
        }));

        setHeatCells(normalized);
      } catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") return;
        setHeatCells([]);
        setHeatError("Unable to load theme heat data.");
      } finally {
        setHeatLoading(false);
      }
    }

    void loadHottestThemes();
    return () => controller.abort();
  }, []);

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
        `${API_BASE_URL}/api/fred/series?${query.toString()}`
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

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className={styles.headerInner}>
          <p className={styles.brand}>DAMMIT FINANCE MANAGER</p>
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
                <span className={styles.annotation}>
                  TODO: Connect backend API to display real data, add graphs page with more detailed information for graphs
                </span>
              </div>

              <div className={styles.seriesGrid}>
                {marketSeriesCards.map((card) => (
                  <article key={card.name} className={styles.seriesCard}>
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
                    <Sparkline points={card.points} tone={card.tone} />
                  </article>
                ))}
              </div>
            </section>

            <section id="macro-indicators" className={styles.panel}>
              <div className={styles.panelHead}>
                <h2 className={styles.featureTitle}>Today&apos;s Macroeconomic Indicators</h2>
                <span className={styles.annotation}>
                  TODO: Add global/country expansion (currently USA only) and richer chart drill-down
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
            <section id="theme-heat" className={styles.panel}>
              <div className={styles.panelHead}>
                <h2 className={styles.featureTitle}>
                  Trending Themes
                </h2>
                <span className={styles.annotation}>
                  TODO: Retrieve highest heat score themes from database
                </span>
              </div>

              {heatLoading ? <p className={styles.macroStatus}>Loading theme heat...</p> : null}
              {heatError ? <p className={styles.macroError}>{heatError}</p> : null}

              {heatCells.length === 0 ? (
                <p className={styles.macroEmpty}>No theme heat data yet.</p>
              ) : (
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
              )}
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



