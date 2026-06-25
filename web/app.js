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
  "partly-cloudy-day": "cloud.png",
  "partly-cloudy-night": "cloud.png",
  fog: "cloud.png",
};
const DEFAULT_ICON = "cloud.png";

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
  nextUpdate: "--:--",
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
  setText("next-update", `Next update ${data.nextUpdate}`);

  const icon = document.getElementById("condition-icon");
  icon.src = `/imgs/${iconFor(data.condition)}`;
  icon.alt = data.condition || "";
}

async function load() {
  const panel = document.getElementById("panel");
  try {
    const res = await fetch("/api/forecast");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    render(await res.json());
    panel.dataset.state = "ready";
  } catch (err) {
    render({ ...OFFLINE_DATA, summary: `Offline: ${err.message}` });
    panel.dataset.state = "offline";
  }
}

load();
