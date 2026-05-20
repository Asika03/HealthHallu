import { useState, useMemo } from "react";
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell
} from "recharts";

const RATES_DATA = [
  { model: "LLaMA_4_Scout_17B",   total: 230, correct: 66,  partial: 23, hallucinated: 18,  refusal: 61,  error: 62,  valid: 107, hallucination_rate: 0.1682, accuracy_rate: 0.6168, response_rate: 0.7304 },
  { model: "MiniMax_M2_5",        total: 230, correct: 51,  partial: 10, hallucinated: 15,  refusal: 47,  error: 107, valid: 76,  hallucination_rate: 0.1974, accuracy_rate: 0.6711, response_rate: 0.5348 },
  { model: "Allam_2_7B",          total: 230, correct: 69,  partial: 19, hallucinated: 25,  refusal: 117, error: 0,   valid: 113, hallucination_rate: 0.2212, accuracy_rate: 0.6106, response_rate: 1.0000 },
  { model: "LLaMA_3_3_70B",       total: 230, correct: 78,  partial: 22, hallucinated: 31,  refusal: 37,  error: 62,  valid: 131, hallucination_rate: 0.2366, accuracy_rate: 0.5954, response_rate: 0.7304 },
  { model: "LLaMA_3_1_8B",        total: 230, correct: 49,  partial: 22, hallucinated: 29,  refusal: 68,  error: 62,  valid: 100, hallucination_rate: 0.2900, accuracy_rate: 0.4900, response_rate: 0.7304 },
  { model: "OpenAI_OSS_120B",     total: 230, correct: 77,  partial: 16, hallucinated: 38,  refusal: 36,  error: 63,  valid: 131, hallucination_rate: 0.2901, accuracy_rate: 0.5878, response_rate: 0.7261 },
  { model: "Free_Router",         total: 230, correct: 41,  partial: 12, hallucinated: 27,  refusal: 20,  error: 130, valid: 80,  hallucination_rate: 0.3375, accuracy_rate: 0.5125, response_rate: 0.4348 },
  { model: "OpenAI_OSS_20B_OR",   total: 230, correct: 46,  partial: 23, hallucinated: 48,  refusal: 27,  error: 86,  valid: 117, hallucination_rate: 0.4103, accuracy_rate: 0.3932, response_rate: 0.6261 },
  { model: "Owl_Alpha",           total: 230, correct: 72,  partial: 14, hallucinated: 61,  refusal: 19,  error: 64,  valid: 147, hallucination_rate: 0.4150, accuracy_rate: 0.4898, response_rate: 0.7217 },
  { model: "Groq_Compound",       total: 230, correct: 9,   partial: 1,  hallucinated: 17,  refusal: 200, error: 3,   valid: 27,  hallucination_rate: 0.6296, accuracy_rate: 0.3333, response_rate: 0.1304 },
  { model: "Groq_Compound_Mini",  total: 230, correct: 7,   partial: 2,  hallucinated: 18,  refusal: 201, error: 2,   valid: 27,  hallucination_rate: 0.6667, accuracy_rate: 0.2593, response_rate: 0.1261 },
  { model: "NVIDIA_Nemotron_120B",total: 230, correct: 1,   partial: 1,  hallucinated: 7,   refusal: 8,   error: 213, valid: 9,   hallucination_rate: 0.7778, accuracy_rate: 0.1111, response_rate: 0.0739 },
  { model: "LiquidAI_Instruct",   total: 230, correct: 0,   partial: 1,  hallucinated: 9,   refusal: 7,   error: 213, valid: 10,  hallucination_rate: 0.9000, accuracy_rate: 0.0000, response_rate: 0.0739 },
  { model: "Qwen3_32B",           total: 230, correct: 0,   partial: 0,  hallucinated: 99,  refusal: 69,  error: 62,  valid: 99,  hallucination_rate: 1.0000, accuracy_rate: 0.0000, response_rate: 0.7304 },
];

const CATEGORY_DATA = [
  { model: "LLaMA_3_3_70B",      category: "Disease Stats",   hallucination_rate: 0.5625, valid_attempts: 32 },
  { model: "LLaMA_3_3_70B",      category: "Mortality",       hallucination_rate: 0.1961, valid_attempts: 51 },
  { model: "LLaMA_3_3_70B",      category: "Healthcare",      hallucination_rate: 0.1154, valid_attempts: 26 },
  { model: "LLaMA_3_3_70B",      category: "Vaccination",     hallucination_rate: 0.0000, valid_attempts: 12 },
  { model: "LLaMA_3_3_70B",      category: "Historical",      hallucination_rate: 0.0000, valid_attempts: 10 },
  { model: "LLaMA_3_1_8B",       category: "Disease Stats",   hallucination_rate: 1.0000, valid_attempts: 9  },
  { model: "LLaMA_3_1_8B",       category: "Mortality",       hallucination_rate: 0.2222, valid_attempts: 45 },
  { model: "LLaMA_3_1_8B",       category: "Healthcare",      hallucination_rate: 0.3750, valid_attempts: 16 },
  { model: "LLaMA_3_1_8B",       category: "Vaccination",     hallucination_rate: 0.2857, valid_attempts: 7  },
  { model: "LLaMA_3_1_8B",       category: "Historical",      hallucination_rate: 0.1304, valid_attempts: 23 },
  { model: "LLaMA_4_Scout_17B",  category: "Disease Stats",   hallucination_rate: 0.1429, valid_attempts: 21 },
  { model: "LLaMA_4_Scout_17B",  category: "Mortality",       hallucination_rate: 0.1852, valid_attempts: 54 },
  { model: "LLaMA_4_Scout_17B",  category: "Healthcare",      hallucination_rate: 0.0000, valid_attempts: 15 },
  { model: "LLaMA_4_Scout_17B",  category: "Vaccination",     hallucination_rate: 0.0000, valid_attempts: 5  },
  { model: "LLaMA_4_Scout_17B",  category: "Historical",      hallucination_rate: 0.3333, valid_attempts: 12 },
  { model: "Qwen3_32B",          category: "Disease Stats",   hallucination_rate: 1.0000, valid_attempts: 18 },
  { model: "Qwen3_32B",          category: "Mortality",       hallucination_rate: 1.0000, valid_attempts: 52 },
  { model: "Qwen3_32B",          category: "Healthcare",      hallucination_rate: 1.0000, valid_attempts: 14 },
  { model: "Qwen3_32B",          category: "Vaccination",     hallucination_rate: 1.0000, valid_attempts: 8  },
  { model: "Qwen3_32B",          category: "Historical",      hallucination_rate: 1.0000, valid_attempts: 7  },
  { model: "OpenAI_OSS_120B",    category: "Disease Stats",   hallucination_rate: 0.3500, valid_attempts: 20 },
  { model: "OpenAI_OSS_120B",    category: "Mortality",       hallucination_rate: 0.2642, valid_attempts: 53 },
  { model: "OpenAI_OSS_120B",    category: "Healthcare",      hallucination_rate: 0.2500, valid_attempts: 20 },
  { model: "OpenAI_OSS_120B",    category: "Vaccination",     hallucination_rate: 0.1429, valid_attempts: 7  },
  { model: "OpenAI_OSS_120B",    category: "Historical",      hallucination_rate: 0.1333, valid_attempts: 15 },
  { model: "Owl_Alpha",          category: "Disease Stats",   hallucination_rate: 0.6000, valid_attempts: 25 },
  { model: "Owl_Alpha",          category: "Mortality",       hallucination_rate: 0.3684, valid_attempts: 57 },
  { model: "Owl_Alpha",          category: "Healthcare",      hallucination_rate: 0.3500, valid_attempts: 20 },
  { model: "Owl_Alpha",          category: "Vaccination",     hallucination_rate: 0.2857, valid_attempts: 7  },
  { model: "Owl_Alpha",          category: "Historical",      hallucination_rate: 0.2632, valid_attempts: 19 },
  { model: "Allam_2_7B",         category: "Disease Stats",   hallucination_rate: 0.2941, valid_attempts: 34 },
  { model: "Allam_2_7B",         category: "Mortality",       hallucination_rate: 0.1538, valid_attempts: 52 },
  { model: "Allam_2_7B",         category: "Healthcare",      hallucination_rate: 0.1538, valid_attempts: 13 },
  { model: "Allam_2_7B",         category: "Vaccination",     hallucination_rate: 0.1667, valid_attempts: 6  },
  { model: "Allam_2_7B",         category: "Historical",      hallucination_rate: 0.3750, valid_attempts: 8  },
  { model: "MiniMax_M2_5",       category: "Disease Stats",   hallucination_rate: 0.2353, valid_attempts: 17 },
  { model: "MiniMax_M2_5",       category: "Mortality",       hallucination_rate: 0.1481, valid_attempts: 27 },
  { model: "MiniMax_M2_5",       category: "Healthcare",      hallucination_rate: 0.2000, valid_attempts: 10 },
  { model: "MiniMax_M2_5",       category: "Vaccination",     hallucination_rate: 0.0000, valid_attempts: 4  },
  { model: "MiniMax_M2_5",       category: "Historical",      hallucination_rate: 0.2222, valid_attempts: 9  },

  // Free_Router
  { model: "Free_Router",        category: "Disease Stats",   hallucination_rate: 0.8889, valid_attempts: 18 },
  { model: "Free_Router",        category: "Mortality",       hallucination_rate: 0.2333, valid_attempts: 30 },
  { model: "Free_Router",        category: "Healthcare",      hallucination_rate: 0.0556, valid_attempts: 18 },
  { model: "Free_Router",        category: "Vaccination",     hallucination_rate: 0.0000, valid_attempts: 9  },
  { model: "Free_Router",        category: "Historical",      hallucination_rate: 0.6000, valid_attempts: 5  },

  // OpenAI_OSS_20B_OR
  { model: "OpenAI_OSS_20B_OR",  category: "Disease Stats",   hallucination_rate: 0.9737, valid_attempts: 38 },
  { model: "OpenAI_OSS_20B_OR",  category: "Mortality",       hallucination_rate: 0.1795, valid_attempts: 39 },
  { model: "OpenAI_OSS_20B_OR",  category: "Healthcare",      hallucination_rate: 0.1500, valid_attempts: 20 },
  { model: "OpenAI_OSS_20B_OR",  category: "Vaccination",     hallucination_rate: 0.0000, valid_attempts: 11 },
  { model: "OpenAI_OSS_20B_OR",  category: "Historical",      hallucination_rate: 0.1111, valid_attempts: 9  },

  // Groq_Compound — only Disease Stats had valid attempts
  { model: "Groq_Compound",      category: "Disease Stats",   hallucination_rate: 0.6296, valid_attempts: 27 },

  // Groq_Compound_Mini
  { model: "Groq_Compound_Mini", category: "Disease Stats",   hallucination_rate: 0.7200, valid_attempts: 25 },
  { model: "Groq_Compound_Mini", category: "Mortality",       hallucination_rate: 0.0000, valid_attempts: 2  },

  // NVIDIA_Nemotron_120B — only Historical had valid attempts
  { model: "NVIDIA_Nemotron_120B", category: "Historical",    hallucination_rate: 0.7778, valid_attempts: 9  },

  // LiquidAI_Instruct
  { model: "LiquidAI_Instruct",  category: "Disease Stats",   hallucination_rate: 1.0000, valid_attempts: 1  },
  { model: "LiquidAI_Instruct",  category: "Historical",      hallucination_rate: 0.8889, valid_attempts: 9  },
];

const STATUS_COLORS = {
  correct: "#22c55e", partial: "#3b82f6",
  hallucinated: "#ef4444", refusal: "#f59e0b", error: "#94a3b8",
};

const pct = (v) => v == null || isNaN(v) ? "—" : `${(v * 100).toFixed(1)}%`;
const rateColor = (v) => {
  if (v == null || isNaN(v)) return "#94a3b8";
  if (v <= 0.25) return "#16a34a";
  if (v <= 0.5)  return "#d97706";
  return "#dc2626";
};

const TT = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background:"#fff", border:"1px solid #e2e8f0", borderRadius:6, padding:"8px 12px", fontSize:11, boxShadow:"0 4px 12px rgba(0,0,0,0.08)" }}>
      <div style={{ fontWeight:700, color:"#1e293b", marginBottom:4 }}>{label}</div>
      {payload.map((p,i) => (
        <div key={i} style={{ color: p.color || "#475569" }}>
          {p.name}: <b>{typeof p.value === "number" ? (p.value > 1 ? p.value : pct(p.value)) : p.value}</b>
        </div>
      ))}
    </div>
  );
};

const Card = ({ children, style = {} }) => (
  <div style={{
    background: "#fff", borderRadius: 10, border: "1px solid #e2e8f0",
    boxShadow: "0 1px 4px rgba(0,0,0,0.05)", overflow: "hidden",
    display: "flex", flexDirection: "column", ...style
  }}>
    {children}
  </div>
);

const CardHeader = ({ children }) => (
  <div style={{ fontSize: 9, fontWeight: 700, color: "#94a3b8", letterSpacing: 2, textTransform: "uppercase", padding: "10px 12px 0 12px" }}>
    {children}
  </div>
);

export default function Dashboard() {
  const [selected, setSelected] = useState("LLaMA_4_Scout_17B");

  const sel = useMemo(() => RATES_DATA.find(d => d.model === selected) || RATES_DATA[0], [selected]);

  const catData = useMemo(() =>
    CATEGORY_DATA.filter(d => d.model === selected && d.valid_attempts > 0), [selected]);

  const statusBarData = [
    { status: "Correct",      count: sel.correct,      color: STATUS_COLORS.correct },
    { status: "Partial",      count: sel.partial,      color: STATUS_COLORS.partial },
    { status: "Hallucinated", count: sel.hallucinated, color: STATUS_COLORS.hallucinated },
    { status: "Refusal",      count: sel.refusal,      color: STATUS_COLORS.refusal },
    { status: "Error",        count: sel.error,        color: STATUS_COLORS.error },
  ];

  const validModels = RATES_DATA.filter(d => d.hallucination_rate != null && !isNaN(d.hallucination_rate));
  const bestModel  = [...validModels].sort((a,b) => (a.hallucination_rate - 2*a.accuracy_rate) - (b.hallucination_rate - 2*b.accuracy_rate))[0];
  const worstModel = [...validModels].sort((a,b) => (b.hallucination_rate - 2*b.accuracy_rate) - (a.hallucination_rate - 2*a.accuracy_rate))[0];

  const lineData = RATES_DATA.filter(d => d.valid > 0).map(d => ({
    name: d.model.replace(/_/g," ").slice(0,11),
    hallucination_rate: d.hallucination_rate,
    accuracy_rate: d.accuracy_rate,
    response_rate: d.response_rate,
    _full: d.model,
  }));

  const kpis = [
    { label: "Total Questions",      value: sel.total,                                    color: "#0f172a" },
    { label: "Total Valid Attempts",  value: RATES_DATA.reduce((s,d)=>s+d.valid,0),       color: "#0f172a" },
    { label: "Valid Attempts",        value: sel.valid,                                    color: "#0f172a" },
    { label: "Hallucination Rate",    value: pct(sel.hallucination_rate),                  color: rateColor(sel.hallucination_rate) },
    { label: "Accuracy Rate",         value: pct(sel.accuracy_rate),                       color: "#16a34a" },
    { label: "Response Rate",         value: pct(sel.response_rate),                       color: "#2563eb" },
  ];

  return (
    <div style={{
      width: "100vw", height: "100vh", overflow: "hidden",
      background: "#f1f5f9",
      fontFamily: "'IBM Plex Sans', 'Segoe UI', sans-serif",
      display: "grid",
      gridTemplateRows: "44px 72px 1fr 68px",
      gridTemplateColumns: "1fr",
      gap: 0,
      padding: "10px 14px",
      boxSizing: "border-box",
    }}>

      {/* ── ROW 1: HEADER ── */}
      <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", paddingBottom: 8 }}>
        <div style={{ display:"flex", alignItems:"center", gap:10 }}>
          <div style={{ width:3, height:20, background:"#2563eb", borderRadius:2 }} />
          <div>
            <div style={{ fontSize:9, color:"#94a3b8", letterSpacing:3, textTransform:"uppercase" }}>Real-Time Health & Disease Data</div>
            <div style={{ fontSize:16, fontWeight:700, color:"#0f172a", lineHeight:1.2 }}>LLM Reliability Analysis Dashboard</div>
          </div>
        </div>
        <div style={{ display:"flex", alignItems:"center", gap:8 }}>
          <span style={{ fontSize:10, color:"#64748b", fontWeight:600, letterSpacing:1, textTransform:"uppercase" }}>Model</span>
          <select
            value={selected}
            onChange={e => setSelected(e.target.value)}
            style={{
              background:"#fff", color:"#0f172a", border:"1.5px solid #cbd5e1",
              borderRadius:7, padding:"5px 10px", fontSize:12, fontWeight:600,
              cursor:"pointer", outline:"none", minWidth:170,
              boxShadow:"0 1px 3px rgba(0,0,0,0.06)"
            }}
          >
            {RATES_DATA.map(d => (
              <option key={d.model} value={d.model}>{d.model.replace(/_/g," ")}</option>
            ))}
          </select>
        </div>
      </div>

      {/* ── ROW 2: KPI CARDS ── */}
      <div style={{ display:"grid", gridTemplateColumns:"repeat(6,1fr)", gap:8, alignItems:"stretch" }}>
        {kpis.map((k,i) => (
          <Card key={i} style={{ padding:"8px 12px", justifyContent:"center" }}>
            <div style={{ fontSize:8, color:"#94a3b8", letterSpacing:2, textTransform:"uppercase", marginBottom:2 }}>{k.label}</div>
            <div style={{ fontSize:22, fontWeight:800, color:k.color, lineHeight:1 }}>{k.value}</div>
          </Card>
        ))}
      </div>

      {/* ── ROW 3: MAIN CHARTS ── */}
      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:8, minHeight:0, marginTop:8 }}>

        {/* Col 1: Response Status Horizontal Bar */}
        <Card>
          <CardHeader>Response Status — {selected.replace(/_/g," ")}</CardHeader>
          <div style={{ flex:1, minHeight:0, padding:"4px 4px 8px 0" }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={statusBarData} layout="vertical" margin={{ left:8, right:20, top:6, bottom:16 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
                <XAxis type="number" tick={{ fill:"#94a3b8", fontSize:9 }} axisLine={false} tickLine={false}
                  label={{ value:"Question Count", position:"insideBottom", offset:-4, fontSize:9, fill:"#94a3b8" }} />
                <YAxis type="category" dataKey="status" tick={{ fill:"#475569", fontSize:10, fontWeight:600 }} axisLine={false} tickLine={false} width={76} />
                <Tooltip content={<TT />} cursor={{ fill: "#f1f5f9" }} />
                <Bar dataKey="count" name="Question Count" radius={[0,5,5,0]} barSize={18}>
                  {statusBarData.map((d,i) => <Cell key={i} fill={d.color} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Col 2: Hallucination by Category */}
        <Card>
          <CardHeader>Hallucination Rate by Category</CardHeader>
          <div style={{ flex:1, minHeight:0, padding:"4px 4px 8px 0" }}>
            {catData.length === 0
              ? <div style={{ color:"#94a3b8", fontSize:12, padding:20 }}>No category data</div>
              : <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={catData} margin={{ left:-8, right:8, bottom:36, top:6 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="category" tick={{ fill:"#94a3b8", fontSize:8 }} angle={-25} textAnchor="end" interval={0} />
                    <YAxis tick={{ fill:"#94a3b8", fontSize:9 }} tickFormatter={v=>`${(v*100).toFixed(0)}%`} />
                    <Tooltip content={<TT />} />
                    <Bar dataKey="hallucination_rate" name="Hallucination Rate" radius={[5,5,0,0]} barSize={24}>
                      {catData.map((d,i) => <Cell key={i} fill={rateColor(d.hallucination_rate)} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
            }
          </div>
        </Card>

        {/* Col 3: Three stacked line charts */}
        <div style={{ display:"flex", flexDirection:"column", gap:8, minHeight:0 }}>
          {[
            { key:"hallucination_rate", label:"Model vs Hallucination Rate", color:"#ef4444" },
            { key:"accuracy_rate",      label:"Model vs Accuracy Rate",      color:"#22c55e" },
            { key:"response_rate",      label:"Model vs Response Rate",      color:"#3b82f6" },
          ].map(({ key, label, color }) => (
            <Card key={key} style={{ flex:1, minHeight:0 }}>
              <CardHeader>{label}</CardHeader>
              <div style={{ flex:1, minHeight:0, padding:"2px 4px 6px 0" }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={lineData} margin={{ left:-20, right:6, top:4, bottom:16 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f8fafc" />
                    <XAxis dataKey="name" tick={{ fill:"#cbd5e1", fontSize:6 }} angle={-30} textAnchor="end" interval={0} />
                    <YAxis tick={{ fill:"#94a3b8", fontSize:8 }} tickFormatter={v=>`${(v*100).toFixed(0)}%`} domain={[0,1]} />
                    <Tooltip content={<TT />} />
                    <Line type="monotone" dataKey={key} name={label} stroke={color} strokeWidth={1.5}
                      dot={(props) => {
                        const isSel = props.payload._full === selected;
                        return <circle key={props.key} cx={props.cx} cy={props.cy} r={isSel?4:2} fill={isSel?"#fff":color} stroke={color} strokeWidth={isSel?2:1} />;
                      }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* ── ROW 4: BEST / WORST ── */}
      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:8, marginTop:8 }}>
        {[
          { badge:"Best Model",  m: bestModel,  bg:"#f0fdf4", border:"#86efac", lc:"#16a34a", mc:"#16a34a", reason:"Lowest hallucination with highest accuracy on health & disease Q&A" },
          { badge:"Worst Model", m: worstModel, bg:"#fef2f2", border:"#fca5a5", lc:"#dc2626", mc:"#dc2626", reason:"Highest hallucination rate with lowest accuracy — unreliable for health queries" },
        ].map((b,i) => (
          <div key={i} style={{
            background:b.bg, border:`1.5px solid ${b.border}`, borderRadius:10,
            padding:"8px 16px", display:"flex", alignItems:"center", justifyContent:"space-between"
          }}>
            <div>
              <div style={{ fontSize:8, color:b.lc, fontWeight:800, letterSpacing:3, textTransform:"uppercase", marginBottom:2 }}>{b.badge}</div>
              <div style={{ fontSize:14, fontWeight:800, color:"#0f172a", lineHeight:1.2 }}>{b.m?.model.replace(/_/g," ")}</div>
              <div style={{ fontSize:9, color:"#64748b", marginTop:2 }}>{b.reason}</div>
            </div>
            <div style={{ display:"flex", gap:14, textAlign:"center" }}>
              {[["Hallucination", b.m?.hallucination_rate], ["Accuracy", b.m?.accuracy_rate], ["Response", b.m?.response_rate]].map(([lbl,val]) => (
                <div key={lbl}>
                  <div style={{ fontSize:15, fontWeight:800, color:b.mc }}>{pct(val)}</div>
                  <div style={{ fontSize:8, color:"#94a3b8", textTransform:"uppercase", letterSpacing:1 }}>{lbl}</div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

    </div>
  );
}
