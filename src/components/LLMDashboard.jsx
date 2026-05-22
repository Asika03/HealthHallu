import { useState, useMemo } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Cell, ComposedChart,
  LineChart, Line, RadarChart, Radar, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis,
} from "recharts";

// ─── THEME ────────────────────────────────────────────────────────────────────
const T = {
  bg:      "#f0f4f8",
  surface: "#ffffff",
  border:  "#e2e8f0",
  border2: "#cbd5e1",
  text:    "#0f172a",
  muted:   "#64748b",
  dim:     "#94a3b8",
  accent:  "#6366f1",
  green:   "#16a34a",
  red:     "#dc2626",
  orange:  "#d97706",
  purple:  "#7c3aed",
  cyan:    "#0284c7",
  font:    "'Inter','Segoe UI',sans-serif",
};

// ─── DATA ─────────────────────────────────────────────────────────────────────
const RATES_DATA = [
  { model:"LLaMA_4_Scout_17B",   label:"LLaMA 4 Scout",  total:230, correct:66,  partial:23, hallucinated:18,  refusal:61,  error:62,  valid:107, hallucination_rate:0.1682, accuracy_rate:0.6168, response_rate:0.7304 },
  { model:"MiniMax_M2_5",        label:"MiniMax M2.5",   total:230, correct:51,  partial:10, hallucinated:15,  refusal:47,  error:107, valid:76,  hallucination_rate:0.1974, accuracy_rate:0.6711, response_rate:0.5348 },
  { model:"Allam_2_7B",          label:"Allam 2 7B",     total:230, correct:69,  partial:19, hallucinated:25,  refusal:117, error:0,   valid:113, hallucination_rate:0.2212, accuracy_rate:0.6106, response_rate:1.0000 },
  { model:"LLaMA_3_3_70B",       label:"LLaMA 3.3 70B",  total:230, correct:78,  partial:22, hallucinated:31,  refusal:37,  error:62,  valid:131, hallucination_rate:0.2366, accuracy_rate:0.5954, response_rate:0.7304 },
  { model:"LLaMA_3_1_8B",        label:"LLaMA 3.1 8B",   total:230, correct:49,  partial:22, hallucinated:29,  refusal:68,  error:62,  valid:100, hallucination_rate:0.2900, accuracy_rate:0.4900, response_rate:0.7304 },
  { model:"OpenAI_OSS_120B",     label:"OSS 120B",        total:230, correct:77,  partial:16, hallucinated:38,  refusal:36,  error:63,  valid:131, hallucination_rate:0.2901, accuracy_rate:0.5878, response_rate:0.7261 },
  { model:"Free_Router",         label:"Free Router",     total:230, correct:41,  partial:12, hallucinated:27,  refusal:20,  error:130, valid:80,  hallucination_rate:0.3375, accuracy_rate:0.5125, response_rate:0.4348 },
  { model:"OpenAI_OSS_20B_OR",   label:"OSS 20B-OR",      total:230, correct:46,  partial:23, hallucinated:48,  refusal:27,  error:86,  valid:117, hallucination_rate:0.4103, accuracy_rate:0.3932, response_rate:0.6261 },
  { model:"Owl_Alpha",           label:"Owl Alpha",       total:230, correct:72,  partial:14, hallucinated:61,  refusal:19,  error:64,  valid:147, hallucination_rate:0.4150, accuracy_rate:0.4898, response_rate:0.7217 },
  { model:"Groq_Compound",       label:"Groq Compound",   total:230, correct:9,   partial:1,  hallucinated:17,  refusal:200, error:3,   valid:27,  hallucination_rate:0.6296, accuracy_rate:0.3333, response_rate:0.1304 },
  { model:"Groq_Compound_Mini",  label:"Groq Mini",       total:230, correct:7,   partial:2,  hallucinated:18,  refusal:201, error:2,   valid:27,  hallucination_rate:0.6667, accuracy_rate:0.2593, response_rate:0.1261 },
  { model:"NVIDIA_Nemotron_120B",label:"Nemotron 120B",   total:230, correct:1,   partial:1,  hallucinated:7,   refusal:8,   error:213, valid:9,   hallucination_rate:0.7778, accuracy_rate:0.1111, response_rate:0.0739 },
  { model:"LiquidAI_Instruct",   label:"LiquidAI",        total:230, correct:0,   partial:1,  hallucinated:9,   refusal:7,   error:213, valid:10,  hallucination_rate:0.9000, accuracy_rate:0.0000, response_rate:0.0739 },
  { model:"Qwen3_32B",           label:"Qwen3 32B",       total:230, correct:0,   partial:0,  hallucinated:99,  refusal:69,  error:62,  valid:99,  hallucination_rate:1.0000, accuracy_rate:0.0000, response_rate:0.7304 },
];

const CATEGORY_DATA = [
  { model:"LLaMA_3_3_70B",       category:"Disease Stats", hallucination_rate:0.5625, accuracy_rate:0.1563, valid_attempts:32 },
  { model:"LLaMA_3_3_70B",       category:"Mortality",     hallucination_rate:0.1961, accuracy_rate:0.6275, valid_attempts:51 },
  { model:"LLaMA_3_3_70B",       category:"Healthcare",    hallucination_rate:0.1154, accuracy_rate:0.6923, valid_attempts:26 },
  { model:"LLaMA_3_3_70B",       category:"Vaccination",   hallucination_rate:0.0000, accuracy_rate:0.8333, valid_attempts:12 },
  { model:"LLaMA_3_3_70B",       category:"Historical",    hallucination_rate:0.0000, accuracy_rate:1.0000, valid_attempts:10 },
  { model:"LLaMA_3_1_8B",        category:"Disease Stats", hallucination_rate:1.0000, accuracy_rate:0.0000, valid_attempts:9  },
  { model:"LLaMA_3_1_8B",        category:"Mortality",     hallucination_rate:0.2222, accuracy_rate:0.4889, valid_attempts:45 },
  { model:"LLaMA_3_1_8B",        category:"Healthcare",    hallucination_rate:0.3750, accuracy_rate:0.3125, valid_attempts:16 },
  { model:"LLaMA_3_1_8B",        category:"Vaccination",   hallucination_rate:0.2857, accuracy_rate:0.4286, valid_attempts:7  },
  { model:"LLaMA_3_1_8B",        category:"Historical",    hallucination_rate:0.1304, accuracy_rate:0.6522, valid_attempts:23 },
  { model:"LLaMA_4_Scout_17B",   category:"Disease Stats", hallucination_rate:0.1429, accuracy_rate:0.6190, valid_attempts:21 },
  { model:"LLaMA_4_Scout_17B",   category:"Mortality",     hallucination_rate:0.1852, accuracy_rate:0.6111, valid_attempts:54 },
  { model:"LLaMA_4_Scout_17B",   category:"Healthcare",    hallucination_rate:0.0000, accuracy_rate:0.8000, valid_attempts:15 },
  { model:"LLaMA_4_Scout_17B",   category:"Vaccination",   hallucination_rate:0.0000, accuracy_rate:0.8000, valid_attempts:5  },
  { model:"LLaMA_4_Scout_17B",   category:"Historical",    hallucination_rate:0.3333, accuracy_rate:0.5833, valid_attempts:12 },
  { model:"Qwen3_32B",           category:"Disease Stats", hallucination_rate:1.0000, accuracy_rate:0.0000, valid_attempts:18 },
  { model:"Qwen3_32B",           category:"Mortality",     hallucination_rate:1.0000, accuracy_rate:0.0000, valid_attempts:52 },
  { model:"Qwen3_32B",           category:"Healthcare",    hallucination_rate:1.0000, accuracy_rate:0.0000, valid_attempts:14 },
  { model:"Qwen3_32B",           category:"Vaccination",   hallucination_rate:1.0000, accuracy_rate:0.0000, valid_attempts:8  },
  { model:"Qwen3_32B",           category:"Historical",    hallucination_rate:1.0000, accuracy_rate:0.0000, valid_attempts:7  },
  { model:"OpenAI_OSS_120B",     category:"Disease Stats", hallucination_rate:0.3500, accuracy_rate:0.4500, valid_attempts:20 },
  { model:"OpenAI_OSS_120B",     category:"Mortality",     hallucination_rate:0.2642, accuracy_rate:0.5849, valid_attempts:53 },
  { model:"OpenAI_OSS_120B",     category:"Healthcare",    hallucination_rate:0.2500, accuracy_rate:0.6000, valid_attempts:20 },
  { model:"OpenAI_OSS_120B",     category:"Vaccination",   hallucination_rate:0.1429, accuracy_rate:0.7143, valid_attempts:7  },
  { model:"OpenAI_OSS_120B",     category:"Historical",    hallucination_rate:0.1333, accuracy_rate:0.7333, valid_attempts:15 },
  { model:"Owl_Alpha",           category:"Disease Stats", hallucination_rate:0.6000, accuracy_rate:0.2400, valid_attempts:25 },
  { model:"Owl_Alpha",           category:"Mortality",     hallucination_rate:0.3684, accuracy_rate:0.4561, valid_attempts:57 },
  { model:"Owl_Alpha",           category:"Healthcare",    hallucination_rate:0.3500, accuracy_rate:0.4500, valid_attempts:20 },
  { model:"Owl_Alpha",           category:"Vaccination",   hallucination_rate:0.2857, accuracy_rate:0.5714, valid_attempts:7  },
  { model:"Owl_Alpha",           category:"Historical",    hallucination_rate:0.2632, accuracy_rate:0.6316, valid_attempts:19 },
  { model:"Allam_2_7B",          category:"Disease Stats", hallucination_rate:0.2941, accuracy_rate:0.5294, valid_attempts:34 },
  { model:"Allam_2_7B",          category:"Mortality",     hallucination_rate:0.1538, accuracy_rate:0.6731, valid_attempts:52 },
  { model:"Allam_2_7B",          category:"Healthcare",    hallucination_rate:0.1538, accuracy_rate:0.6923, valid_attempts:13 },
  { model:"Allam_2_7B",          category:"Vaccination",   hallucination_rate:0.1667, accuracy_rate:0.6667, valid_attempts:6  },
  { model:"Allam_2_7B",          category:"Historical",    hallucination_rate:0.3750, accuracy_rate:0.5000, valid_attempts:8  },
  { model:"MiniMax_M2_5",        category:"Disease Stats", hallucination_rate:0.2353, accuracy_rate:0.5882, valid_attempts:17 },
  { model:"MiniMax_M2_5",        category:"Mortality",     hallucination_rate:0.1481, accuracy_rate:0.6667, valid_attempts:27 },
  { model:"MiniMax_M2_5",        category:"Healthcare",    hallucination_rate:0.2000, accuracy_rate:0.6000, valid_attempts:10 },
  { model:"MiniMax_M2_5",        category:"Vaccination",   hallucination_rate:0.0000, accuracy_rate:1.0000, valid_attempts:4  },
  { model:"MiniMax_M2_5",        category:"Historical",    hallucination_rate:0.2222, accuracy_rate:0.5556, valid_attempts:9  },
  { model:"Free_Router",         category:"Disease Stats", hallucination_rate:0.8889, accuracy_rate:0.0556, valid_attempts:18 },
  { model:"Free_Router",         category:"Mortality",     hallucination_rate:0.2333, accuracy_rate:0.5333, valid_attempts:30 },
  { model:"Free_Router",         category:"Healthcare",    hallucination_rate:0.0556, accuracy_rate:0.7222, valid_attempts:18 },
  { model:"Free_Router",         category:"Vaccination",   hallucination_rate:0.0000, accuracy_rate:0.7778, valid_attempts:9  },
  { model:"Free_Router",         category:"Historical",    hallucination_rate:0.6000, accuracy_rate:0.2000, valid_attempts:5  },
  { model:"OpenAI_OSS_20B_OR",   category:"Disease Stats", hallucination_rate:0.9737, accuracy_rate:0.0263, valid_attempts:38 },
  { model:"OpenAI_OSS_20B_OR",   category:"Mortality",     hallucination_rate:0.1795, accuracy_rate:0.5897, valid_attempts:39 },
  { model:"OpenAI_OSS_20B_OR",   category:"Healthcare",    hallucination_rate:0.1500, accuracy_rate:0.6000, valid_attempts:20 },
  { model:"OpenAI_OSS_20B_OR",   category:"Vaccination",   hallucination_rate:0.0000, accuracy_rate:0.8182, valid_attempts:11 },
  { model:"OpenAI_OSS_20B_OR",   category:"Historical",    hallucination_rate:0.1111, accuracy_rate:0.6667, valid_attempts:9  },
  { model:"Groq_Compound",       category:"Disease Stats", hallucination_rate:0.6296, accuracy_rate:0.3333, valid_attempts:27 },
  { model:"Groq_Compound_Mini",  category:"Disease Stats", hallucination_rate:0.7200, accuracy_rate:0.2400, valid_attempts:25 },
  { model:"Groq_Compound_Mini",  category:"Mortality",     hallucination_rate:0.0000, accuracy_rate:0.5000, valid_attempts:2  },
  { model:"NVIDIA_Nemotron_120B",category:"Historical",    hallucination_rate:0.7778, accuracy_rate:0.1111, valid_attempts:9  },
  { model:"LiquidAI_Instruct",   category:"Disease Stats", hallucination_rate:1.0000, accuracy_rate:0.0000, valid_attempts:1  },
  { model:"LiquidAI_Instruct",   category:"Historical",    hallucination_rate:0.8889, accuracy_rate:0.1111, valid_attempts:9  },
];

const ALL_CATEGORIES = ["Disease Stats","Mortality","Healthcare","Vaccination","Historical"];
const PIE_COLORS = ["#3b82f6","#06b6d4","#10b981","#f59e0b","#ef4444","#8b5cf6","#0ea5e9","#84cc16","#f97316","#ec4899","#14b8a6","#a855f7","#6366f1","#22c55e"];

const pct  = v => (v == null || isNaN(v)) ? "—" : `${(v*100).toFixed(1)}%`;
const hCol = v => v <= 0.25 ? T.green : v <= 0.5 ? T.orange : T.red;
const aCol = v => v >= 0.6  ? T.green : v >= 0.35 ? T.orange : T.red;

// ─── SHARED UI ────────────────────────────────────────────────────────────────
const TT = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background:T.surface, border:`1px solid ${T.border2}`, borderRadius:6, padding:"8px 12px", fontSize:11, fontFamily:T.font, boxShadow:"0 8px 24px rgba(0,0,0,0.5)" }}>
      <div style={{ fontWeight:700, color:T.text, marginBottom:5, letterSpacing:"0.02em" }}>{label}</div>
      {payload.map((p,i) => (
        <div key={i} style={{ color:T.muted, display:"flex", justifyContent:"space-between", gap:14 }}>
          <span>{p.name}</span>
          <b style={{ color:T.text }}>{typeof p.value==="number"?(p.value<=1&&p.value>=0?pct(p.value):p.value):p.value}</b>
        </div>
      ))}
    </div>
  );
};

const PieLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, value }) => {
  const R = Math.PI/180, r = innerRadius+(outerRadius-innerRadius)*0.5;
  const x = cx+r*Math.cos(-midAngle*R), y = cy+r*Math.sin(-midAngle*R);
  if (value < 30) return null;
  return <text x={x} y={y} fill="#fff" textAnchor="middle" dominantBaseline="central" fontSize={9} fontWeight={700} fontFamily={T.font}>{value}</text>;
};

const Card = ({ children, style={} }) => (
  <div style={{ background:T.surface, borderRadius:8, border:`1px solid ${T.border}`, display:"flex", flexDirection:"column", overflow:"hidden", ...style }}>
    {children}
  </div>
);

const CH = ({ title, sub }) => (
  <div style={{ padding:"8px 12px 4px", borderBottom:`1px solid ${T.border}` }}>
    <div style={{ display:"flex", alignItems:"baseline", gap:6 }}>
      <span style={{ fontSize:9, fontWeight:700, color:T.text, textTransform:"uppercase", letterSpacing:"0.1em", fontFamily:T.font }}>{title}</span>
      {sub && <span style={{ fontSize:8, color:T.muted, fontFamily:T.font }}>/ {sub}</span>}
    </div>
  </div>
);

// ─── CUSTOM TOOLTIPS ─────────────────────────────────────────────────────────
const ReliabilityTT = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const name = payload[0]?.payload?.name;
  const score = payload[0]?.value;
  const row = RATES_DATA.find(d => d.label === name);
  if (!row) return null;
  return (
    <div style={{ background:T.surface, border:`1px solid ${T.border2}`, borderRadius:6, padding:"8px 12px", fontSize:11, fontFamily:T.font, boxShadow:"0 4px 16px rgba(0,0,0,0.12)", minWidth:180 }}>
      <div style={{ fontWeight:700, color:T.text, marginBottom:6 }}>{name}</div>
      {[
        ["Reliability Score", `${score > 0 ? "+" : ""}${(score*100).toFixed(1)}%`, score >= 0.3 ? T.green : score >= 0 ? T.orange : T.red],
        ["Accuracy Rate",     `${(row.accuracy_rate*100).toFixed(1)}%`,             T.green],
        ["Hallucination Rate",`${(row.hallucination_rate*100).toFixed(1)}%`,        T.red],
        ["Response Rate",     `${(row.response_rate*100).toFixed(1)}%`,             T.cyan],
      ].map(([l,v,c]) => (
        <div key={l} style={{ display:"flex", justifyContent:"space-between", gap:14, marginBottom:2 }}>
          <span style={{ color:T.muted }}>{l}</span>
          <b style={{ color:c }}>{v}</b>
        </div>
      ))}
    </div>
  );
};

const ConsistencyTT = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const name = payload[0]?.payload?.name;
  const score = payload[0]?.value;
  const row = RATES_DATA.find(d => d.label === name);
  if (!row) return null;
  const cats = CATEGORY_DATA.filter(c => c.model === row.model && c.valid_attempts > 0);
  const catMap = Object.fromEntries(cats.map(c => [c.category, c.hallucination_rate]));
  const catLabels = ["Disease Stats","Mortality","Healthcare","Vaccination","Historical"];
  return (
    <div style={{ background:T.surface, border:`1px solid ${T.border2}`, borderRadius:6, padding:"8px 12px", fontSize:11, fontFamily:T.font, boxShadow:"0 4px 16px rgba(0,0,0,0.12)", minWidth:200 }}>
      <div style={{ fontWeight:700, color:T.text, marginBottom:6 }}>{name}</div>
      <div style={{ display:"flex", justifyContent:"space-between", gap:14, marginBottom:5 }}>
        <span style={{ color:T.muted }}>Consistency Score</span>
        <b style={{ color: score >= 80 ? T.green : score >= 60 ? T.orange : T.red }}>{score?.toFixed(1)}%</b>
      </div>
      <div style={{ borderTop:`1px solid ${T.border}`, paddingTop:5, marginTop:2 }}>
        <div style={{ fontSize:9, color:T.dim, marginBottom:4, textTransform:"uppercase", letterSpacing:"0.06em" }}>Hallucination by Category</div>
        {catLabels.map(cat => {
          const val = catMap[cat];
          return (
            <div key={cat} style={{ display:"flex", justifyContent:"space-between", gap:14, marginBottom:2 }}>
              <span style={{ color:T.muted, fontSize:10 }}>{cat}</span>
              <b style={{ color: val == null ? T.dim : val <= 0.25 ? T.green : val <= 0.5 ? T.orange : T.red, fontSize:10 }}>
                {val == null ? "—" : `${(val*100).toFixed(0)}%`}
              </b>
            </div>
          );
        })}
      </div>
    </div>
  );
};
export default function Dashboard() {
  const [tab, setTab]       = useState(0);
  const [selCat, setSelCat] = useState("Disease Stats");

  const totalValid = RATES_DATA.reduce((s,d)=>s+d.valid,0);
  const avgHalluc  = RATES_DATA.reduce((s,d)=>s+d.hallucination_rate,0)/RATES_DATA.length;
  const avgAcc     = RATES_DATA.reduce((s,d)=>s+d.accuracy_rate,0)/RATES_DATA.length;

  const validModels = RATES_DATA.filter(d=>!isNaN(d.hallucination_rate));
  const bestModel   = [...validModels].sort((a,b)=>(a.hallucination_rate-2*a.accuracy_rate)-(b.hallucination_rate-2*b.accuracy_rate))[0];
  const worstModel  = [...validModels].sort((a,b)=>(b.hallucination_rate-2*b.accuracy_rate)-(a.hallucination_rate-2*a.accuracy_rate))[0];

  const catFiltered = useMemo(()=>
    CATEGORY_DATA.filter(d=>d.category===selCat&&d.valid_attempts>0)
      .map(d=>({ ...d, label:RATES_DATA.find(r=>r.model===d.model)?.label||d.model }))
      .sort((a,b)=>a.hallucination_rate-b.hallucination_rate),
    [selCat]);

  const pieData = useMemo(()=>
    RATES_DATA.filter(d=>d.valid>0).sort((a,b)=>b.valid-a.valid).map(d=>({ name:d.label, value:d.valid })),
    []);

  const lineData = RATES_DATA.map(d=>({ name:d.label, hallucination_rate:d.hallucination_rate, accuracy_rate:d.accuracy_rate }));

  const radarData = useMemo(()=>{
    if (!bestModel) return [];
    const catRow = CATEGORY_DATA.find(d=>d.model===bestModel.model&&d.category===selCat);
    const accVal  = catRow ? +(catRow.accuracy_rate*100).toFixed(1) : +(bestModel.accuracy_rate*100).toFixed(1);
    const hallVal = catRow ? catRow.hallucination_rate : bestModel.hallucination_rate;
    return [
      { metric:"Accuracy",      value: accVal },
      { metric:"Response",      value: +(bestModel.response_rate*100).toFixed(1) },
      { metric:"Safety",        value: +((1-hallVal)*100).toFixed(1) },
      { metric:"Reliability",   value: +(bestModel.correct/bestModel.total*100).toFixed(1) },
      { metric:"Hallucination", value: +(hallVal*100).toFixed(1) },
    ];
  }, [bestModel, selCat]);

  // ── shared axis/grid props ──
  const axisProps = { tick:{ fill:T.muted, fontSize:8, fontFamily:T.font }, axisLine:false, tickLine:false };
  const gridProps = { strokeDasharray:"3 3", stroke:T.dim };

  // ── header ──
  const Header = () => (
    <>
      <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", height:44 }}>
        <div style={{ display:"flex", alignItems:"center", gap:12 }}>
          <div style={{ width:3, height:22, background:T.accent, borderRadius:2 }} />
          <div>
            <div style={{ fontSize:15, fontWeight:700, color:T.text, letterSpacing:"0.02em", fontFamily:T.font }}>LLM RELIABILITY ANALYSIS DASHBOARD</div>
          </div>
        </div>
        <div style={{ display:"flex", alignItems:"center", gap:10 }}>
          {/* TABS */}
          <div style={{ display:"flex", background:T.surface, border:`1px solid ${T.border}`, borderRadius:6, padding:3, gap:2 }}>
            {["OVERVIEW","MODEL ANALYSIS"].map((t,i)=>(
              <button key={i} onClick={()=>setTab(i)} style={{
                padding:"4px 14px", borderRadius:4, border:"none", cursor:"pointer",
                fontSize:9, fontWeight:700, fontFamily:T.font, letterSpacing:"0.08em",
                background: tab===i ? T.accent : "transparent",
                color: tab===i ? "#fff" : T.muted,
                transition:"all 0.15s",
              }}>{t}</button>
            ))}
          </div>
          {/* CATEGORY DROPDOWN */}
          {tab===0 && (
            <div style={{ display:"flex", alignItems:"center", gap:6 }}>
              <span style={{ fontSize:8, color:T.muted, fontWeight:700, letterSpacing:"0.1em", textTransform:"uppercase", fontFamily:T.font }}>CATEGORY</span>
              <select value={selCat} onChange={e=>setSelCat(e.target.value)} style={{
                background:T.surface, color:T.text, border:`1.5px solid ${T.accent}`,
                borderRadius:5, padding:"4px 26px 4px 9px", fontSize:10, fontWeight:700,
                fontFamily:T.font, cursor:"pointer", outline:"none", minWidth:130,
                appearance:"none",
                backgroundImage:`url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='2.5'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E")`,
                backgroundRepeat:"no-repeat", backgroundPosition:"right 7px center",
              }}>
                {ALL_CATEGORIES.map(c=><option key={c} value={c}>{c}</option>)}
              </select>
            </div>
          )}
        </div>
      </div>

      {/* KPI CARDS */}
      <div style={{ display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:6, height:62 }}>
        {[
          { label:"TOTAL QUESTIONS",     value:"230",                        sub:"per model",          accent:T.accent  },
          { label:"TOTAL VALID ATTEMPTS",value:totalValid.toLocaleString(),  sub:"all 14 models",      accent:T.cyan    },
          { label:"AVG HALLUCINATION",   value:pct(avgHalluc),               sub:"across all models",  accent:T.red     },
          { label:"AVG ACCURACY",        value:pct(avgAcc),                  sub:"across all models",  accent:T.green   },
        ].map((k,i)=>(
          <div key={i} style={{ background:T.surface, borderRadius:6, border:`1px solid ${T.border}`, borderLeft:`3px solid ${k.accent}`, padding:"6px 10px" }}>
            <div style={{ fontSize:7, color:T.muted, letterSpacing:"0.1em", marginBottom:2, fontFamily:T.font }}>{k.label}</div>
            <div style={{ fontSize:17, fontWeight:700, color:k.accent, lineHeight:1.1, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap", fontFamily:T.font }}>{k.value}</div>
            <div style={{ fontSize:7, color:T.dim, marginTop:1, fontFamily:T.font }}>{k.sub}</div>
          </div>
        ))}
      </div>
    </>
  );

  // ════════════════════════════════════════════════════════════════════════════
  // TAB 0 — OVERVIEW
  // ════════════════════════════════════════════════════════════════════════════

  // ── Novel metrics computed from RATES_DATA + CATEGORY_DATA ──
  // Category Consistency: 1 - std_dev(hallucination_rate across categories per model)
  const consistencyData = useMemo(() => {
    return RATES_DATA.map(d => {
      const cats = CATEGORY_DATA.filter(c => c.model === d.model && c.valid_attempts > 0);
      if (cats.length < 2) return { name: d.label, consistency: null };
      const rates = cats.map(c => c.hallucination_rate);
      const mean  = rates.reduce((s,v) => s+v, 0) / rates.length;
      const std   = Math.sqrt(rates.reduce((s,v) => s + (v-mean)**2, 0) / rates.length);
      return { name: d.label, consistency: +((1 - std) * 100).toFixed(1) };
    }).filter(d => d.consistency !== null).sort((a,b) => b.consistency - a.consistency);
  }, []);

  // Refusal Intelligence: refusal / (refusal + hallucinated)
  // High = model knows its limits; Low = model fabricates instead of refusing
  const refusalIntelData = useMemo(() => {
    return RATES_DATA.map(d => {
      const denom = d.refusal + d.hallucinated;
      const ri = denom > 0 ? +((d.refusal / denom) * 100).toFixed(1) : 0;
      return { name: d.label, ri };
    }).sort((a,b) => b.ri - a.ri);
  }, []);

  const Tab0 = () => (
    <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gridTemplateRows:"2fr 1fr", gap:8, flex:1, minHeight:0 }}>

      {/* COL 1: Multivariate bar chart — Hallucination + Accuracy side by side per model */}
      <Card style={{ minHeight:0 }}>
        <CH title="Hallucination vs Accuracy Rate" sub={selCat} />
        <div style={{ flex:1, minHeight:0, padding:"4px 8px 8px 0" }}>
          {catFiltered.length === 0
            ? <div style={{ color:T.muted, fontSize:11, padding:16 }}>No data for this category</div>
            : <ResponsiveContainer width="100%" height="100%">
                <BarChart data={catFiltered} margin={{ left:-4, right:8, top:6, bottom:32 }}>
                  <CartesianGrid {...gridProps} vertical={false} />
                  <XAxis dataKey="label" {...axisProps} angle={-28} textAnchor="end" interval={0} />
                  <YAxis {...axisProps} tickFormatter={v=>`${(v*100).toFixed(0)}%`} domain={[0,1]} />
                  <Tooltip content={<TT />} cursor={{ fill:"rgba(99,102,241,0.04)" }} />
                  <Legend
                    formatter={v=><span style={{ fontSize:8, color:T.muted, fontFamily:T.font }}>{v}</span>}
                    wrapperStyle={{ paddingTop:2 }}
                  />
                  <Bar dataKey="hallucination_rate" name="Hallucination" radius={[3,3,0,0]} barSize={10} fill={T.red} opacity={0.85} />
                  <Bar dataKey="accuracy_rate"      name="Accuracy"      radius={[3,3,0,0]} barSize={10} fill={T.green} opacity={0.85} />
                </BarChart>
              </ResponsiveContainer>
          }
        </div>
      </Card>

      {/* COL 2: Category Consistency Score — line graph */}
      <Card style={{ minHeight:0 }}>
        <CH title="Category Consistency Score" />
        <div style={{ flex:1, minHeight:0, padding:"4px 8px 8px 0" }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={consistencyData} margin={{ left:-4, right:12, top:8, bottom:32 }}>
              <CartesianGrid {...gridProps} vertical={false} />
              <XAxis dataKey="name" {...axisProps} angle={-28} textAnchor="end" interval={0} />
              <YAxis {...axisProps} tickFormatter={v=>`${v.toFixed(0)}%`} domain={[0,100]} />
              <Tooltip content={<ConsistencyTT />} />
              <Line type="monotone" dataKey="consistency" name="Consistency Score"
                stroke={T.accent} strokeWidth={2.5}
                dot={(props) => {
                  const c = props.payload.consistency;
                  const col = c >= 80 ? T.green : c >= 60 ? T.orange : T.red;
                  return <circle key={props.key} cx={props.cx} cy={props.cy} r={4} fill={col} stroke="#fff" strokeWidth={1.5} />;
                }}
                activeDot={{ r:6, stroke:"#fff", strokeWidth:2 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* COL 3: Refusal Intelligence Score — line graph */}
      <Card style={{ minHeight:0 }}>
        <CH title="Refusal Intelligence Score" />
        <div style={{ flex:1, minHeight:0, padding:"4px 8px 8px 0" }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={refusalIntelData} margin={{ left:-4, right:12, top:8, bottom:32 }}>
              <CartesianGrid {...gridProps} vertical={false} />
              <XAxis dataKey="name" {...axisProps} angle={-28} textAnchor="end" interval={0} />
              <YAxis {...axisProps} tickFormatter={v=>`${v.toFixed(0)}%`} domain={[0,100]} />
              <Tooltip content={<TT />} formatter={v=>[`${v.toFixed(1)}%`,"Refusal Intelligence"]} />
              <Line type="monotone" dataKey="ri" name="Refusal Intelligence"
                stroke={T.purple} strokeWidth={2.5}
                dot={(props) => {
                  const c = props.payload.ri;
                  const col = c >= 70 ? T.green : c >= 40 ? T.orange : T.red;
                  return <circle key={props.key} cx={props.cx} cy={props.cy} r={4} fill={col} stroke="#fff" strokeWidth={1.5} />;
                }}
                activeDot={{ r:6, stroke:"#fff", strokeWidth:2 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* BOTTOM ROW: full-width insights panel */}
      <div style={{ gridColumn:"1 / 4", background:T.surface, borderRadius:8, border:`1px solid ${T.border}`, padding:"8px 14px", overflow:"hidden" }}>
        <div style={{ fontSize:8, fontWeight:700, color:T.text, textTransform:"uppercase", letterSpacing:"0.1em", marginBottom:7 }}>
          What These Charts Tell You
        </div>
        <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:14 }}>

          {/* Chart 1 insight */}
          <div>
            <div style={{ fontSize:8, fontWeight:600, color:T.accent, textTransform:"uppercase", letterSpacing:"0.08em", marginBottom:3 }}>
              Hallucination vs Accuracy — {selCat}
            </div>
            <div style={{ fontSize:10, color:T.muted, lineHeight:1.5 }}>
              Compares how often each model fabricates a wrong answer against how often it answers correctly — filtered to the selected category.
              A model with low hallucination and high accuracy is reliable for that topic.
              Wide gaps between the two bars indicate inconsistent behaviour within the category.
            </div>
            {catFiltered.length > 0 && (() => {
              const best = [...catFiltered].sort((a,b) => a.hallucination_rate - b.hallucination_rate)[0];
              const worst = [...catFiltered].sort((a,b) => b.hallucination_rate - a.hallucination_rate)[0];
              return (
                <div style={{ marginTop:8, display:"flex", gap:8 }}>
                  <span style={{ fontSize:9, background:"#f0fdf4", color:T.green, border:"1px solid #bbf7d0", borderRadius:4, padding:"2px 8px" }}>
                    Best: {best.label} ({(best.hallucination_rate*100).toFixed(0)}% halluc)
                  </span>
                  <span style={{ fontSize:9, background:"#fef2f2", color:T.red, border:"1px solid #fecaca", borderRadius:4, padding:"2px 8px" }}>
                    Worst: {worst.label} ({(worst.hallucination_rate*100).toFixed(0)}% halluc)
                  </span>
                </div>
              );
            })()}
          </div>

          {/* Chart 2 insight */}
          <div>
            <div style={{ fontSize:8, fontWeight:600, color:T.accent, textTransform:"uppercase", letterSpacing:"0.08em", marginBottom:3 }}>
              Category Consistency Score
            </div>
            <div style={{ fontSize:10, color:T.muted, lineHeight:1.5 }}>
              Measures how stable a model's hallucination rate is across all categories.
              A high score means the model performs similarly on Disease Stats, Mortality, Healthcare, Vaccination and Historical questions.
              A low score means the model is unpredictable — reliable on some topics but unreliable on others.
            </div>
            {consistencyData.length > 0 && (() => {
              const top = consistencyData[0];
              const bot = consistencyData[consistencyData.length - 1];
              return (
                <div style={{ marginTop:8, display:"flex", gap:8 }}>
                  <span style={{ fontSize:9, background:"#f0fdf4", color:T.green, border:"1px solid #bbf7d0", borderRadius:4, padding:"2px 8px" }}>
                    Most consistent: {top.name} ({top.consistency.toFixed(0)}%)
                  </span>
                  <span style={{ fontSize:9, background:"#fef2f2", color:T.red, border:"1px solid #fecaca", borderRadius:4, padding:"2px 8px" }}>
                    Least: {bot.name} ({bot.consistency.toFixed(0)}%)
                  </span>
                </div>
              );
            })()}
          </div>

          {/* Chart 3 insight */}
          <div>
            <div style={{ fontSize:9, fontWeight:600, color:T.accent, textTransform:"uppercase", letterSpacing:"0.08em", marginBottom:5 }}>
              Refusal Intelligence Score
            </div>
            <div style={{ fontSize:11, color:T.muted, lineHeight:1.6 }}>
              When a model doesn't know the answer, does it refuse or does it fabricate?
              A high score means the model correctly declines to answer rather than inventing statistics.
              In health contexts this is critical — a model that says "I don't know" is safer than one that confidently gives a wrong death toll.
            </div>
            {refusalIntelData.length > 0 && (() => {
              const top = refusalIntelData[0];
              const bot = refusalIntelData[refusalIntelData.length - 1];
              return (
                <div style={{ marginTop:8, display:"flex", gap:8 }}>
                  <span style={{ fontSize:9, background:"#f0fdf4", color:T.green, border:"1px solid #bbf7d0", borderRadius:4, padding:"2px 8px" }}>
                    Safest: {top.name} ({top.ri.toFixed(0)}%)
                  </span>
                  <span style={{ fontSize:9, background:"#fef2f2", color:T.red, border:"1px solid #fecaca", borderRadius:4, padding:"2px 8px" }}>
                    Riskiest: {bot.name} ({bot.ri.toFixed(0)}%)
                  </span>
                </div>
              );
            })()}
          </div>

        </div>
      </div>

    </div>
  );

  // ════════════════════════════════════════════════════════════════════════════
  // TAB 1 — MODEL ANALYSIS
  // ════════════════════════════════════════════════════════════════════════════
  const Tab1 = () => (
    <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:8, flex:1, minHeight:0 }}>

      {/* COL 1: Hallucination line */}
      <Card style={{ minHeight:0 }}>
        <CH title="Model vs Hallucination Rate" sub="all models" />
        <div style={{ flex:1, minHeight:0, padding:"4px 6px 8px 0" }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={lineData} margin={{ left:-16, right:8, top:6, bottom:22 }}>
              <CartesianGrid {...gridProps} />
              <XAxis dataKey="name" {...axisProps} angle={-30} textAnchor="end" interval={0} tick={{ fill:T.dim, fontSize:6, fontFamily:T.font }} />
              <YAxis {...axisProps} tickFormatter={v=>`${(v*100).toFixed(0)}%`} domain={[0,1]} />
              <Tooltip content={<TT />} />
              <Line type="monotone" dataKey="hallucination_rate" name="Hallucination Rate" stroke={T.red} strokeWidth={2}
                dot={{ r:3, fill:T.red, stroke:T.bg, strokeWidth:1.5 }} activeDot={{ r:5 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* COL 2: Accuracy line */}
      <Card style={{ minHeight:0 }}>
        <CH title="Model vs Accuracy Rate" sub="all models" />
        <div style={{ flex:1, minHeight:0, padding:"4px 6px 8px 0" }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={lineData} margin={{ left:-16, right:8, top:6, bottom:22 }}>
              <CartesianGrid {...gridProps} />
              <XAxis dataKey="name" {...axisProps} angle={-30} textAnchor="end" interval={0} tick={{ fill:T.dim, fontSize:6, fontFamily:T.font }} />
              <YAxis {...axisProps} tickFormatter={v=>`${(v*100).toFixed(0)}%`} domain={[0,1]} />
              <Tooltip content={<TT />} />
              <Line type="monotone" dataKey="accuracy_rate" name="Accuracy Rate" stroke={T.green} strokeWidth={2}
                dot={{ r:3, fill:T.green, stroke:T.bg, strokeWidth:1.5 }} activeDot={{ r:5 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* COL 3: Score graph (accuracy - hallucination) */}
      <Card style={{ minHeight:0 }}>
        <CH title="Model Reliability Score" sub="accuracy − hallucination rate" />
        <div style={{ flex:1, minHeight:0, padding:"4px 8px 8px 0" }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={[...RATES_DATA]
                .map(d => ({
                  name: d.label,
                  score: +(d.accuracy_rate - d.hallucination_rate).toFixed(4),
                }))
                .sort((a,b) => b.score - a.score)}
              layout="vertical"
              margin={{ left:4, right:36, top:4, bottom:4 }}
            >
              <CartesianGrid {...gridProps} horizontal={false} />
              <XAxis type="number" {...axisProps}
                tickFormatter={v => v > 0 ? `+${(v*100).toFixed(0)}%` : `${(v*100).toFixed(0)}%`}
                domain={[-1, 1]}
              />
              <YAxis type="category" dataKey="name" {...axisProps}
                tick={{ fill:T.muted, fontSize:8 }} width={80} />
              <Tooltip
                content={<ReliabilityTT />}
                cursor={{ fill:"rgba(99,102,241,0.05)" }}
              />
              <Bar dataKey="score" name="Reliability Score" radius={[0,4,4,0]} barSize={12}>
                {[...RATES_DATA]
                  .map(d => d.accuracy_rate - d.hallucination_rate)
                  .sort((a,b) => b - a)
                  .map((v, i) => (
                    <Cell key={i} fill={v >= 0.3 ? T.green : v >= 0 ? T.orange : T.red} />
                  ))
                }
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* ROW 2: Best + Worst spanning all 3 cols */}
      <div style={{ gridColumn:"1/-1", alignSelf:"start", display:"grid", gridTemplateColumns:"1fr 1fr", gap:8 }}>
        {[
          { label:"BEST MODEL",  m:bestModel,  accent:T.green, bg:"#f0fdf4", border:"#86efac",
            reason:"Lowest hallucination with highest accuracy on health & disease Q&A." },
          { label:"WORST MODEL", m:worstModel, accent:T.red,   bg:"#fef2f2", border:"#fca5a5",
            reason:"Highest hallucination rate with lowest accuracy — unreliable for health queries." },
        ].map((b,i)=>(
          <div key={i} style={{ background:b.bg, border:`1.5px solid ${b.border}`, borderLeft:`3px solid ${b.accent}`, borderRadius:8, padding:"7px 14px", display:"flex", alignItems:"center", justifyContent:"space-between" }}>
            <div style={{ minWidth:0, flex:1 }}>
              <div style={{ fontSize:8, color:b.accent, fontWeight:700, letterSpacing:"0.1em", textTransform:"uppercase", marginBottom:2 }}>{b.label}</div>
              <div style={{ fontSize:12, fontWeight:700, color:T.text, whiteSpace:"nowrap", overflow:"hidden", textOverflow:"ellipsis" }}>{b.m?.label}</div>
              <div style={{ fontSize:9, color:T.muted, marginTop:2, lineHeight:1.4 }}>{b.reason}</div>
            </div>
            <div style={{ display:"flex", gap:12, marginLeft:12, flexShrink:0 }}>
              {[["HALLUC", b.m?.hallucination_rate, b.accent],["ACCURACY", b.m?.accuracy_rate, T.green],["RESPONSE", b.m?.response_rate, T.cyan]].map(([l,v,c])=>(
                <div key={l} style={{ textAlign:"center" }}>
                  <div style={{ fontSize:13, fontWeight:700, color:c }}>{pct(v)}</div>
                  <div style={{ fontSize:7, color:T.muted, textTransform:"uppercase", letterSpacing:"0.06em" }}>{l}</div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  // ── render ──
  return (
    <div style={{
      width:"100vw", height:"100vh", overflow:"hidden",
      background:T.bg, fontFamily:T.font,
      display:"flex", flexDirection:"column",
      padding:"10px 16px", gap:7, boxSizing:"border-box",
    }}>
      <Header />
      {tab===0 ? <Tab0 /> : <Tab1 />}
    </div>
  );
}
