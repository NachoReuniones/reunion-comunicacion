import json, datetime

with open('C:/Users/usuario/OneDrive/Escritorio/CLAUDE/ventas_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

data_js = json.dumps(data, ensure_ascii=False)
today = datetime.date.today().strftime('%d/%m/%Y')

html = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Luctron – Dashboard de Ventas</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',Arial,sans-serif;background:#eef1f6;color:#1a202c;font-size:14px}
header{background:linear-gradient(135deg,#1a365d 0%,#2b6cb0 100%);color:#fff;padding:18px 32px;display:flex;align-items:center;justify-content:space-between}
header h1{font-size:22px;font-weight:700;letter-spacing:.5px}
header .sub{font-size:12px;opacity:.75;margin-top:3px}
.note-tc{font-size:11px;background:#fff3cd;border-left:3px solid #f0b429;padding:6px 16px;margin:0}
.filters{background:#fff;border-bottom:1px solid #e2e8f0;padding:12px 32px;display:flex;align-items:center;gap:20px;flex-wrap:wrap}
.filter-group{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.filter-label{font-size:12px;font-weight:600;color:#4a5568;white-space:nowrap}
.year-btn{padding:4px 11px;border:1.5px solid #cbd5e0;border-radius:4px;background:#fff;cursor:pointer;font-size:12px;color:#4a5568;transition:all .15s}
.vend-btn{padding:4px 10px;border:1.5px solid #cbd5e0;border-radius:4px;background:#fff;cursor:pointer;font-size:12px;color:#4a5568;transition:all .15s}
.main{padding:20px 32px;display:grid;gap:20px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:16px}
.kpi{background:#fff;border-radius:10px;padding:18px 20px;box-shadow:0 1px 4px rgba(0,0,0,.08);border-left:4px solid #e2e8f0}
.kpi.ok{border-left-color:#276749}
.kpi.warn{border-left-color:#c05621}
.kpi.info{border-left-color:#2b6cb0}
.kpi-label{font-size:11px;font-weight:600;color:#718096;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px}
.kpi-value{font-size:26px;font-weight:700;color:#1a365d;line-height:1}
.kpi.ok .kpi-value{color:#276749}
.kpi.warn .kpi-value{color:#c05621}
.kpi-sub{font-size:11px;color:#718096;margin-top:5px}
.progress-bar{height:5px;background:#e2e8f0;border-radius:3px;margin-top:8px;overflow:hidden}
.progress-fill{height:100%;border-radius:3px;transition:width .4s}
.section{background:#fff;border-radius:10px;padding:20px;box-shadow:0 1px 4px rgba(0,0,0,.08)}
.section-title{font-size:14px;font-weight:700;color:#2d3748;margin-bottom:14px;display:flex;align-items:center;gap:8px}
.section-title .sub{font-size:11px;font-weight:400;color:#718096}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.legend{display:flex;flex-wrap:wrap;gap:14px;margin-top:8px}
.legend-item{display:flex;align-items:center;gap:5px;font-size:12px;color:#4a5568}
.legend-dot{width:12px;height:12px;border-radius:2px;flex-shrink:0}
table{width:100%;border-collapse:collapse;font-size:12px}
th{background:#f7fafc;padding:8px 12px;text-align:right;font-weight:600;color:#4a5568;border-bottom:2px solid #e2e8f0;white-space:nowrap}
th:first-child{text-align:left}
td{padding:7px 12px;text-align:right;border-bottom:1px solid #f0f0f0;color:#2d3748}
td:first-child{text-align:left;font-weight:500}
tr:last-child td{font-weight:700;background:#f7fafc}
tr:hover:not(:last-child) td{background:#f7fafc}
@media(max-width:800px){.grid-2{grid-template-columns:1fr}.filters{padding:10px 16px}.main{padding:14px 16px}}
</style>
</head>
<body>
<header>
  <div>
    <h1>&#9889; Luctron Led Lighting</h1>
    <div class="sub">Dashboard de Ventas &middot; Actualizado """ + today + """</div>
  </div>
  <div style="text-align:right;font-size:12px;opacity:.85">
    Target mensual: <strong>USD 215.000</strong><br>
    Historial: 2020 &ndash; 2026
  </div>
</header>
<div class="note-tc">&#x26A0; Las ventas en ARS se convierten a USD usando TC BNA oficial hist&oacute;rico mensual. Las facturas en USD se toman directamente.</div>

<div class="filters">
  <div class="filter-group">
    <span class="filter-label">A&ntilde;o:</span>
    <div id="year-filters" style="display:flex;gap:6px;flex-wrap:wrap"></div>
  </div>
  <div class="filter-group">
    <span class="filter-label">Vendedor:</span>
    <div id="vend-filters" style="display:flex;gap:6px;flex-wrap:wrap"></div>
  </div>
</div>

<div class="main">
  <div class="kpis" id="kpis"></div>

  <div class="section">
    <div class="section-title">Facturaci&oacute;n mensual <span class="sub" id="monthly-sub"></span></div>
    <div id="monthly-chart"></div>
    <div class="legend" id="monthly-legend"></div>
  </div>

  <div class="grid-2">
    <div class="section">
      <div class="section-title">Por vendedor <span class="sub" id="vend-sub"></span></div>
      <div id="vendor-chart"></div>
    </div>
    <div class="section">
      <div class="section-title">Evoluci&oacute;n anual</div>
      <div id="annual-chart"></div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">Detalle mensual (USD)</div>
    <div id="monthly-table" style="overflow-x:auto"></div>
  </div>
</div>

<script>
const VENTAS = """ + data_js + """;

const TC = {
  '2020-1':63,'2020-2':64,'2020-3':66,'2020-4':67,'2020-5':68,'2020-6':70,
  '2020-7':73,'2020-8':74,'2020-9':76,'2020-10':79,'2020-11':81,'2020-12':84,
  '2021-1':85,'2021-2':88,'2021-3':91,'2021-4':93,'2021-5':96,'2021-6':98,
  '2021-7':100,'2021-8':102,'2021-9':99,'2021-10':100,'2021-11':102,'2021-12':104,
  '2022-1':107,'2022-2':108,'2022-3':111,'2022-4':114,'2022-5':121,'2022-6':126,
  '2022-7':131,'2022-8':137,'2022-9':145,'2022-10':155,'2022-11':163,'2022-12':176,
  '2023-1':188,'2023-2':196,'2023-3':205,'2023-4':214,'2023-5':239,'2023-6':263,
  '2023-7':268,'2023-8':350,'2023-9':350,'2023-10':354,'2023-11':368,'2023-12':800,
  '2024-1':810,'2024-2':843,'2024-3':868,'2024-4':874,'2024-5':906,'2024-6':935,
  '2024-7':974,'2024-8':995,'2024-9':1007,'2024-10':1022,'2024-11':1048,'2024-12':1005,
  '2025-1':1060,'2025-2':1072,'2025-3':1080,'2025-4':1150,'2025-5':1200,'2025-6':1250,
  '2025-7':1290,'2025-8':1320,'2025-9':1350,'2025-10':1380,'2025-11':1395,'2025-12':1400,
  '2026-1':1410,'2026-2':1430,'2026-3':1450,'2026-4':1470,'2026-5':1490
};

const TARGET = 215000;
const MONTHS = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
const YEAR_COLORS = {
  2020:'#a0aec0',2021:'#90cdf4',2022:'#9ae6b4',
  2023:'#fbd38d',2024:'#fc8181',2025:'#2b6cb0',2026:'#805ad5'
};
const VEND_LABELS = {
  'INX2 ILUMINACION SA':'INX2 / Nacho',
  'ANIBAL CASOY':'Anibal Casoy',
  'FACUNDO OROZA':'Facundo Oroza',
  'FEDERICO CAFFARELLI':'Federico Caffarelli',
  'LUCAS LUNA':'Lucas Luna',
  'ARIEL FLORES':'Ariel Flores',
  'SUELEM':'Suelem',
  'MARCOS GOMEZ':'Marcos Gomez',
  'OSCAR NOGUERA':'Oscar Noguera',
  'PABLO DRAGHI':'Pablo Draghi',
  'GRISEL FERNANDEZ':'Grisel Fernandez'
};
const VEND_COLORS = ['#2b6cb0','#276749','#c05621','#6b46c1','#b7791f','#2c7a7b','#c53030','#2f855a','#553c9a','#744210','#1a365d'];
const ALL_YEARS = [2020,2021,2022,2023,2024,2025,2026];
const ALL_VENDORS = [...new Set(VENTAS.map(r=>r.vendedor).filter(Boolean))].sort();

let selYears = new Set([2024,2025]);
let selVendors = new Set(ALL_VENDORS);

function toUSD(r){
  if(r.moneda==='DL') return r.total;
  return r.total / (TC[r.anio+'-'+r.mes]||1000);
}
function fmtK(v){
  if(v>=1e6) return '$'+(v/1e6).toFixed(2)+'M';
  if(v>=1e3) return '$'+(v/1e3).toFixed(0)+'K';
  return '$'+v.toFixed(0);
}
function fmtFull(v){ return '$'+Math.round(v).toLocaleString('es-AR'); }
function pct(v,t){ return t>0?Math.round(v/t*100):0; }

function getFiltered(){ return VENTAS.filter(r=>selYears.has(r.anio)&&selVendors.has(r.vendedor)); }

function monthlyByYear(){
  const res={};
  selYears.forEach(y=>{ res[y]=new Array(12).fill(0); });
  getFiltered().forEach(r=>{ if(res[r.anio]) res[r.anio][r.mes-1]+=toUSD(r); });
  return res;
}

function vendorTotals(){
  const res={};
  getFiltered().forEach(r=>{ res[r.vendedor]=(res[r.vendedor]||0)+toUSD(r); });
  return res;
}

function annualTotals(){
  const res={};
  ALL_YEARS.forEach(y=>res[y]=0);
  VENTAS.filter(r=>selVendors.has(r.vendedor)).forEach(r=>{
    res[r.anio]=(res[r.anio]||0)+toUSD(r);
  });
  return res;
}

// SVG bar chart (grouped, monthly)
function svgBarChart(monthly){
  const W=820,H=280,PL=72,PR=30,PT=15,PB=42;
  const CW=W-PL-PR, CH=H-PT-PB;
  const years=[...selYears].sort();
  const allVals=years.flatMap(y=>monthly[y]||[]);
  const maxVal=Math.max(...allVals,TARGET)*1.12||1;
  const nY=years.length;
  const groupW=CW/12;
  const barW=Math.min(groupW*0.75/nY,28);
  const barGap=(groupW-barW*nY)*0.5;
  let svg=`<svg viewBox="0 0 ${W} ${H}" width="100%">`;
  for(let i=0;i<=5;i++){
    const y=PT+CH*(1-i/5), v=maxVal*i/5;
    svg+=`<line x1="${PL}" y1="${y.toFixed(1)}" x2="${W-PR}" y2="${y.toFixed(1)}" stroke="#e2e8f0" stroke-width="1"/>`;
    svg+=`<text x="${PL-6}" y="${(y+4).toFixed(1)}" text-anchor="end" font-size="10" fill="#718096">${fmtK(v)}</text>`;
  }
  years.forEach((yr,yi)=>{
    const vals=monthly[yr]||new Array(12).fill(0);
    vals.forEach((v,mi)=>{
      if(!v) return;
      const bh=(v/maxVal)*CH;
      const x=PL+mi*groupW+barGap+yi*barW;
      const y=PT+CH-bh;
      svg+=`<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${barW.toFixed(1)}" height="${bh.toFixed(1)}" fill="${YEAR_COLORS[yr]||'#2b6cb0'}" rx="2" opacity=".88"><title>${yr} ${MONTHS[mi]}: ${fmtFull(v)}</title></rect>`;
    });
  });
  // Target line
  const ty=PT+CH*(1-TARGET/maxVal);
  svg+=`<line x1="${PL}" y1="${ty.toFixed(1)}" x2="${W-PR}" y2="${ty.toFixed(1)}" stroke="#e53e3e" stroke-width="1.5" stroke-dasharray="6,3"/>`;
  svg+=`<text x="${W-PR+4}" y="${(ty+4).toFixed(1)}" font-size="10" fill="#e53e3e" font-weight="600">Target</text>`;
  MONTHS.forEach((m,i)=>{
    const x=PL+i*groupW+groupW/2;
    svg+=`<text x="${x.toFixed(1)}" y="${H-6}" text-anchor="middle" font-size="11" fill="#718096">${m}</text>`;
  });
  svg+=`<line x1="${PL}" y1="${PT+CH}" x2="${W-PR}" y2="${PT+CH}" stroke="#cbd5e0"/>`;
  svg+=`<line x1="${PL}" y1="${PT}" x2="${PL}" y2="${PT+CH}" stroke="#cbd5e0"/>`;
  svg+='</svg>';
  return svg;
}

// SVG horizontal bar chart (vendors)
function svgHBar(vdData){
  const entries=Object.entries(vdData).sort((a,b)=>b[1]-a[1]).slice(0,11);
  if(!entries.length) return '<p style="color:#718096;padding:20px">Sin datos</p>';
  const maxVal=entries[0][1]||1;
  const ROW=30, W=500, PL=128, PR=70, PT=8;
  const H=PT+entries.length*ROW+10;
  let svg=`<svg viewBox="0 0 ${W} ${H}" width="100%">`;
  entries.forEach(([vend,val],i)=>{
    const y=PT+i*ROW;
    const bw=Math.max(2,(val/maxVal)*(W-PL-PR));
    const col=VEND_COLORS[ALL_VENDORS.indexOf(vend)%VEND_COLORS.length];
    const label=(VEND_LABELS[vend]||vend).substring(0,20);
    svg+=`<text x="${PL-6}" y="${y+ROW/2+4}" text-anchor="end" font-size="11" fill="#2d3748">${label}</text>`;
    svg+=`<rect x="${PL}" y="${y+5}" width="${bw.toFixed(1)}" height="${ROW-10}" fill="${col}" rx="3" opacity=".85"><title>${label}: ${fmtFull(val)}</title></rect>`;
    svg+=`<text x="${PL+bw+5}" y="${y+ROW/2+4}" font-size="11" fill="#4a5568" font-weight="600">${fmtK(val)}</text>`;
  });
  svg+='</svg>';
  return svg;
}

// SVG annual bar chart
function svgAnnual(annData){
  const W=400, H=220, PL=60, PR=15, PT=15, PB=30;
  const CW=W-PL-PR, CH=H-PT-PB;
  const vals=ALL_YEARS.map(y=>annData[y]||0);
  const maxVal=Math.max(...vals)*1.1||1;
  const annTarget=TARGET*12;
  const barStep=CW/ALL_YEARS.length;
  const barW=barStep*0.6;
  let svg=`<svg viewBox="0 0 ${W} ${H}" width="100%">`;
  for(let i=0;i<=4;i++){
    const y=PT+CH*(1-i/4);
    svg+=`<line x1="${PL}" y1="${y.toFixed(1)}" x2="${W-PR}" y2="${y.toFixed(1)}" stroke="#e2e8f0"/>`;
    svg+=`<text x="${PL-4}" y="${(y+4).toFixed(1)}" text-anchor="end" font-size="9" fill="#718096">${fmtK(maxVal*i/4)}</text>`;
  }
  ALL_YEARS.forEach((yr,i)=>{
    const v=annData[yr]||0;
    const bh=(v/maxVal)*CH;
    const x=PL+i*barStep+(barStep-barW)/2;
    const y=PT+CH-bh;
    svg+=`<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${barW.toFixed(1)}" height="${bh.toFixed(1)}" fill="${YEAR_COLORS[yr]||'#2b6cb0'}" rx="2"><title>${yr}: ${fmtFull(v)}</title></rect>`;
    svg+=`<text x="${(x+barW/2).toFixed(1)}" y="${H-5}" text-anchor="middle" font-size="10" fill="#4a5568">${yr}</text>`;
    if(v>0) svg+=`<text x="${(x+barW/2).toFixed(1)}" y="${Math.max(y-3,PT+9)}" text-anchor="middle" font-size="9" fill="#2d3748" font-weight="600">${fmtK(v)}</text>`;
  });
  if(annTarget<=maxVal){
    const ty=PT+CH*(1-annTarget/maxVal);
    svg+=`<line x1="${PL}" y1="${ty.toFixed(1)}" x2="${W-PR}" y2="${ty.toFixed(1)}" stroke="#e53e3e" stroke-width="1.5" stroke-dasharray="5,3"/>`;
    svg+=`<text x="${W-PR+2}" y="${(ty+4).toFixed(1)}" font-size="9" fill="#e53e3e">Obj</text>`;
  }
  svg+=`<line x1="${PL}" y1="${PT+CH}" x2="${W-PR}" y2="${PT+CH}" stroke="#cbd5e0"/>`;
  svg+=`<line x1="${PL}" y1="${PT}" x2="${PL}" y2="${PT+CH}" stroke="#cbd5e0"/>`;
  svg+='</svg>';
  return svg;
}

function renderKPIs(){
  const monthly=monthlyByYear();
  const years=[...selYears].sort();
  let totalUSD=0, monthCount=0, bestVal=0, bestLabel='';
  years.forEach(yr=>{
    (monthly[yr]||[]).forEach((v,mi)=>{
      if(v>0){totalUSD+=v;monthCount++;}
      if(v>bestVal){bestVal=v;bestLabel=MONTHS[mi]+' '+yr;}
    });
  });
  const avg=monthCount>0?totalUSD/monthCount:0;
  const p=pct(avg,TARGET);
  const isOk=p>=100;
  document.getElementById('kpis').innerHTML=[
    {lbl:'Total facturado',val:fmtFull(totalUSD),sub:'período seleccionado',cls:'info'},
    {lbl:'Promedio mensual',val:fmtK(avg),sub:p+'% del target USD 215K',cls:isOk?'ok':'warn'},
    {lbl:'Mejor mes',val:fmtK(bestVal),sub:bestLabel||'–',cls:'info'},
    {lbl:'Target mensual',val:fmtK(TARGET),sub:(isOk?'&#10003; Alcanzado':'Falta '+'$'+Math.round(TARGET-avg).toLocaleString('es-AR'))+' en prom.',cls:isOk?'ok':'warn'},
  ].map(k=>`<div class="kpi ${k.cls}">
    <div class="kpi-label">${k.lbl}</div>
    <div class="kpi-value">${k.val}</div>
    <div class="kpi-sub">${k.sub}</div>
    <div class="progress-bar"><div class="progress-fill" style="width:${Math.min(p,100)}%;background:${isOk?'#276749':'#c05621'}"></div></div>
  </div>`).join('');
}

function renderMonthly(){
  const m=monthlyByYear();
  const yrs=[...selYears].sort();
  document.getElementById('monthly-sub').textContent=yrs.join(' vs ');
  document.getElementById('monthly-chart').innerHTML=svgBarChart(m);
  document.getElementById('monthly-legend').innerHTML=
    yrs.map(y=>`<div class="legend-item"><div class="legend-dot" style="background:${YEAR_COLORS[y]}"></div>${y}</div>`).join('')+
    `<div class="legend-item" style="margin-left:8px"><svg width="20" height="3" style="vertical-align:middle"><line x1="0" y1="1.5" x2="20" y2="1.5" stroke="#e53e3e" stroke-width="2" stroke-dasharray="5,3"/></svg>&nbsp;Target USD 215K</div>`;
}

function renderVendor(){
  const yrs=[...selYears].sort();
  document.getElementById('vend-sub').textContent=yrs.join(', ');
  document.getElementById('vendor-chart').innerHTML=svgHBar(vendorTotals());
}

function renderAnnual(){
  document.getElementById('annual-chart').innerHTML=svgAnnual(annualTotals());
}

function renderTable(){
  const years=[...selYears].sort();
  const monthly=monthlyByYear();
  const latestYear=years[years.length-1];
  let html=`<table><thead><tr><th>Mes</th>${years.map(y=>`<th>${y}</th>`).join('')}<th>vs Target</th></tr></thead><tbody>`;
  const totals=years.map(()=>0);
  MONTHS.forEach((m,mi)=>{
    const vals=years.map((y,yi)=>{const v=(monthly[y]||[])[mi]||0;totals[yi]+=v;return v;});
    const last=vals[vals.length-1];
    const p=pct(last,TARGET);
    const pc=p>=100?'#276749':p>=70?'#c05621':'#a0aec0';
    html+=`<tr><td>${m}</td>${vals.map(v=>`<td>${v>0?fmtK(v):'&ndash;'}</td>`).join('')}<td style="color:${pc};font-weight:600">${last>0?p+'%':'&ndash;'}</td></tr>`;
  });
  const lastTotal=totals[totals.length-1];
  const avgP=pct(lastTotal/12,TARGET);
  html+=`<tr><td>TOTAL</td>${totals.map(t=>`<td>${fmtFull(t)}</td>`).join('')}<td style="color:${avgP>=100?'#276749':'#c05621'}">${avgP}% prom</td></tr>`;
  html+='</tbody></table>';
  document.getElementById('monthly-table').innerHTML=html;
}

function renderAll(){renderKPIs();renderMonthly();renderVendor();renderAnnual();renderTable();}

// Setup filters
function setupFilters(){
  const yf=document.getElementById('year-filters');
  ALL_YEARS.forEach(yr=>{
    const btn=document.createElement('button');
    btn.className='year-btn'+(selYears.has(yr)?' active':'');
    btn.textContent=yr;
    btn.style.cssText=selYears.has(yr)?`background:${YEAR_COLORS[yr]};border-color:${YEAR_COLORS[yr]};color:#fff`:`border-color:${YEAR_COLORS[yr]}`;
    btn.onclick=()=>{
      if(selYears.has(yr)){
        if(selYears.size>1){selYears.delete(yr);btn.className='year-btn';btn.style.cssText=`border-color:${YEAR_COLORS[yr]}`;}
      }else{
        selYears.add(yr);btn.className='year-btn active';btn.style.cssText=`background:${YEAR_COLORS[yr]};border-color:${YEAR_COLORS[yr]};color:#fff`;
      }
      renderAll();
    };
    yf.appendChild(btn);
  });

  const vf=document.getElementById('vend-filters');
  const todoBtn=document.createElement('button');
  todoBtn.className='vend-btn active';todoBtn.textContent='Todos';
  todoBtn.style.cssText='background:#2f855a;border-color:#2f855a;color:#fff';
  todoBtn.onclick=()=>{
    selVendors=new Set(ALL_VENDORS);
    document.querySelectorAll('.vend-btn').forEach(b=>{
      b.className='vend-btn active';b.style.cssText='background:#2f855a;border-color:#2f855a;color:#fff';
    });
    renderAll();
  };
  vf.appendChild(todoBtn);

  ALL_VENDORS.forEach((v,idx)=>{
    const btn=document.createElement('button');
    btn.className='vend-btn active';
    const col=VEND_COLORS[idx%VEND_COLORS.length];
    btn.textContent=(VEND_LABELS[v]||v).split(' ')[0];
    btn.title=VEND_LABELS[v]||v;
    btn.style.cssText=`background:${col};border-color:${col};color:#fff`;
    btn.onclick=()=>{
      if(selVendors.has(v)&&selVendors.size>1){
        selVendors.delete(v);btn.className='vend-btn';btn.style.cssText=`border-color:${col};color:${col}`;
      }else{
        selVendors.add(v);btn.className='vend-btn active';btn.style.cssText=`background:${col};border-color:${col};color:#fff`;
      }
      renderAll();
    };
    vf.appendChild(btn);
  });
}

setupFilters();
renderAll();
</script>
</body>
</html>"""

out = 'C:/Users/usuario/OneDrive/Escritorio/CLAUDE/dashboard_ventas.html'
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"OK: {out}")
print(f"Size: {len(html)/1024:.0f} KB")
