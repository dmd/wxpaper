const ICONS = {
  "clear-day": "sun.png",
  "clear-night": "moon.png",
  rain: "rain.png",
  snow: "snow.png",
  sleet: "sleet.png",
  hail: "hail.png",
  thunderstorm: "storm.png",
  wind: "windmill.png",
  cloudy: "clouds.png",
  "partly-cloudy-day": "partly-cloudy-day.png",
  "partly-cloudy-night": "partly-cloudy-night.png",
  fog: "fog.png",
};
const DEFAULT_ICON = "clouds.png";

// trmnl renders the page from a blank base, so relative asset/fetch URLs can't
// be resolved there. Use absolute URLs against the deployment, except when
// previewing through the local dev server (webversion.py).
const IS_LOCAL = ["localhost", "127.0.0.1"].includes(location.hostname);
const BASE = IS_LOCAL ? "" : "https://3e.org/wxpaper/";

const OFFLINE_DATA = {
  tempNow: 0,
  tempHigh: 0,
  tempLow: 0,
  uv: 0,
  condition: "cloudy",
  summary: "",
  allowance: "—",
  weekday: "---",
  date: "--- --",
  lastUpdate: "--:--",
};

function formatTemp(value) {
  if (value >= 100) return "HI";
  if (value < 0) return "LO";
  return String(Math.round(value));
}

function formatUv(value) {
  if (value > 9) return "X";
  return String(Math.round(value));
}

function iconFor(condition) {
  return ICONS[condition] || DEFAULT_ICON;
}

function setText(id, text) {
  document.getElementById(id).textContent = text;
}

function render(data) {
  setText("temp-now", formatTemp(data.tempNow));
  setText("temp-high", formatTemp(data.tempHigh));
  setText("temp-low", formatTemp(data.tempLow));
  setText("uv", formatUv(data.uv));
  setText("weekday", data.weekday);
  setText("date", data.date);
  setText("summary", data.summary);
  setText("allowance", data.allowance);
  setText("last-update", `Last update ${data.lastUpdate}`);

  const icon = document.getElementById("condition-icon");
  icon.src = `${BASE}imgs/${iconFor(data.condition)}`;
  icon.alt = data.condition || "";
}

async function load() {
  const panel = document.getElementById("panel");
  try {
    const res = await fetch(`${BASE}forecast.py`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    render(await res.json());
    panel.dataset.state = "ready";
  } catch (err) {
    render({ ...OFFLINE_DATA, summary: `Offline: ${err.message}` });
    panel.dataset.state = "offline";
  }
}

function fitStage() {
  const panel = document.getElementById("panel");
  const scale = Math.min(window.innerWidth / 800, window.innerHeight / 480, 1);
  panel.style.transform = `scale(${scale})`;
}

document.getElementById("uv-icon").src = `${BASE}imgs/uv.png`;
load();
fitStage();
window.addEventListener("resize", fitStage);
