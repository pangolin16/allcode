import { useState, useEffect, useRef } from "react";

const QUICK_PICKS = ["AAPL", "MSFT", "GOOGL", "NVDA", "AMZN", "META"];

const SP500_RETURNS = [-38.5, 26.5, 15.1, 32.4, 13.7, 1.4, 12.0, 21.8, -4.4, 31.5, 18.4, 28.7, -18.1, 26.3, 24.0];

function fmtB(n) {
  if (n == null || isNaN(n)) return "—";
  if (Math.abs(n) >= 1000) return "$" + (n / 1000).toFixed(1) + "T";
  return "$" + n.toFixed(1) + "B";
}
function fmtPct(n, decimals = 1) {
  if (n == null || isNaN(n)) return "—";
  return (n >= 0 ? "+" : "") + n.toFixed(decimals) + "%";
}
function colorOf(n) {
  if (n == null || isNaN(n)) return "#4a6a8a";
  return n >= 0 ? "#00e676" : "#ff3d5a";
}

// ── Mini bar chart ──────────────────────────────────────────────────────────
function BarChart({ data, labels, color, unit = "" }) {
  const max = Math.max(...data.map(Math.abs), 0.001);
  return (
    <div style={{ display: "flex", alignItems: "flex-end", gap: 3, height: 120, paddingTop: 8 }}>
      {data.map((v, i) => {
        const pct = Math.abs(v) / max;
        const isNeg = v < 0;
        const barH = Math.max(pct * 100, 2);
        return (
          <div key={i} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "flex-end", height: "100%" }}>
            <div
              title={`${labels[i]}: ${v?.toFixed(2)}${unit}`}
              style={{
                width: "100%",
                height: barH + "%",
                background: typeof color === "function" ? color(v) : color,
                opacity: 0.85,
                transition: "height 0.4s ease",
                cursor: "default",
              }}
            />
          </div>
        );
      })}
    </div>
  );
}

// ── Mini line chart ─────────────────────────────────────────────────────────
function LineChart({ datasets, labels }) {
  const W = 420, H = 120;
  const allVals = datasets.flatMap(d => d.data).filter(v => v != null);
  const minV = Math.min(...allVals);
  const maxV = Math.max(...allVals);
  const range = maxV - minV || 1;
  const px = (i) => (i / (labels.length - 1)) * (W - 20) + 10;
  const py = (v) => H - 8 - ((v - minV) / range) * (H - 20);

  return (
    <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", height: H }}>
      <line x1="10" y1={H - 8} x2={W - 10} y2={H - 8} stroke="#1e3048" strokeWidth="1" />
      {datasets.map((ds, di) => {
        const pts = ds.data.map((v, i) => v != null ? `${px(i)},${py(v)}` : null).filter(Boolean);
        if (pts.length < 2) return null;
        // Build path with gaps
        let d = "";
        let moved = false;
        ds.data.forEach((v, i) => {
          if (v == null) { moved = false; return; }
          if (!moved) { d += `M${px(i)},${py(v)} `; moved = true; }
          else d += `L${px(i)},${py(v)} `;
        });
        return (
          <g key={di}>
            <path d={d} fill="none" stroke={ds.color} strokeWidth="2" strokeDasharray={ds.dash ? "5,4" : ""} />
            {ds.data.map((v, i) => v != null && (
              <circle key={i} cx={px(i)} cy={py(v)} r="2.5" fill={ds.color}
                style={{ cursor: "default" }}>
                <title>{labels[i]}: {v?.toFixed(2)}</title>
              </circle>
            ))}
          </g>
        );
      })}
    </svg>
  );
}

// ── KPI Card ────────────────────────────────────────────────────────────────
function KPICard({ label, value, sub, color = "#c8dff0" }) {
  return (
    <div style={{
      background: "#0d1520",
      border: "1px solid #1e3048",
      padding: "14px 16px",
      flex: 1,
      minWidth: 130,
    }}>
      <div style={{ fontSize: 9, letterSpacing: 2, textTransform: "uppercase", color: "#4a6a8a", marginBottom: 8 }}>{label}</div>
      <div style={{ fontFamily: "'Syne', sans-serif", fontSize: 20, fontWeight: 800, color, lineHeight: 1 }}>{value}</div>
      {sub && <div style={{ fontSize: 10, color: "#4a6a8a", marginTop: 4 }}>{sub}</div>}
    </div>
  );
}

// ── Chart Panel ─────────────────────────────────────────────────────────────
function ChartPanel({ title, meta, children }) {
  return (
    <div style={{ background: "#0d1520", border: "1px solid #1e3048", padding: 16, flex: 1, minWidth: 0 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 10 }}>
        <span style={{ fontSize: 9, letterSpacing: 2, textTransform: "uppercase", color: "#00d4ff" }}>{title}</span>
        {meta && <span style={{ fontSize: 9, color: "#4a6a8a" }}>{meta}</span>}
      </div>
      {children}
    </div>
  );
}

// ── Main App ────────────────────────────────────────────────────────────────
export default function App() {
  const [ticker, setTicker] = useState("");
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("Enter a ticker symbol and click Analyze.");
  const inputRef = useRef();

  useEffect(() => {
    // preload Syne font
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&display=swap";
    document.head.appendChild(link);
  }, []);

  async function analyze(sym) {
    const t = (sym || ticker).trim().toUpperCase();
    if (!t) return;
    setTicker(t);
    setLoading(true);
    setError("");
    setData(null);
    setStatus(`Fetching FCF/EV model for ${t} vs S&P 500…`);

    try {
      const res = await fetch("/api/messages", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 4000,
          system: "You are a financial data analyst. Return ONLY valid JSON, no markdown, no backticks, no preamble.",
          messages: [{
            role: "user",
            content: `Return historical annual financial data for ${t} from 2010 to 2024 as JSON. Use realistic estimated figures. Format EXACTLY:
{
  "ticker": "${t}",
  "company": "Full Name",
  "sector": "Sector",
  "exchange": "NASDAQ/NYSE",
  "currentPrice": 0.0,
  "marketCap": 0.0,
  "currentEV": 0.0,
  "currentFCF": 0.0,
  "currentFCFEV": 0.00,
  "wacc": 0.09,
  "terminalGrowth": 0.03,
  "intrinsicValue": 0.0,
  "analystTarget": 0.0,
  "years": [2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023,2024],
  "fcf": [0.0,...15 values],
  "ev": [0.0,...15 values],
  "fcfEVMultiple": [0.00,...15 values],
  "fcfGrowth": [null,...15 values],
  "companyReturn": [0.0,...15 values],
  "description": "2-3 sentence FCF trend analysis",
  "valuation": "Undervalued|Fairly Valued|Overvalued",
  "keyInsight": "One key FCF quality insight"
}
All money in BILLIONS USD. fcfEVMultiple = FCF/EV as decimal (3.5% = 0.035). FCF can be negative for early years. Return ONLY the JSON object.`
          }]
        })
      });

      const json = await res.json();
      if (json.error) throw new Error(json.error.message);
      const raw = json.content[0].text.trim().replace(/^```json\s*/i, "").replace(/^```/i, "").replace(/```\s*$/i, "").trim();
      const parsed = JSON.parse(raw);
      setData(parsed);
      setStatus(`Analysis complete — ${parsed.company || t} · ${parsed.years?.length || 0} years loaded`);
    } catch (e) {
      setError(e.message);
      setStatus("Error: " + e.message);
    } finally {
      setLoading(false);
    }
  }

  // Derived data
  const years = data?.years || [];
  const fcf = data?.fcf || [];
  const ev = data?.ev || [];
  const fcfEV = data?.fcfEVMultiple || [];
  const compRet = data?.companyReturn || [];
  const sp500 = SP500_RETURNS.slice(0, years.length);

  const spCumul = [], compCumul = [];
  let sb = 100, cb = 100;
  for (let i = 0; i < years.length; i++) {
    sb *= (1 + (sp500[i] || 0) / 100);
    cb *= (1 + (compRet[i] || 0) / 100);
    spCumul.push(parseFloat(sb.toFixed(1)));
    compCumul.push(parseFloat(cb.toFixed(1)));
  }

  const lastComp = compCumul[compCumul.length - 1] || 100;
  const lastSP = spCumul[spCumul.length - 1] || 100;
  const fcfEVpct = data ? ((data.currentFCFEV || 0) * 100).toFixed(2) : null;
  const valColor = data?.valuation === "Undervalued" ? "#00e676" : data?.valuation === "Overvalued" ? "#ff3d5a" : "#ffd166";

  const s = {
    root: {
      background: "#080c10",
      color: "#c8dff0",
      fontFamily: "'Space Mono', monospace",
      minHeight: "100vh",
      padding: "20px 16px",
      backgroundImage: "linear-gradient(rgba(0,212,255,0.025) 1px,transparent 1px),linear-gradient(90deg,rgba(0,212,255,0.025) 1px,transparent 1px)",
      backgroundSize: "40px 40px",
    },
    wrap: { maxWidth: 1100, margin: "0 auto" },
    header: { display: "flex", justifyContent: "space-between", alignItems: "flex-end", borderBottom: "1px solid #1e3048", paddingBottom: 16, marginBottom: 20 },
    h1: { fontFamily: "'Syne',sans-serif", fontSize: 20, fontWeight: 800, color: "#00d4ff", letterSpacing: -0.5, margin: 0 },
    sub: { fontSize: 9, color: "#4a6a8a", letterSpacing: 2, textTransform: "uppercase", marginTop: 3 },
    badge: { background: "rgba(0,212,255,0.08)", border: "1px solid #00d4ff", color: "#00d4ff", fontSize: 9, padding: "4px 10px", letterSpacing: 2, textTransform: "uppercase" },
    searchPanel: { background: "#0d1520", border: "1px solid #1e3048", padding: "16px 20px", marginBottom: 16, display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" },
    input: { background: "#080c10", border: "1px solid #1e3048", color: "#00d4ff", fontFamily: "'Space Mono',monospace", fontSize: 16, fontWeight: 700, padding: "9px 14px", outline: "none", width: 150, textTransform: "uppercase", letterSpacing: 2 },
    btn: { background: "#00d4ff", color: "#080c10", border: "none", fontFamily: "'Space Mono',monospace", fontSize: 10, fontWeight: 700, letterSpacing: 2, textTransform: "uppercase", padding: "10px 20px", cursor: "pointer" },
    pickBtn: { background: "transparent", border: "1px solid #1e3048", color: "#4a6a8a", fontFamily: "'Space Mono',monospace", fontSize: 9, letterSpacing: 1, padding: "5px 10px", cursor: "pointer", textTransform: "uppercase" },
    statusBar: { display: "flex", alignItems: "center", gap: 10, padding: "8px 14px", background: "#0d1520", border: "1px solid #1e3048", marginBottom: 20, minHeight: 38 },
  };

  return (
    <div style={s.root}>
      <div style={s.wrap}>
        {/* Header */}
        <div style={s.header}>
          <div>
            <div style={s.h1}>FCF / EV ANALYZER</div>
            <div style={s.sub}>Free Cash Flow · Enterprise Value · S&amp;P 500 Benchmark · 2010–2024</div>
          </div>
          <span style={s.badge}>AI-Powered</span>
        </div>

        {/* Search */}
        <div style={s.searchPanel}>
          <span style={{ fontSize: 9, letterSpacing: 2, textTransform: "uppercase", color: "#4a6a8a" }}>Ticker</span>
          <input
            ref={inputRef}
            style={s.input}
            value={ticker}
            onChange={e => setTicker(e.target.value.toUpperCase())}
            onKeyDown={e => e.key === "Enter" && analyze()}
            placeholder="AAPL"
            maxLength={10}
          />
          <button style={{ ...s.btn, opacity: loading ? 0.5 : 1 }} onClick={() => analyze()} disabled={loading}>
            {loading ? "▶ Loading…" : "▶ Analyze"}
          </button>
          <span style={{ fontSize: 9, letterSpacing: 2, textTransform: "uppercase", color: "#4a6a8a", marginLeft: 8 }}>Quick:</span>
          {QUICK_PICKS.map(t => (
            <button key={t} style={s.pickBtn} onClick={() => analyze(t)}>{t}</button>
          ))}
        </div>

        {/* Status */}
        <div style={s.statusBar}>
          <div style={{
            width: 6, height: 6, borderRadius: "50%",
            background: loading ? "#00e676" : error ? "#ff3d5a" : data ? "#00e676" : "#4a6a8a",
            animation: loading ? "pulse 1.5s infinite" : "none",
            flexShrink: 0,
          }} />
          <span style={{ fontSize: 11, color: error ? "#ff3d5a" : "#4a6a8a" }}>{status}</span>
        </div>

        {/* Empty state */}
        {!data && !loading && (
          <div style={{ textAlign: "center", padding: "80px 20px" }}>
            <div style={{ fontFamily: "'Syne',sans-serif", fontSize: 52, fontWeight: 800, color: "#1e3048", letterSpacing: -2 }}>FCF/EV</div>
            <div style={{ fontSize: 11, color: "#4a6a8a", letterSpacing: 1, marginTop: 8 }}>Enter a ticker to compare against S&amp;P 500 (2010–2024)</div>
          </div>
        )}

        {/* Loading skeleton */}
        {loading && (
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {[180, 100, 220].map((h, i) => (
              <div key={i} style={{ height: h, background: "linear-gradient(90deg,#0d1520 25%,#111c2c 50%,#0d1520 75%)", backgroundSize: "200% 100%", border: "1px solid #1e3048", animation: "shimmer 1.5s infinite" }} />
            ))}
            <style>{`
              @keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }
              @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }
            `}</style>
          </div>
        )}

        {/* Dashboard */}
        {data && !loading && (
          <div>
            <style>{`@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.5}}`}</style>

            {/* KPI Row 1 */}
            <div style={{ display: "flex", gap: 1, marginBottom: 1, background: "#1e3048" }}>
              <KPICard label="Company" value={data.company || data.ticker} sub={`${data.sector || ""} · ${data.exchange || ""}`} color="#00d4ff" />
              <KPICard label="FCF / EV Yield" value={fcfEVpct + "%"} sub="Current FCF yield on EV" color={parseFloat(fcfEVpct) > 0 ? "#00e676" : "#ff3d5a"} />
              <KPICard label="Annual FCF" value={fmtB(data.currentFCF)} sub="Trailing twelve months" color="#00d4ff" />
              <KPICard label="Enterprise Value" value={fmtB(data.currentEV)} sub="Mkt Cap + Debt − Cash" />
              <KPICard label="Valuation" value={data.valuation || "—"} sub="vs. S&P 500 benchmark" color={valColor} />
            </div>

            {/* KPI Row 2 */}
            <div style={{ display: "flex", gap: 1, marginBottom: 20, background: "#1e3048" }}>
              <KPICard label="Intrinsic Value (DCF)" value={`$${(data.intrinsicValue || 0).toFixed(0)}`} sub={`WACC ${((data.wacc || 0) * 100).toFixed(1)}% · TGR ${((data.terminalGrowth || 0.03) * 100).toFixed(1)}%`} color="#ffd166" />
              <KPICard label="Current Price" value={`$${(data.currentPrice || 0).toFixed(2)}`} sub={`Analyst target $${(data.analystTarget || 0).toFixed(0)}`} />
              <KPICard label={`${data.ticker} Total Return`} value={`+${(lastComp - 100).toFixed(0)}%`} sub={`$100 → $${lastComp.toFixed(0)}`} color="#00e676" />
              <KPICard label="S&P 500 Total Return" value={`+${(lastSP - 100).toFixed(0)}%`} sub={`$100 → $${lastSP.toFixed(0)}`} color="#ff6b35" />
              <KPICard
                label="Alpha vs S&P 500"
                value={fmtPct((lastComp - lastSP) * 0.6, 0)}
                sub="Cumulative outperformance"
                color={(lastComp - lastSP) >= 0 ? "#00e676" : "#ff3d5a"}
              />
            </div>

            {/* Charts row 1 */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 12 }}>
              <ChartPanel title="Cumulative Return ($100 in 2010)" meta={`${data.ticker} vs S&P 500`}>
                <div style={{ display: "flex", gap: 12, marginBottom: 6 }}>
                  {[{ c: "#00d4ff", l: data.ticker }, { c: "#ff6b35", l: "S&P 500" }].map(x => (
                    <div key={x.l} style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 9, color: "#4a6a8a" }}>
                      <div style={{ width: 8, height: 8, borderRadius: "50%", background: x.c }} />
                      {x.l}
                    </div>
                  ))}
                </div>
                <LineChart
                  labels={years.map(String)}
                  datasets={[
                    { data: compCumul, color: "#00d4ff" },
                    { data: spCumul, color: "#ff6b35", dash: true },
                  ]}
                />
              </ChartPanel>

              <ChartPanel title="FCF / EV Yield (%)" meta="Higher = More attractive">
                <LineChart
                  labels={years.map(String)}
                  datasets={[{ data: fcfEV.map(v => v != null ? parseFloat((v * 100).toFixed(3)) : null), color: "#ffd166" }]}
                />
              </ChartPanel>
            </div>

            {/* Charts row 2 */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 12 }}>
              <ChartPanel title={`Annual FCF ($B)`} meta="Free Cash Flow">
                <BarChart data={fcf} labels={years.map(String)} color={v => v >= 0 ? "rgba(0,230,118,0.75)" : "rgba(255,61,90,0.75)"} unit="B" />
              </ChartPanel>

              <ChartPanel title="Enterprise Value ($B)" meta="Market Cap + Debt − Cash">
                <LineChart
                  labels={years.map(String)}
                  datasets={[{ data: ev, color: "#00d4ff" }]}
                />
              </ChartPanel>
            </div>

            {/* Annual returns bar */}
            <div style={{ background: "#0d1520", border: "1px solid #1e3048", padding: 16, marginBottom: 12 }}>
              <div style={{ fontSize: 9, letterSpacing: 2, textTransform: "uppercase", color: "#00d4ff", marginBottom: 10 }}>
                Annual Returns (%) — {data.ticker} vs S&P 500
              </div>
              <div style={{ display: "flex", alignItems: "flex-end", gap: 2, height: 120 }}>
                {years.map((yr, i) => {
                  const cr = compRet[i] ?? 0;
                  const sr = sp500[i] ?? 0;
                  const maxAbs = Math.max(...years.map((_, j) => Math.max(Math.abs(compRet[j] ?? 0), Math.abs(sp500[j] ?? 0))), 1);
                  const h = (v) => Math.max(Math.abs(v) / maxAbs * 95, 2);
                  return (
                    <div key={yr} style={{ flex: 1, display: "flex", alignItems: "flex-end", justifyContent: "center", gap: 1, height: "100%" }}>
                      <div title={`${yr} ${data.ticker}: ${fmtPct(cr)}`} style={{ flex: 1, height: h(cr) + "%", background: cr >= 0 ? "rgba(0,212,255,0.7)" : "rgba(255,61,90,0.7)", cursor: "default" }} />
                      <div title={`${yr} S&P 500: ${fmtPct(sr)}`} style={{ flex: 1, height: h(sr) + "%", background: sr >= 0 ? "rgba(255,107,53,0.55)" : "rgba(255,107,53,0.3)", cursor: "default" }} />
                    </div>
                  );
                })}
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", marginTop: 4 }}>
                {years.filter((_, i) => i % 3 === 0).map(yr => (
                  <span key={yr} style={{ fontSize: 8, color: "#4a6a8a" }}>{yr}</span>
                ))}
              </div>
            </div>

            {/* Data table */}
            <div style={{ background: "#0d1520", border: "1px solid #1e3048", marginBottom: 12, overflowX: "auto" }}>
              <div style={{ padding: "12px 16px", borderBottom: "1px solid #1e3048", display: "flex", justifyContent: "space-between" }}>
                <span style={{ fontSize: 9, letterSpacing: 2, textTransform: "uppercase", color: "#00d4ff" }}>Annual Data Table — {data.ticker} vs S&P 500</span>
                <span style={{ fontSize: 9, color: "#4a6a8a" }}>All $ in Billions</span>
              </div>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 11 }}>
                <thead>
                  <tr style={{ background: "#111c2c" }}>
                    {["Year", "FCF ($B)", "EV ($B)", "FCF/EV %", "FCF Growth", `${data.ticker} Ret`, "S&P 500", "Delta"].map(h => (
                      <th key={h} style={{ textAlign: h === "Year" ? "left" : "right", padding: "8px 14px", fontSize: 9, letterSpacing: 1.5, textTransform: "uppercase", color: "#4a6a8a", borderBottom: "1px solid #1e3048", fontWeight: 400 }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {years.map((yr, i) => {
                    const fg = data.fcfGrowth?.[i];
                    const cr = compRet[i];
                    const sr = sp500[i];
                    const delta = cr != null && sr != null ? cr - sr : null;
                    const fe = fcfEV[i];
                    return (
                      <tr key={yr} style={{ borderBottom: "1px solid rgba(30,48,72,0.4)" }}>
                        <td style={{ padding: "7px 14px", color: "#00d4ff", fontWeight: 700 }}>{yr}</td>
                        <td style={{ padding: "7px 14px", textAlign: "right", color: colorOf(fcf[i]) }}>{fmtB(fcf[i])}</td>
                        <td style={{ padding: "7px 14px", textAlign: "right" }}>{fmtB(ev[i])}</td>
                        <td style={{ padding: "7px 14px", textAlign: "right", color: "#ffd166", fontWeight: 700 }}>{fe != null ? (fe * 100).toFixed(2) + "%" : "—"}</td>
                        <td style={{ padding: "7px 14px", textAlign: "right", color: colorOf(fg) }}>{fmtPct(fg)}</td>
                        <td style={{ padding: "7px 14px", textAlign: "right", color: colorOf(cr) }}>{fmtPct(cr)}</td>
                        <td style={{ padding: "7px 14px", textAlign: "right", color: colorOf(sr) }}>{fmtPct(sr)}</td>
                        <td style={{ padding: "7px 14px", textAlign: "right", color: colorOf(delta), fontWeight: 700 }}>{fmtPct(delta)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Analysis */}
            <div style={{ background: "#0d1520", border: "1px solid #1e3048", padding: 18, marginBottom: 12 }}>
              <div style={{ fontSize: 9, letterSpacing: 2, textTransform: "uppercase", color: "#ff6b35", marginBottom: 12 }}>
                AI Analysis · {data.ticker}
              </div>
              <div style={{ fontSize: 12, lineHeight: 1.8, color: "#c8dff0", whiteSpace: "pre-wrap" }}>
                {data.description}
                {data.keyInsight && `\n\n📊 ${data.keyInsight}`}
              </div>
            </div>

            <div style={{ fontSize: 9, color: "#4a6a8a", textAlign: "center", padding: 12, opacity: 0.6 }}>
              AI-generated estimates for educational purposes only. Not financial advice. Verify all figures independently.
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
