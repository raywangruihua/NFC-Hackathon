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

const seriesCards: SeriesCard[] = [
  {
    name: "S&P 500",
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

const gdpBars = [
  { q: "Q1", v: 2.2 },
  { q: "Q2", v: 1.9 },
  { q: "Q3", v: 2.4 },
  { q: "Q4", v: 2.1 },
  { q: "Q1*", v: 1.7 },
];

const timelineEvents: TimelineEvent[] = [
  {
    date: "2026-02-27",
    title: "Fed signals caution on rate cuts",
    source: "FOMC Minutes",
    impact: "High",
  },
  {
    date: "2026-02-21",
    title: "Core inflation prints below estimate",
    source: "BLS Release",
    impact: "High",
  },
  {
    date: "2026-02-15",
    title: "Manufacturing PMI re-enters expansion",
    source: "ISM",
    impact: "Medium",
  },
  {
    date: "2026-02-08",
    title: "Labor market remains resilient",
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
  { topic: "Supply Chain", score: 44 },
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
  const width = 220;
  const height = 72;
  const max = Math.max(...points);
  const min = Math.min(...points);
  const spread = Math.max(max - min, 1);

  const path = points
    .map((point, i) => {
      const x = (i / (points.length - 1)) * width;
      const y = height - ((point - min) / spread) * height;
      return `${i === 0 ? "M" : "L"} ${x} ${y}`;
    })
    .join(" ");

  const stroke = tone === "up" ? "#2DD4BF" : "#FB7185";

  return (
    <svg
      className="h-[72px] w-full rounded bg-[#09111d]"
      viewBox={`0 0 ${width} ${height}`}
      preserveAspectRatio="none"
      aria-hidden
    >
      <path d={path} fill="none" stroke={stroke} strokeWidth="2.5" />
    </svg>
  );
}

function heatTone(score: number) {
  if (score >= 75) return "bg-red-500/30 text-red-200 border-red-300/30";
  if (score >= 60) return "bg-orange-400/25 text-orange-100 border-orange-300/35";
  if (score >= 45) return "bg-yellow-300/20 text-yellow-100 border-yellow-200/30";
  return "bg-cyan-500/20 text-cyan-100 border-cyan-300/30";
}

export default function Home() {
  return (
    <div className="min-h-screen bg-[#050b14] text-slate-100">
      <header className="border-b border-cyan-300/20 bg-[#081224]">
        <div className="mx-auto flex w-full max-w-[1600px] flex-wrap items-center gap-3 px-4 py-3 sm:px-6">
          <p className="text-sm font-semibold tracking-[0.22em] text-cyan-300">
            MACRO COMMAND
          </p>
          <div className="h-4 w-px bg-cyan-400/40" />
          <p className="text-xs text-slate-300">Terminal-style Macro Tracker MVP</p>
          <span className="ml-auto rounded border border-cyan-300/30 bg-cyan-900/40 px-2 py-1 text-[11px] text-cyan-100">
            Live mode (mock)
          </span>
        </div>
      </header>

      <main className="mx-auto grid w-full max-w-[1600px] grid-cols-1 gap-4 p-4 sm:p-6 lg:grid-cols-[230px_1fr]">
        <aside className="rounded-lg border border-slate-700/70 bg-[#0b1524] p-4">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Modules
          </p>
          <ul className="mt-3 space-y-2 text-sm text-slate-200">
            <li className="rounded border border-amber-300/30 bg-amber-300/10 px-3 py-2">
              Market & Macro
            </li>
            <li className="rounded border border-slate-600 px-3 py-2">Timelines</li>
            <li className="rounded border border-slate-600 px-3 py-2">Theme Heat</li>
            <li className="rounded border border-slate-600 px-3 py-2">AI Assistant</li>
            <li className="rounded border border-slate-600 px-3 py-2">Alerts</li>
          </ul>
          <div className="mt-4 rounded border border-cyan-300/25 bg-cyan-950/40 p-3 text-xs text-cyan-100">
            Annotated MVP
            <p className="mt-1 text-cyan-50/90">
              Focused on frontend look/flow. Data calls are represented as mock
              backend bindings.
            </p>
          </div>
        </aside>

        <section className="grid grid-cols-1 gap-4 xl:grid-cols-[2fr_1fr]">
          <div className="space-y-4">
            <section className="rounded-lg border border-slate-700/70 bg-[#0b1524] p-4">
              <div className="mb-3 flex flex-wrap items-center gap-2">
                <h2 className="text-sm font-semibold tracking-wide text-amber-300">
                  FEATURE 1: MARKET + MACRO GRAPHS
                </h2>
                <span className="rounded border border-amber-200/35 bg-amber-200/10 px-2 py-1 text-[11px] text-amber-100">
                  Annotation: /api/series?tickers=SPX,CPI,GDP,UNRATE
                </span>
              </div>

              <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                {seriesCards.map((card) => (
                  <article
                    key={card.name}
                    className="rounded border border-slate-600/70 bg-[#0a1320] p-3"
                  >
                    <div className="mb-2 flex items-end justify-between">
                      <div>
                        <p className="text-xs uppercase tracking-wider text-slate-400">
                          {card.type}
                        </p>
                        <p className="text-sm font-semibold text-slate-50">{card.name}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-semibold text-slate-50">{card.value}</p>
                        <p
                          className={
                            card.tone === "up" ? "text-xs text-teal-300" : "text-xs text-rose-300"
                          }
                        >
                          {card.change}
                        </p>
                      </div>
                    </div>
                    <Sparkline points={card.points} tone={card.tone} />
                  </article>
                ))}
              </div>

              <article className="mt-3 rounded border border-slate-600/70 bg-[#0a1320] p-3">
                <div className="mb-2 flex items-center justify-between">
                  <p className="text-sm font-semibold text-slate-100">GDP Growth (Quarterly)</p>
                  <p className="text-xs text-slate-400">MVP bar visualization</p>
                </div>
                <div className="flex h-32 items-end gap-2">
                  {gdpBars.map((bar) => (
                    <div key={bar.q} className="flex flex-1 flex-col items-center gap-2">
                      <div
                        className="w-full rounded-t bg-cyan-400/70"
                        style={{ height: `${bar.v * 30}px` }}
                      />
                      <p className="text-[11px] text-slate-300">{bar.q}</p>
                    </div>
                  ))}
                </div>
              </article>
            </section>

            <section className="rounded-lg border border-slate-700/70 bg-[#0b1524] p-4">
              <div className="mb-3 flex flex-wrap items-center gap-2">
                <h2 className="text-sm font-semibold tracking-wide text-amber-300">
                  FEATURE 2: QUERYABLE TIMELINE (DB-BACKED)
                </h2>
                <span className="rounded border border-amber-200/35 bg-amber-200/10 px-2 py-1 text-[11px] text-amber-100">
                  Annotation: GET /api/timeline?topic=inflation - from database
                </span>
              </div>

              <div className="mb-4 flex flex-col gap-2 sm:flex-row">
                <input
                  readOnly
                  value="inflation"
                  aria-label="Timeline topic query"
                  className="w-full rounded border border-slate-500 bg-[#07101b] px-3 py-2 text-sm text-slate-100 outline-none"
                />
                <button
                  type="button"
                  className="rounded border border-cyan-300/40 bg-cyan-500/15 px-4 py-2 text-sm text-cyan-100"
                >
                  Query Timeline
                </button>
              </div>

              <div className="relative space-y-3 pl-4 before:absolute before:left-[6px] before:top-1 before:h-[95%] before:w-px before:bg-slate-500/80">
                {timelineEvents.map((event) => (
                  <article
                    key={`${event.date}-${event.title}`}
                    className="relative rounded border border-slate-600/70 bg-[#0a1320] p-3"
                  >
                    <span className="absolute -left-[15px] top-4 h-3 w-3 rounded-full border border-cyan-300/40 bg-cyan-400/70" />
                    <div className="flex flex-wrap items-center gap-2">
                      <p className="text-xs text-slate-400">{event.date}</p>
                      <span className="rounded bg-slate-700/70 px-2 py-0.5 text-[10px] uppercase tracking-wider text-slate-200">
                        {event.impact}
                      </span>
                    </div>
                    <p className="mt-1 text-sm font-medium text-slate-50">{event.title}</p>
                    <p className="text-xs text-slate-300">Source: {event.source}</p>
                  </article>
                ))}
              </div>
            </section>
          </div>

          <div className="space-y-4">
            <section className="rounded-lg border border-slate-700/70 bg-[#0b1524] p-4">
              <div className="mb-3 flex flex-wrap items-center gap-2">
                <h2 className="text-sm font-semibold tracking-wide text-amber-300">
                  FEATURE 3: TRENDING TOPIC HEAT MAP
                </h2>
                <span className="rounded border border-amber-200/35 bg-amber-200/10 px-2 py-1 text-[11px] text-amber-100">
                  Annotation: GET /api/heatmap - backend ranked topics
                </span>
              </div>

              <div className="grid grid-cols-3 gap-2">
                {heatCells.map((cell) => (
                  <div
                    key={cell.topic}
                    className={`rounded border p-2 ${heatTone(cell.score)}`}
                  >
                    <p className="text-xs font-medium">{cell.topic}</p>
                    <p className="text-[11px]">Heat {cell.score}</p>
                  </div>
                ))}
              </div>
            </section>

            <section className="rounded-lg border border-slate-700/70 bg-[#0b1524] p-4">
              <div className="mb-3 flex flex-wrap items-center gap-2">
                <h2 className="text-sm font-semibold tracking-wide text-amber-300">
                  FEATURE 4: CHATBOT WITH REASONING + SOURCES
                </h2>
                <span className="rounded border border-amber-200/35 bg-amber-200/10 px-2 py-1 text-[11px] text-amber-100">
                  Annotation: POST /api/chat and POST /api/chat/save
                </span>
              </div>

              <div className="space-y-2 rounded border border-slate-600/70 bg-[#0a1320] p-3">
                {chatMessages.map((msg, i) => (
                  <div
                    key={`${msg.role}-${i}`}
                    className={`rounded p-2 text-sm ${
                      msg.role === "user"
                        ? "bg-slate-700/80 text-slate-100"
                        : "bg-cyan-900/45 text-cyan-50"
                    }`}
                  >
                    <p className="mb-1 text-[11px] uppercase tracking-wide text-slate-300">
                      {msg.role}
                    </p>
                    <p>{msg.text}</p>
                  </div>
                ))}
              </div>

              <div className="mt-3 rounded border border-slate-600/70 bg-[#0a1320] p-3">
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-300">
                  Reasoning Trace (UI mock)
                </p>
                <ul className="mt-2 space-y-1 text-xs text-slate-200">
                  {chatReasoning.map((step) => (
                    <li key={step}>{step}</li>
                  ))}
                </ul>
                <p className="mt-3 text-xs font-semibold uppercase tracking-wider text-slate-300">
                  Sources Cited
                </p>
                <ul className="mt-1 space-y-1 text-xs text-cyan-100">
                  {chatSources.map((source) => (
                    <li key={source}>- {source}</li>
                  ))}
                </ul>
                <p className="mt-3 text-[11px] text-teal-300">
                  Conversation status: Saved to backend session #CH-204
                </p>
              </div>
            </section>

            <section className="rounded-lg border border-slate-700/70 bg-[#0b1524] p-4">
              <div className="mb-3 flex flex-wrap items-center gap-2">
                <h2 className="text-sm font-semibold tracking-wide text-amber-300">
                  FEATURE 5: NOTIFICATION & ALERT SERVICE
                </h2>
                <span className="rounded border border-amber-200/35 bg-amber-200/10 px-2 py-1 text-[11px] text-amber-100">
                  Annotation: stream from /api/alerts (risk + heat thresholds)
                </span>
              </div>

              <div className="space-y-2">
                {alertRules.map((rule) => (
                  <article
                    key={rule.name}
                    className="rounded border border-slate-600/70 bg-[#0a1320] p-3"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <p className="text-sm font-medium text-slate-50">{rule.name}</p>
                      <span
                        className={`rounded px-2 py-0.5 text-[11px] ${
                          rule.status === "Breached"
                            ? "bg-rose-500/25 text-rose-100"
                            : "bg-cyan-500/25 text-cyan-100"
                        }`}
                      >
                        {rule.status}
                      </span>
                    </div>
                    <p className="mt-1 text-xs text-slate-300">Trigger: {rule.threshold}</p>
                    <p className="text-xs text-slate-400">{rule.detail}</p>
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
