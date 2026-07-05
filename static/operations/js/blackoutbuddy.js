'use strict';

// --- EARLY COMPATIBILITY SHIM (uncommented, no nested block comments) ---
(function () {
  try {
    if (typeof window !== 'undefined' && typeof window.buildDefaultWATTAGES === 'undefined') {
      window.buildDefaultWATTAGES = function () {
        // If the proper function exists later, call it; otherwise return any already-built map or empty object.
        if (typeof buildDefaultWattages === 'function') {
          try { return buildDefaultWattages(); } catch (e) { /* ignore */ }
        }
        return window.DEFAULT_WATTAGES || {};
      };
    }
  } catch (err) {
    console.warn('BlackoutBuddy early shim error (non-fatal):', err);
  }
})();

/* -------------------- NAV: HAMBURGER -------------------- */
(function initMenu() {
  const hamburger = document.getElementById('hamburger-menu');
  const navMenu = document.getElementById('nav-menu');
  if (hamburger && navMenu) {
    hamburger.addEventListener('click', () => {
      navMenu.classList.toggle('active');
      hamburger.classList.toggle('open');
    });
  }
})();

/* -------------------- EXISTING OPTIONS (KEPT + MERGED LATER) -------------------- */
const EXISTING_APPLIANCE_OPTIONS = [
  'Select Appliance',
  'Air Conditioner (Window)',
  'Box Fan',
  'Coffee Pot - Keurig',
  'CPAP',
  'Desktop Computer',
  'Electric Clothes Dryer',
  'Electric Stove',
  'Freezer',
  'Laptop Gaming',
  'Laptop home/office',
  'Microwave',
  'OTHER - insert your own values',
  'Refrigerator',
  'Smart Phone',
  'Space Heater',
  'Tablet',
  'Television',
  'Washing Machine'
];

/* Typical wattage estimates for existing items (will be extended by commonAppliances) */
const BASE_DEFAULT_WATTAGES = {
  'Air Conditioner (Window)': { run: 1000, start: 2200 },
  'Box Fan': { run: 75, start: 100 },
  'Coffee Pot - Keurig': { run: 1500, start: 1500 },
  'CPAP': { run: 60, start: 100 },
  'Desktop Computer': { run: 200, start: 200 },
  'Electric Clothes Dryer': { run: 3000, start: 5000 },
  'Electric Stove': { run: 2000, start: 2100 },
  'Freezer': { run: 100, start: 800 },
  'Laptop Gaming': { run: 500, start: 300 },
  'Laptop home/office': { run: 175, start: 200 },
  'Microwave': { run: 1000, start: 1500 },
  'Refrigerator': { run: 150, start: 1200 },
  'Smart Phone': { run: 6.5, start: 2 },
  'Space Heater': { run: 1500, start: 1500 },
  'Tablet': { run: 35, start: 4 },
  'Television': { run: 100, start: 150 },
  'Washing Machine': { run: 500, start: 1200 }
};

/* -------------------- DATA (MERGED FROM LOGIC DOC + YOUR ADDITIONS) -------------------- */
const commonAppliances = [
  { name: 'Refrigerator', runningWatts: 150, startingWatts: 1200, category: 'Essential' },
  { name: 'CPAP', runningWatts: 60, startingWatts: 100, category: 'Essential' },
  { name: 'Freezer', runningWatts: 100, startingWatts: 800, category: 'Essential' },
  { name: 'Microwave', runningWatts: 1000, startingWatts: 1500, category: 'Kitchen' },
  { name: 'Electric Stove', runningWatts: 2000, startingWatts: 2100, category: 'Kitchen' },
  { name: 'Coffee Pot - Keurig', runningWatts: 1500, startingWatts: 1500, category: 'Kitchen' },
  { name: 'Air Conditioner (Window)', runningWatts: 1000, startingWatts: 2200, category: 'Climate' },
  { name: 'Box Fan', runningWatts: 75, startingWatts: 100, category: 'Climate' },
  { name: 'Space Heater', runningWatts: 1500, startingWatts: 1500, category: 'Climate' },
  { name: 'Television', runningWatts: 100, startingWatts: 150, category: 'Entertainment' },
  { name: 'Desktop Computer', runningWatts: 200, startingWatts: 200, category: 'Entertainment' },
  { name: 'Washing Machine', runningWatts: 500, startingWatts: 1200, category: 'Laundry' },
  { name: 'Smart Phone', runningWatts: 6.5, startingWatts: 2, category: 'Mobile' },
  { name: 'Tablet', runningWatts: 35, startingWatts: 4, category: 'Mobile' },
  { name: 'Laptop home/office', runningWatts: 175, startingWatts: 200, category: 'Computing' },
  { name: 'Laptop Gaming', runningWatts: 500, startingWatts: 300, category: 'Computing' },
  { name: 'Electric Clothes Dryer', runningWatts: 3000, startingWatts: 5000, category: 'Laundry' },
  { name: 'OTHER - insert your own values', runningWatts: 0, startingWatts: 0, category: 'Other' }
];

const ecoFlowProducts = [
  // DELTA (AC-capable)
  { name: 'DELTA Mini', series: 'DELTA', baseCapacity: 0.882, maxPower: 1400, surgePower: 2100, expandable: false },
  { name: 'DELTA 2', series: 'DELTA', baseCapacity: 1.024, maxPower: 1800, surgePower: 2700, expandable: true, maxCapacity: 2.048 },
  { name: 'DELTA 2 Max', series: 'DELTA', baseCapacity: 2.048, maxPower: 2400, surgePower: 3400, expandable: true, maxCapacity: 6.048 },
  { name: 'DELTA 3', series: 'DELTA', baseCapacity: 1.024, maxPower: 1800, surgePower: 3600, expandable: true, maxCapacity: 6.048 },
  { name: 'DELTA 3 Plus (2 solar inputs)', series: 'DELTA', baseCapacity: 1.024, maxPower: 1800, surgePower: 3600, expandable: true, maxCapacity: 6.048 },
  { name: 'DELTA 3 1500', series: 'DELTA', baseCapacity: 1.536, maxPower: 1800, surgePower: 3600, expandable: true, maxCapacity: 6.048 },
  { name: 'DELTA Pro', series: 'DELTA', baseCapacity: 3.6, maxPower: 3600, surgePower: 7200, expandable: true, maxCapacity: 10.8 },
  { name: 'DELTA 3 Pro', series: 'DELTA', baseCapacity: 4.096, maxPower: 4000, surgePower: 8000, expandable: true, maxCapacity: 12.288 },
  { name: 'DELTA Pro Ultra', series: 'DELTA', baseCapacity: 6, maxPower: 7200, surgePower: 7200, expandable: true, maxCapacity: 90 },
  { name: 'DELTA 3 Classic', series: 'DELTA', baseCapacity: 1.024, maxPower: 1800, surgePower: 3600, expandable: false, maxCapacity: 1.024 },
  { name: 'DELTA 3 Max', series: 'DELTA', baseCapacity: 2.048, maxPower: 2400, surgePower: 4800, expandable: false, maxCapacity: 2.048 },
  { name: 'DELTA 3 Max Plus', series: 'DELTA', baseCapacity: 2.048, maxPower: 3000, surgePower: 6000, expandable: true, maxCapacity: 10.8 },
  { name: 'DELTA 3 Ultra', series: 'DELTA', baseCapacity: 3.072, maxPower: 3600, surgePower: 7200, expandable: false, maxCapacity:  3.072 },
  { name: 'DELTA 3 Ultra Plus', series: 'DELTA', baseCapacity: 3.072, maxPower: 3600, surgePower: 7200, expandable: false, maxCapacity: 11.8 },
  { name: 'DELTA Pro Ultra X', series: 'DELTA', baseCapacity: 6, maxPower: 7200, surgePower: 12000, expandable: true, maxCapacity: 180 },

  // RAPID (DC-only, capacities in kWh)
  { name: 'Rapid 10K', series: 'RAPID', baseCapacity: 0.037, maxPower: 65, surgePower: 0, expandable: false, maxCapacity: 0.037 },
  { name: 'Rapid 5K', series: 'RAPID', baseCapacity: 0.0185, maxPower: 30, surgePower: 0, expandable: false, maxCapacity: 0.0185 },
  { name: 'Rapid Pro X', series: 'RAPID', baseCapacity: 0.099, maxPower: 300, surgePower: 0, expandable: false, maxCapacity: 0.099 },
  { name: 'Rapid Pro (140W Built-in Cable)', series: 'RAPID', baseCapacity: 0.099, maxPower: 300, surgePower: 0, expandable: false, maxCapacity: 0.099 },
  { name: 'Rapid Pro Power (100W Built-in Cable)', series: 'RAPID', baseCapacity: 0.074, maxPower: 230, surgePower: 0, expandable: false, maxCapacity: 0.074 },
  { name: 'Rapid Pro 3-in-1', series: 'RAPID', baseCapacity: 0.036, maxPower: 67, surgePower: 0, expandable: false, maxCapacity: 0.036 },
  { name: 'Rapid Power (100w built-in cable)', series: 'RAPID', baseCapacity: 0.090, maxPower: 170, surgePower: 0, expandable: false, maxCapacity: 0.090 },
  { name: 'Rapid Power', series: 'RAPID', baseCapacity: 0.090, maxPower: 170, surgePower: 0, expandable: false, maxCapacity: 0.090 },
  { name: 'Rapid Mag Power 10k (7.5w wireless)', series: 'RAPID', baseCapacity: 0.039, maxPower: 30, surgePower: 0, expandable: false, maxCapacity: 0.036 },
  { name: 'Rapid Mag Power 5k (7.5w wireless)', series: 'RAPID', baseCapacity: 0.019, maxPower: 20, surgePower: 0, expandable: false, maxCapacity: 0.019 },

  // TRAIL (DC-only)
  { name: 'Trail 200 DC', series: 'TRAIL', baseCapacity: 0.192, maxPower: 220, surgePower: 0, expandable: false, maxCapacity: 0.192 },
  { name: 'Trail 300 DC', series: 'TRAIL', baseCapacity: 0.288, maxPower: 300, surgePower: 0, expandable: false, maxCapacity: 0.288 },
  { name: 'Trail PLUS 300 DC (Has Light and works with app)', series: 'TRAIL', baseCapacity: 0.288, maxPower: 300, surgePower: 0, expandable: false, maxCapacity: 0.288 },

  // RIVER (AC-capable)
  { name: 'RIVER Pro', series: 'RIVER', baseCapacity: 0.72, maxPower: 600, surgePower: 1200, expandable: true, maxCapacity: 1.44 },
  { name: 'RIVER 2', series: 'RIVER', baseCapacity: 0.24, maxPower: 300, surgePower: 600, expandable: false },
  { name: 'RIVER 2 Max', series: 'RIVER', baseCapacity: 0.512, maxPower: 500, surgePower: 1000, expandable: false },
  { name: 'RIVER 2 Pro', series: 'RIVER', baseCapacity: 0.716, maxPower: 800, surgePower: 1600, expandable: false },
  { name: 'RIVER 3', series: 'RIVER', baseCapacity: 0.245, maxPower: 300, surgePower: 600, expandable: false },
  { name: 'RIVER 3 Plus', series: 'RIVER', baseCapacity: 0.286, maxPower: 600, surgePower: 1200, expandable: true, maxCapacity: 0.572 },
  { name: 'RIVER 3 Plus Max Wireless ( adds a 5k Rapid charger )', series: 'RIVER', baseCapacity: 0.858, maxPower: 600, surgePower: 1200, expandable: true, maxCapacity: 0.572 },
  { name: 'RIVER 3 Max', series: 'RIVER', baseCapacity: 0.572, maxPower: 600, surgePower: 1200, expandable: true, maxCapacity: 0.858 },
  { name: 'RIVER 3 Max Plus', series: 'RIVER', baseCapacity: 0.858, maxPower: 600, surgePower: 1200, expandable: true },
];

const productAffiliateLinks = {
  'DELTA Mini': 'https://us.ecoflow.com/products/delta-mini-portable-power-station?sca_ref=7408943.R33f7CbNF7',
  'DELTA 2': 'https://us.ecoflow.com/products/delta-2-portable-power-station?_pos=1&_sid=cd6c8860b&_ss=r&variant=40569176326217&sca_ref=7408943.R33f7CbNF7&sca_source=EcoFlow DELTA 2',
  'DELTA 2 Max': 'https://us.ecoflow.com/products/delta-2-max-portable-power-station?_pos=1&_sid=cc369e7d5&_ss=r&variant=40538145095753&sca_ref=7408943.R33f7CbNF7&sca_source=delta 2 max',
  'DELTA 3': 'https://us.ecoflow.com/products/delta-3-portable-power-station?_pos=1&_sid=f54de58a6&_ss=r&variant=42017992048713&sca_ref=7408943.R33f7CbNF7&sca_source=Delta 3',
  'DELTA 3 Plus (2 solar inputs)': 'https://us.ecoflow.com/products/delta-3-plus-portable-power-station?_pos=1&_sid=3ff778c93&_ss=r&variant=54588299575369&sca_ref=7408943.R33f7CbNF7&sca_source=Delta 3 plus',
  'DELTA 3 1500': 'https://us.ecoflow.com/products/ecoflow-delta-3-1500-solar-generator?_pos=2&_sid=8d7d9a1ce&_ss=r&variant=41836896682057&sca_ref=7408943.R33f7CbNF7&sca_source=Delta 3 1500',
  'DELTA 3 Max Plus': 'https://us.ecoflow.com/products/delta-3-max-series-portable-power-station?variant=54718699962441&view=d3mp&sca_ref=7408943.R33f7CbNF7&sca_source=delta 3 max plus',
  'DELTA 3 Max': 'https://us.ecoflow.com/products/delta-3-max-series-portable-power-station?sca_ref=7408943.R33f7CbNF7&sca_source=delta 3 max',
  'DELTA 3 Classic': 'https://us.ecoflow.com/products/delta-3-classic-portable-power-station?_pos=1&_sid=35a92c297&_ss=r&variant=54692156801097&sca_ref=7408943.R33f7CbNF7&sca_source=delta 3 classic',
  'DELTA 3 ULTRA': 'https://us.ecoflow.com/products/delta-3-ultra-series-portable-power-station?_pos=1&_sid=4d01aad85&_ss=r&variant=54692148871241&view=d3u&sca_ref=7408943.R33f7CbNF7&sca_source=delta 3 ultra',
  'DELTA Pro': 'https://us.ecoflow.com/products/delta-pro-portable-power-station?sca_ref=7408943.R33f7CbNF7',
  'DELTA 3 Pro': 'https://us.ecoflow.com/products/delta-pro-3-portable-power-station?sca_ref=7408943.R33f7CbNF7&sca_source=DELTA PRO 3',
  'DELTA 3 ULTRA PLUS': 'https://us.ecoflow.com/products/delta-pro-3-portable-power-station?sca_ref=7408943.R33f7CbNF7&sca_source=DELTA PRO 3',
  'DELTA Pro Ultra': 'https://us.ecoflow.com/products/delta-3-ultra-series-portable-power-station?variant=54718705107017&view=d3up&sca_ref=7408943.R33f7CbNF7&sca_source=delta 3 ultra plus',
  'DELTA Pro Ultra X' : 'https://us.ecoflow.com/collections/delta-pro-series/products/delta-pro-ultra-x?variant=54714781171785&sca_ref=7408943.R33f7CbNF7&sca_source=delta ultra x',
  'RIVER Pro': 'https://us.ecoflow.com/products/river-pro-river-pro-extra-battery-bundle?sca_ref=7408943.R33f7CbNF7',
  'RIVER 2': 'https://us.ecoflow.com/products/river-2-portable-power-station?_pos=1&_sid=0234254f1&_ss=r&variant=40589642039369&sca_ref=7408943.R33f7CbNF7&sca_source=River 2',
  'RIVER 2 Max': 'https://us.ecoflow.com/products/river-2-max-portable-power-station?sca_ref=7408943.R33f7CbNF7',
  'RIVER 2 Pro': 'https://us.ecoflow.com/products/river-2-pro-portable-power-station?_pos=2&_sid=13bd458b5&_ss=r&sca_ref=7408943.R33f7CbNF7&sca_source=River 2 Pro',
  'RIVER 3': 'https://us.ecoflow.com/products/river-3-portable-power-station?_pos=1&_sid=11ece7428&_ss=r&variant=41636504305737&sca_ref=7408943.R33f7CbNF7&sca_source=River 3',
  'RIVER 3 Plus': 'https://us.ecoflow.com?sca_ref=7408943.R33f7CbNF7&utm_source=uppromote&utm_medium=community&utm_campaign=koc',
  'RIVER 3 Max': 'https://us.ecoflow.com?sca_ref=7408943.R33f7CbNF7&utm_source=uppromote&utm_medium=community&utm_campaign=koc',
  'RIVER 3 Max Plus': 'https://us.ecoflow.com?sca_ref=7408943.R33f7CbNF7&utm_source=uppromote&utm_medium=community&utm_campaign=koc',
  'RIVER 3 Plus Max Wireless ( adds a 5k Rapid charger )': 'https://us.ecoflow.com/products/river-3-max-plus-wireless?_pos=1&_sid=e77e636dd&_ss=r&variant=54478642905161&sca_ref=7408943.R33f7CbNF7&sca_source=RIVER 3 Max Plus Wireless',
  'Rapid 10K': 'https://us.ecoflow.com/collections/power-bank/products/ecoflow-rapid-magnetic-power-bank-10000mah?variant=42021147443273&sca_ref=7408943.R33f7CbNF7&sca_source=Rapid 10k',
  'Rapid 5K': 'https://us.ecoflow.com/products/rapid-magnetic-power-bank-5000mah?variant=54347781832777&sca_ref=7408943.R33f7CbNF7&sca_source=Rapid 5k',
  'Rapid Pro X': 'https://us.ecoflow.com/products/ecoflow-rapid-pro-x-power-bank-27650mah-300w?sca_ref=7408943.R33f7CbNF7',
  'Rapid Pro (140W Built-in Cable)': 'https://us.ecoflow.com/products/ecoflow-rapid-pro-power-bank-27650mah-300w-140w-built-in-cable?variant=54593876000841&sca_ref=7408943.R33f7CbNF7&sca_source=Pro Power',
  'Rapid Pro Power (100W Built-in Cable)': 'https://us.ecoflow.com/products/ecoflow-rapid-pro-power-bank-20000mah-230w-100w-built-in-cable?variant=54627329474633&sca_ref=7408943.R33f7CbNF7&sca_source=Pro Power 140w cable',
  'Rapid Pro 3-in-1': 'https://us.ecoflow.com/products/ecoflow-rapid-pro-3-in-1-power-bank-10000mah-67w?variant=54593877606473&sca_ref=7408943.R33f7CbNF7&sca_source=Pro 3-in-1',
  'Rapid Power': 'https://us.ecoflow.com/products/ecoflow-rapid-power-bank-25000mah-170w?variant=54593882128457&sca_ref=7408943.R33f7CbNF7&sca_source=Power',
  'Rapid Power (100w built-in cable)': 'https://us.ecoflow.com/products/ecoflow-rapid-power-bank-25-000mah-170w-100w-built-in-and-retractable?variant=54593881374793&sca_ref=7408943.R33f7CbNF7&sca_source=Power 100w cable',
  'Rapid Mag Power 10k (7.5w wireless)': 'https://us.ecoflow.com/products/ecoflow-rapid-mag-power-bank-10-000mah-7-5w-magnetic-charging?variant=54593884651593&sca_ref=7408943.R33f7CbNF7&sca_source=MagPower 10K',
  'Rapid Mag Power 5k (7.5w wireless)': 'https://us.ecoflow.com/products/ecoflow-rapid-mag-power-bank-5000mah-7-5w-magnetic-charging?variant=54593882488905&sca_ref=7408943.R33f7CbNF7&sca_source=MagPower 5K',
  'Trail 200 DC': 'https://us.ecoflow.com/products/trail-series?variant=54553979682889&view=trail200&sca_ref=7408943.R33f7CbNF7&sca_source=Trail 200',
  'Trail 300 DC': 'https://us.ecoflow.com/products/trail-series?variant=54553980043337&view=trail&sca_ref=7408943.R33f7CbNF7&sca_source=Trail 300',
  'Trail PLUS 300 DC (Has Light and works with app)':'https://us.ecoflow.com/products/trail-series?variant=54553980141641&view=trailplus300&sca_ref=7408943.R33f7CbNF7&sca_source=Trail PLUS 300 DC',
  
};

/* -------------------- MERGED OPTIONS + WATTAGE MAP -------------------- */
function buildMergedOptions() {
  const set = new Set(EXISTING_APPLIANCE_OPTIONS);
  commonAppliances.forEach(a => set.add(a.name));
  const all = Array.from(set).filter(Boolean);
  const rest = all.filter(v => v !== 'Select Appliance')
    .sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase()));
  return ['Select Appliance', ...rest];
}
function buildDefaultWattages() {
  const map = { ...BASE_DEFAULT_WATTAGES };
  commonAppliances.forEach(a => { map[a.name] = { run: a.runningWatts, start: a.startingWatts }; });
  return map;
}
const MERGED_APPLIANCE_OPTIONS = buildMergedOptions();
const DEFAULT_WATTAGES = buildDefaultWATTAGES();

/* -------------------- UI RENDERING -------------------- */
const ROW_COUNT = 5;

function createApplianceRow(index) {
  const optionsHtml = MERGED_APPLIANCE_OPTIONS
    .map(name => `<option value="${name.replace(/"/g, '&quot;')}">${name}</option>`)
    .join('');
  return `
    <div class="appliance-row" id="appliance-${index}">
      <select class="appliance-select" data-index="${index}" aria-label="Appliance ${index + 1}">
        ${optionsHtml}
      </select>
      <input type="number" class="running-watts" placeholder="Running Watts" min="0" step="0.1" aria-label="Running Watts ${index + 1}">
      <input type="number" class="starting-watts" placeholder="Starting Watts" min="0" step="0.1" aria-label="Starting Watts (Surge) ${index + 1}">
      <input type="number" class="hours" placeholder="Hours" min="0" max="24" step="0.1" aria-label="Hours/Day ${index + 1}">
      <div class="daily-kwh">0.00 kWh</div>
    </div>
  `;
}

function renderApplianceRows() {
  const container = document.getElementById('applianceRows');
  if (!container) return;
  let html = '';
  for (let i = 0; i < ROW_COUNT; i++) html += createApplianceRow(i);
  container.innerHTML = html;

  // Wire events
  container.querySelectorAll('.appliance-select').forEach(sel => {
    sel.addEventListener('change', () => {
      const idx = Number(sel.getAttribute('data-index') || '0');
      updateWattage(idx);
    });
  });
  container.addEventListener('input', (e) => {
    const t = e.target;
    if (!t) return;
    if (t.classList.contains('running-watts') || t.classList.contains('starting-watts') || t.classList.contains('hours')) {
      calculatePower();
    }
  });
}

function updateWattage(index) {
  const row = document.getElementById(`appliance-${index}`);
  if (!row) return;
  const select = row.querySelector('.appliance-select');
  const runningInput = row.querySelector('.running-watts');
  const startingInput = row.querySelector('.starting-watts');

  const name = select?.value || '';
  const preset = DEFAULT_WATTAGES[name];

  if (!name || name === 'Select Appliance' || name === 'OTHER - insert your own values') {
    runningInput.value = '';
    startingInput.value = '';
    runningInput.placeholder = 'Enter value';
    startingInput.placeholder = 'Enter value';
  } else if (preset) {
    runningInput.value = preset.run;
    startingInput.value = preset.start;
    runningInput.placeholder = '';
    startingInput.placeholder = '';
  }
  calculatePower();
}

/* -------------------- CALCULATION + RECOMMENDATIONS -------------------- */
function effectiveSurge(p) {
  const s = Number(p?.surgePower ?? 0);
  return s > 0 ? s : Number(p?.maxPower ?? 0);
}
function hasCapacity(p, kwh) {
  const base = Number(p?.baseCapacity ?? 0);
  const canExpand = !!p?.expandable && Number(p?.maxCapacity ?? 0) >= kwh;
  return base >= kwh || canExpand;
}
function isCompatible(p, running, starting, kwh) {
  const maxP = Number(p?.maxPower ?? 0);
  const surge = effectiveSurge(p);
  return maxP >= running && surge >= starting && hasCapacity(p, kwh);
}
function isRapidFamily(p) {
  const n = String(p?.name || '').toLowerCase();
  const s = String(p?.series || '').toLowerCase();
  return s === 'rapid' || n.startsWith('rapid');
}
function isTrailFamily(p) {
  const n = String(p?.name || '').toLowerCase();
  const s = String(p?.series || '').toLowerCase();
  return s === 'trail' || n.startsWith('trail');
}
const DC_COMPAT_APPLIANCES = new Set(['Smart Phone', 'Tablet', 'Laptop home/office', 'Laptop Gaming']);

function calculatePower() {
  let totalRunning = 0;
  let totalStarting = 0;
  let totalKwh = 0;
  let hasSelection = false;

  document.querySelectorAll('.appliance-row').forEach(row => {
    const select = row.querySelector('.appliance-select');
    const running = parseFloat(row.querySelector('.running-watts')?.value) || 0;
    const starting = parseFloat(row.querySelector('.starting-watts')?.value) || 0;
    const hours = parseFloat(row.querySelector('.hours')?.value) || 0;

    const kwh = (running * hours) / 1000;
    const dailyEl = row.querySelector('.daily-kwh');
    if (dailyEl) dailyEl.textContent = `${isFinite(kwh) ? kwh.toFixed(2) : '0.00'} kWh`;

    if (select && select.value && select.value !== 'Select Appliance') {
      hasSelection = true;
      totalRunning += running;
      totalStarting += starting;
      totalKwh += isFinite(kwh) ? kwh : 0;
    }
  });

  document.getElementById('totalWatts').textContent = `Total Running Watts: ${Math.round(totalRunning)} W`;
  document.getElementById('totalStarting').textContent = `Total Starting Watts: ${Math.round(totalStarting)} W`;
  document.getElementById('totalKwh').textContent = `Total Daily Usage: ${totalKwh.toFixed(2)} kWh`;

  updateRecommendations(totalRunning, totalStarting, totalKwh, hasSelection);
}

/* Hybrid recommendation logic with AC/DC constraints and mobile prioritization */
function updateRecommendations(running, starting, kwh, hasSelection) {
  const rec = document.getElementById('recommendation');

  // Hide suggestions on empty state
  if (!hasSelection || (running === 0 && starting === 0 && kwh === 0)) {
    if (rec) rec.innerHTML = '';
    return;
  }

  // Collect selected appliances & hours
  const selected = Array.from(document.querySelectorAll('.appliance-row'))
    .map(row => {
      const sel = row.querySelector('.appliance-select');
      if (!sel || !sel.value || sel.value === 'Select Appliance') return null;
      const hours = parseFloat(row.querySelector('.hours')?.value) || 0;
      return { name: sel.value, hours, norm: normalizeKey(sel.value) };
    })
    .filter(Boolean);

  // Trigger condition: any Smart Phone / Tablet / Laptop home/office selected with hours < 10
  const MOBILE_KEYS = new Set([
    normalizeKey('Smart Phone'),
    normalizeKey('Smartphone'),
    normalizeKey('Tablet'),
    normalizeKey('Laptop home/office'),
    normalizeKey('Laptop homeoffice'),
    normalizeKey('Laptop home office')
  ]);
  const mobileUnder10 = selected.some(s => MOBILE_KEYS.has(s.norm) && s.hours < 10);

  // Build compatible products (power / surge / capacity)
  let compatible = ecoFlowProducts.filter(p => isCompatible(p, running, starting, kwh));

  if (compatible.length === 0) {
    if (rec) {
      rec.innerHTML = '<ul class="recommendation-section"><li>No EcoFlow product matches your requirements. Try reducing your load or splitting into multiple units.</li></ul>';
    }
    return;
  }

  // PRIORITIZATION STRATEGY:
  // If mobileUnder10 is true => RAPID first, then TRAIL, then others.
  // Else fall back to previous hybrid logic (series-tier then capacity).
  let ordered = [];

  if (mobileUnder10) {
    // Partition compatible into RAPID, TRAIL, and others (preserve stability)
    const rapids = [];
    const trails = [];
    const others = [];

    for (const p of compatible) {
      if (isRapidFamily(p)) rapids.push(p);
      else if (isTrailFamily(p)) trails.push(p);
      else others.push(p);
    }

    // Within each bucket, keep smaller capacity first (compact products first)
    const sortByCapacityThenPower = arr => arr.slice().sort((a, b) => {
      const ca = Number(a.baseCapacity ?? 0), cb = Number(b.baseCapacity ?? 0);
      if (ca !== cb) return ca - cb;
      return Number(a.maxPower ?? 0) - Number(b.maxPower ?? 0);
    });

    ordered = [
      ...sortByCapacityThenPower(rapids),
      ...sortByCapacityThenPower(trails),
      ...sortByCapacityThenPower(others)
    ];
  } else {
    // Fallback: keep existing overall order (capacity asc then power asc)
    ordered = compatible.slice().sort((a, b) => {
      const ca = Number(a?.baseCapacity ?? 0), cb = Number(b?.baseCapacity ?? 0);
      if (ca !== cb) return ca - cb;
      return Number(a?.maxPower ?? 0) - Number(b?.maxPower ?? 0);
    });
  }

  // Render top 3 as Good / Better / Best (use getAffiliateLink so anchors resolve)
  const labels = ['Good', 'Better', 'Best'];
  let html = '';
  if (ordered.length === 0) {
    html = '<li>No EcoFlow product matches your requirements. Try reducing your load or splitting into multiple units.</li>';
  } else {
    html = ordered.slice(0, 3).map((p, i) => {
      let nameLabel = p.name;
      if (p.expandable && p.maxCapacity && kwh > p.baseCapacity && kwh <= p.maxCapacity) {
        nameLabel += ' with Extra Battery';
      }
      const link = getAffiliateLink(p.name);
      const linkHtml = link && link !== '#' ?
        `<a href="${link}" target="_blank" rel="noopener noreferrer" class="shop-link">${nameLabel}</a>` :
        `<span style="color:#b22222" title="No affiliate link found">${nameLabel} (no link)</span>`;
      const cap = (p.expandable && p.maxCapacity && kwh > p.baseCapacity) ? p.maxCapacity : p.baseCapacity;
      const tier = labels[i] || `Option ${i + 1}`;
      // ensure anchors open safely and are visible (no inline styling changes)
      return `<li><strong>${tier}:</strong> ${linkHtml} (${cap} kWh, ${p.maxPower}W, Surge: ${effectiveSurge(p)}W)</li>`;
    }).join('');
  }

  if (rec) rec.innerHTML = `<ul class="recommendation-section">${html}</ul>`;
}

/* -------------------- PRINT -------------------- */
function printResults() {
  const rows = Array.from(document.querySelectorAll('.appliance-row'));
  let table = '<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;width:100%">';
  table += '<thead><tr><th>Appliance</th><th>Running Watts</th><th>Starting Watts</th><th>Hours/Day</th><th>Daily kWh</th></tr></thead><tbody>';
  rows.forEach(row => {
    const sel = row.querySelector('.appliance-select');
    if (sel && sel.value && sel.value !== 'Select Appliance') {
      const run = row.querySelector('.running-watts')?.value || '0';
      const start = row.querySelector('.starting-watts')?.value || '0';
      const hours = row.querySelector('.hours')?.value || '0';
      const kwh = row.querySelector('.daily-kwh')?.textContent || '0.00 kWh';
      table += `<tr><td>${sel.value}</td><td>${run}</td><td>${start}</td><td>${hours}</td><td>${kwh}</td></tr>`;
    }
  });
  table += '</tbody></table>';

  const totalWatts = document.getElementById('totalWatts')?.textContent || '';
  const totalStarting = document.getElementById('totalStarting')?.textContent || '';
  const totalKwh = document.getElementById('totalKwh')?.textContent || '';
  const recommendation = document.getElementById('recommendation')?.innerHTML || '';

  const w = window.open('', '_blank');
  w.document.write(`
    <html><head><title>BlackoutBuddy Results</title>
      <style>body{font-family:Arial,Helvetica,sans-serif;padding:20px;color:#222}h1{margin:0 0 16px}.totals p{margin:6px 0;font-weight:bold}</style>
    </head><body>
      <h1>BlackoutBuddy Results</h1>
      <div class="totals"><p>${totalWatts}</p><p>${totalStarting}</p><p>${totalKwh}</p></div>
      <h2>Recommendations</h2>
      ${recommendation}
      <h2>Appliance Usage Details</h2>
      ${table}
    </body></html>
  `);
  w.document.close();
  w.focus();
  w.print();
}

/* -------------------- INIT -------------------- */
document.addEventListener('DOMContentLoaded', () => {
  renderApplianceRows();
  calculatePower(); // keeps suggestions hidden until selection

  const resetBtn = document.getElementById('resetButton');
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      renderApplianceRows();
      calculatePower();
      const rec = document.getElementById('recommendation');
      if (rec) rec.innerHTML = ''; // no suggestions after reset
    });
  }
  const printBtn = document.getElementById('printButton');
  if (printBtn) printBtn.addEventListener('click', printResults);
});

/* ---------- Helpers already in-file (ensure these exist) ---------- */
// normalizeKey(name) { ... }
// getAffiliateLink(name) { ... }
// effectiveSurge(p), isRapidFamily(p), isTrailFamily(p), isCompatible(p, running, starting, kwh) ...

// Helper: normalize keys for robust comparisons
function normalizeKey(s) {
  return String(s || '').toLowerCase().replace(/[^a-z0-9]/g, '');
}

// Helper: get affiliate link (case/format tolerant)
function getAffiliateLink(name) {
  if (!name) return '#';
  const keys = Object.keys(productAffiliateLinks || {});
  // direct case-insensitive match
  let match = keys.find(k => k.toLowerCase() === name.toLowerCase());
  if (match) return productAffiliateLinks[match];
  // normalized match (ignores spaces/punctuation)
  match = keys.find(k => normalizeKey(k) === normalizeKey(name));
  if (match) return productAffiliateLinks[match];
  return '#';
}

// Export core functions/globals to window so HTML loader can detect them reliably
(function exportGlobals() {
  if (typeof window === 'undefined') return;
  try {
    if (typeof renderApplianceRows === 'function') window.renderApplianceRows = renderApplianceRows;
    if (typeof calculatePower === 'function') window.calculatePower = calculatePower;
    if (typeof updateRecommendations === 'function') window.updateRecommendations = updateRecommendations;
    window.normalizeKey = normalizeKey;
    window.getAffiliateLink = getAffiliateLink;
    if (typeof buildDefaultWattages === 'function') window.buildDefaultWattages = buildDefaultWattages;
    if (typeof buildMergedOptions === 'function') window.buildMergedOptions = buildMergedOptions;
    if (typeof DEFAULT_WATTAGES !== 'undefined') window.DEFAULT_WATTAGES = DEFAULT_WATTAGES;
    if (typeof MERGED_APPLIANCE_OPTIONS !== 'undefined') window.MERGED_APPLIANCE_OPTIONS = MERGED_APPLIANCE_OPTIONS;
  } catch (err) {
    console.warn('Export globals error (non-fatal):', err);
  }
})();
