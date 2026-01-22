const layout = {
  tempNow: [
    { x: 20, y: 20 },
    { x: 160, y: 20 },
  ],
  tempHigh: [
    { x: 310, y: 10 },
    { x: 390, y: 10 },
  ],
  tempLow: [
    { x: 310, y: 175 },
    { x: 390, y: 175 },
  ],
  icon: { x: 500, y: 160 },
  uvIcon: { x: 20, y: 470 },
  uvDigit: { x: 80, y: 310 },
  lastUpdate: { x: 20, y: 1 },
  nextUpdate: { x: 550, y: 1 },
  allowance: { x: 261, y: 530 },
  summary: { x: 20, y: 570 },
  weekday: { x: 310, y: 370 },
  date: { x: 280, y: 440 },
  dateBox: { x0: 260, y0: 360, x1: 455, y1: 520 },
};

const sampleData = {
  tempNow: 0,
  tempHigh: 0,
  tempLow: 0,
  uv: 0,
  condition: "partly-cloudy-day",
  summary: "Partly cloudy throughout the day.",
  lastUpdate: "08:43",
  nextUpdate: "12:43",
  weekday: "Tue",
  date: "Sep 17",
  allowance: "Allowance unavailable, -- days",
};

const iconMap = {
  "clear-day": "3SUN.BMP",
  "clear-night": "3NIGHT.BMP",
  "cloudy": "3CLOUD.BMP",
  "partly-cloudy-day": "3CLDAY.BMP",
  "partly-cloudy-night": "3CLDNT.BMP",
};

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function twoDig(value) {
  if (value >= 100) {
    return "HI";
  }
  if (value < 0) {
    return "LO";
  }
  const clamped = clamp(Math.round(value), 0, 99);
  return clamped.toString().padStart(2, "0");
}

function uvOneDig(value) {
  if (value > 9) {
    return "X";
  }
  return Math.round(value).toString();
}

function setPosition(el, x, y) {
  el.style.left = `${x}px`;
  el.style.top = `${y}px`;
}

function setDigit(el, size, char) {
  const safeChar = char.toString().toUpperCase();
  el.src = `/imgs/${size}_${safeChar}.BMP`;
  el.alt = safeChar;
}

function render(data) {
  const tempNow = twoDig(data.tempNow);
  setDigit(document.getElementById("temp-now-d0"), 300, tempNow[0]);
  setDigit(document.getElementById("temp-now-d1"), 300, tempNow[1]);

  const tempHigh = twoDig(data.tempHigh);
  setDigit(document.getElementById("temp-high-d0"), 165, tempHigh[0]);
  setDigit(document.getElementById("temp-high-d1"), 165, tempHigh[1]);

  const tempLow = twoDig(data.tempLow);
  setDigit(document.getElementById("temp-low-d0"), 165, tempLow[0]);
  setDigit(document.getElementById("temp-low-d1"), 165, tempLow[1]);

  setDigit(document.getElementById("uv-digit"), 165, uvOneDig(data.uv));

  const icon = iconMap[data.condition] || "3CLOUD.BMP";
  const iconEl = document.getElementById("weather-icon");
  iconEl.src = `/imgs/${icon}`;
  iconEl.alt = data.condition;

  document.getElementById("last-update").textContent = `Last update ${data.lastUpdate}`;
  document.getElementById("next-update").textContent = `Next update ${data.nextUpdate}`;
  document.getElementById("weekday").textContent = data.weekday;
  document.getElementById("date").textContent = data.date;
  document.getElementById("allowance").textContent = data.allowance;
  document.getElementById("summary").textContent = data.summary;

  setPosition(document.getElementById("last-update"), layout.lastUpdate.x, layout.lastUpdate.y);
  setPosition(document.getElementById("next-update"), layout.nextUpdate.x, layout.nextUpdate.y);

  layout.tempNow.forEach((pos, index) => {
    setPosition(document.getElementById(`temp-now-d${index}`), pos.x, pos.y);
  });

  layout.tempHigh.forEach((pos, index) => {
    setPosition(document.getElementById(`temp-high-d${index}`), pos.x, pos.y);
  });

  layout.tempLow.forEach((pos, index) => {
    setPosition(document.getElementById(`temp-low-d${index}`), pos.x, pos.y);
  });

  setPosition(iconEl, layout.icon.x, layout.icon.y);
  setPosition(document.getElementById("uv-icon"), layout.uvIcon.x, layout.uvIcon.y);
  setPosition(document.getElementById("uv-digit"), layout.uvDigit.x, layout.uvDigit.y);
  setPosition(document.getElementById("allowance"), layout.allowance.x, layout.allowance.y);
  setPosition(document.getElementById("summary"), layout.summary.x, layout.summary.y);
  setPosition(document.getElementById("weekday"), layout.weekday.x, layout.weekday.y);
  setPosition(document.getElementById("date"), layout.date.x, layout.date.y);

  const dateBox = document.getElementById("date-box");
  const boxWidth = layout.dateBox.x1 - layout.dateBox.x0;
  const boxHeight = layout.dateBox.y1 - layout.dateBox.y0;
  dateBox.style.left = `${layout.dateBox.x0}px`;
  dateBox.style.top = `${layout.dateBox.y0}px`;
  dateBox.style.width = `${boxWidth}px`;
  dateBox.style.height = `${boxHeight}px`;
}

function scaleScreen() {
  const screen = document.getElementById("screen");
  const scale = Math.min(window.innerWidth / 800, window.innerHeight / 480, 1);
  screen.style.transform = `scale(${scale})`;
}

async function loadData() {
  const layout = document.getElementById("layout");
  try {
    const response = await fetch("/api/forecast");
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const data = await response.json();
    render({ ...sampleData, ...data });
    layout.classList.remove("layout-hidden");
  } catch (err) {
    render({ ...sampleData, summary: `Offline: ${err.message}` });
    layout.classList.remove("layout-hidden");
  }
}

loadData();
scaleScreen();
window.addEventListener("resize", scaleScreen);
