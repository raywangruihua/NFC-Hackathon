import type { CSSProperties } from "react";
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
  tone: "up" | "down";
  type: "stock" | "macro";
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

const macroSeriesCards: SeriesCard[] = [
  {
    name: "Real GDP",
    value: "5,148.42",
    change: "+0.72%",
    points: [38, 42, 41, 46, 44, 50, 52],
    tone: "up",
    type: "stock",
  },
  {
    name: "US 10Y Yield",
    value: "4.21%",
    change: "-0.08%",
    points: [55, 54, 52, 51, 49, 48, 47],
    tone: "down",
    type: "macro",
  },
  {
    name: "CPI YoY",
    value: "3.1%",
    change: "-0.20%",
    points: [60, 58, 57, 55, 54, 52, 50],
    tone: "down",
    type: "macro",
  },
  {
    name: "Unemployment",
    value: "3.9%",
    change: "+0.10%",
    points: [42, 41, 43, 45, 44, 46, 47],
    tone: "up",
    type: "macro",
  },
];

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

const chatReasoning = [
  "Step 1: Pull latest yield curve and inflation surprise data.",
  "Step 2: Compare factor exposure for mega-cap tech vs broad market.",
  "Step 3: Rank themes by impact score and confidence.",
];

const chatSources = [
  "FRED: 10Y Real Yield",
  "BLS CPI Release",
  "SEC Filings: Selected tech names",
];

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

function Sparkline({ points, tone }: { points: number[]; tone: "up" | "down" }) {
  const width = 360;
  const height = 170;
  const padLeft = 16;
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

  const xTicks = [
    { label: "T1", x: padLeft },
    { label: `T${Math.ceil(points.length / 2)}`, x: padLeft + plotWidth / 2 },
    { label: `T${points.length}`, x: padLeft + plotWidth },
  ];

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
            {tick.value.toFixed(0)}
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

export default function Home() {
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
            <li className={styles.moduleItem}>
              <ChartCandlestick className={styles.moduleIcon} aria-hidden />
              <span>Market</span>
            </li>
            <li className={styles.moduleItem}>
              <Earth className={styles.moduleIcon} aria-hidden />
              <span>Macro Indicators</span>
            </li>
            <li className={styles.moduleItem}>
              <Newspaper className={styles.moduleIcon} aria-hidden />
              <span>Timelines</span>
            </li>
            <li className={styles.moduleItem}>
              <Thermometer className={styles.moduleIcon} aria-hidden />
              <span>Theme Heat</span>
            </li>
            <li className={styles.moduleItem}>
              <Bot className={styles.moduleIcon} aria-hidden />
              <span>AI Assistant</span>
            </li>
            <li className={styles.moduleItem}>
              <Bell className={styles.moduleIcon} aria-hidden />
              <span>Alerts</span>
            </li>
          </ul>
        </aside>

        <section className={styles.contentGrid}>
          <div className={styles.stack}>
            <section className={styles.panel}>
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

            <section className={styles.panel}>
              <div className={styles.panelHead}>
                <h2 className={styles.featureTitle}>Today&apos;s Macroeconomic Indicators</h2>
                <span className={styles.annotation}>
                  TODO: Connect backend API to display real data, add graphs page with more detailed information for graphs
                </span>
              </div>

              <div className={styles.seriesGrid}>
                {macroSeriesCards.map((card) => (
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

            <section className={styles.panel}>
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
            <section className={styles.panel}>
              <div className={styles.panelHead}>
                <h2 className={styles.featureTitle}>
                  Trending Themes
                </h2>
                <span className={styles.annotation}>
                  TODO: Retrieve highest heat score themes from database
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

            <section className={styles.panel}>
              <div className={styles.panelHead}>
                <h2 className={styles.featureTitle}>
                  FEATURE 4: CHATBOT WITH REASONING + SOURCES
                </h2>
                <span className={styles.annotation}>
                  Annotation: POST /api/chat and POST /api/chat/save
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
                  Reasoning Trace (UI mock)
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

            <section className={styles.panel}>
              <div className={styles.panelHead}>
                <h2 className={styles.featureTitle}>
                  FEATURE 5: NOTIFICATION & ALERT SERVICE
                </h2>
                <span className={styles.annotation}>
                  Annotation: stream from /api/alerts (risk + heat thresholds)
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
