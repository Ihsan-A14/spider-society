// =====================================================
// UI EFFECTS (your existing stuff)
// =====================================================

// --- SCROLL REVEALS ---
const revealEls = document.querySelectorAll(".reveal");
const io = new IntersectionObserver(
  (entries) => {
    for (const e of entries) {
      if (e.isIntersecting) {
        e.target.classList.add("in");
        io.unobserve(e.target);
      }
    }
  },
  { threshold: 0.12 }
);
revealEls.forEach((el) => io.observe(el));

// --- PARALLAX (simple, smooth) ---
const hero = document.querySelector(".hero");
const parallaxTargets = document.querySelectorAll("[data-parallax]");

function onScroll() {
  const y = window.scrollY || 0;

  parallaxTargets.forEach((el) => {
    const speed = Number(el.getAttribute("data-parallax")) || 0.15;
    el.style.transform = `translateY(${y * speed}px)`;
  });

  if (hero) hero.style.transform = `translateY(${y * 0.03}px)`;
}

window.addEventListener("scroll", onScroll, { passive: true });
onScroll();

document.querySelectorAll(".panel")[1]?.classList.add("loaded");

// =====================================================
// LOADING OVERLAY: "Flaming" + flying 🔥
// (No HTML changes needed; injected via JS)
// =====================================================

function ensureFlamingOverlay() {
  if (document.getElementById("flamingOverlay")) return;

  const overlay = document.createElement("div");
  overlay.id = "flamingOverlay";
  overlay.setAttribute("aria-hidden", "true");
  overlay.style.cssText = `
    position: fixed;
    inset: 0;
    display: none;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    gap: 18px;
    z-index: 9999;
    background: rgba(255,255,255,0.72);
    backdrop-filter: blur(10px);
  `;

  const title = document.createElement("div");
  title.textContent = "Flaming";
  title.style.cssText = `
    font-family: 'Bebas Neue', system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
    font-size: clamp(64px, 9vw, 140px);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: rgba(0,0,0,0.86);
    text-shadow: 0 10px 40px rgba(0,0,0,0.12);
  `;

  const lane = document.createElement("div");
  lane.id = "flameLane";
  lane.style.cssText = `
    position: relative;
    width: min(900px, 92vw);
    height: 140px;
    overflow: hidden;
    border-radius: 18px;
    border: 1px dashed rgba(0,0,0,0.16);
    background: rgba(255,255,255,0.55);
  `;

  // Keyframes (inject once)
  const style = document.createElement("style");
style.textContent = `
  @keyframes flameFly {
    0%   { transform: translate(var(--x0), var(--y)) rotate(var(--r)); opacity: 0; }
    10%  { opacity: 1; }
    90%  { opacity: 1; }
    100% { transform: translate(var(--x1), var(--y)) rotate(calc(var(--r) * -1)); opacity: 0; }
  }
`;

  document.head.appendChild(style);

  overlay.appendChild(title);
  overlay.appendChild(lane);
  document.body.appendChild(overlay);
}

let flameTimer = null;
let flameCleanupTimer = null;

function spawnFlame() {
  const lane = document.getElementById("flameLane");
  if (!lane) return;

  const emoji = document.createElement("div");
  emoji.textContent = "🔥";

  // Randomize size, lane position, rotation, speed
  const size = 24 + Math.floor(Math.random() * 40); // 24..64
  const y = 8 + Math.floor(Math.random() * 96);     // within 140px lane
  const r = -25 + Math.floor(Math.random() * 51);   // -25..25 deg
  const dur = 900 + Math.floor(Math.random() * 900); // 0.9s..1.8s

  emoji.style.cssText = `
    position: absolute;
    left: 0;
    top: 0;
    font-size: ${size}px;
    line-height: 1;
    will-change: transform, opacity;
    --y: ${y}px;
    --r: ${r}deg;
    animation: flameFly ${dur}ms linear forwards;
    filter: drop-shadow(0 10px 18px rgba(0,0,0,0.12));
  `;

  lane.appendChild(emoji);
  emoji.addEventListener("animationend", () => emoji.remove());
}

function showFlamingOverlay() {
  ensureFlamingOverlay();

  const overlay = document.getElementById("flamingOverlay");
  overlay.style.display = "flex";

  // Start spawning flames
  if (flameCleanupTimer) clearTimeout(flameCleanupTimer);
  if (flameTimer) clearInterval(flameTimer);

  // burst
  for (let i = 0; i < 10; i++) setTimeout(spawnFlame, i * 60);

  flameTimer = setInterval(() => {
    // spawn 1-3 flames per tick
    const count = 1 + Math.floor(Math.random() * 3);
    for (let i = 0; i < count; i++) spawnFlame();
  }, 160);
}

function hideFlamingOverlay() {
  const overlay = document.getElementById("flamingOverlay");
  if (!overlay) return;

  if (flameTimer) {
    clearInterval(flameTimer);
    flameTimer = null;
  }

  // Give remaining animations a moment, then hide
  flameCleanupTimer = setTimeout(() => {
    overlay.style.display = "none";

    // clean any leftover flames
    const lane = document.getElementById("flameLane");
    if (lane) lane.querySelectorAll("div").forEach((n) => n.remove());
  }, 250);
}

// =====================================================
// MEME GENERATION (Frontend -> FastAPI -> Image)
// =====================================================

const API_BASE = "http://127.0.0.1:8000";

// Elements
const drop = document.getElementById("drop");
const fileInput = document.getElementById("file");
const pickBtn = document.getElementById("pickBtn");
const fileNameEl = document.getElementById("fileName");

const previewImg = document.getElementById("preview");
const previewEmpty = document.getElementById("previewEmpty");

const resultImg = document.getElementById("result");
const resultEmpty = document.getElementById("resultEmpty");

const generateBtn = document.getElementById("generate");
const resetBtn = document.getElementById("reset");
const statusEl = document.getElementById("status");
const downloadA = document.getElementById("download");

const intensitySel = document.getElementById("intensity");

// Helpers
function setStatus(msg) {
  if (statusEl) statusEl.textContent = msg || "";
}

function setPreview(file) {
  const url = URL.createObjectURL(file);

  previewImg.src = url;
  previewImg.style.display = "block";

  previewEmpty.style.display = "none";
}

function clearPreview() {
  previewImg.style.display = "none";
  previewImg.removeAttribute("src");
  previewEmpty.style.display = "block";
}

function setResultFromBlob(blob) {
  const url = URL.createObjectURL(blob);

  resultImg.src = url;
  resultImg.style.display = "block";
  resultEmpty.style.display = "none";

  downloadA.href = url;
  downloadA.style.display = "inline";
}

function clearResult() {
  resultImg.style.display = "none";
  resultImg.removeAttribute("src");
  resultEmpty.style.display = "block";

  downloadA.style.display = "none";
  downloadA.removeAttribute("href");
}

function resetUI() {
  if (fileInput) fileInput.value = "";
  if (fileNameEl) fileNameEl.textContent = "No file selected";

  clearPreview();
  clearResult();

  if (generateBtn) generateBtn.disabled = true;
  if (resetBtn) resetBtn.disabled = true;

  setStatus("");
}

// ONE clean set of "open file picker" listeners
pickBtn?.addEventListener("click", (e) => {
  e.preventDefault();
  e.stopPropagation();
  fileInput?.click();
});

fileInput?.addEventListener("click", (e) => {
  e.stopPropagation();
});

drop?.addEventListener("click", (e) => {
  if (e.target.closest("button") || e.target === fileInput) return;
  fileInput?.click();
});

// File selected -> show preview, enable buttons
fileInput?.addEventListener("change", () => {
  if (!fileInput.files?.length) return;

  const file = fileInput.files[0];
  fileNameEl.textContent = file.name;

  setPreview(file);

  generateBtn.disabled = false;
  resetBtn.disabled = false;

  setStatus("Ready to roast.");
});

// Reset
resetBtn?.addEventListener("click", (e) => {
  e.preventDefault();
  resetUI();
});

// Generate Meme (with Flaming overlay)
generateBtn?.addEventListener("click", async (e) => {
  e.preventDefault();

  if (!fileInput.files?.length) {
    alert("Upload an image first!");
    return;
  }

  const file = fileInput.files[0];
  const intensity = intensitySel?.value || "medium";

  clearResult();

  generateBtn.disabled = true;
  setStatus("Cooking your meme... 🔥");

  // ✅ show loading overlay
  showFlamingOverlay();

  const form = new FormData();
  form.append("image", file);
  form.append("intensity", intensity);
  form.append("top_text", "CS student debugging");
  form.append("bot_text", "Adds print() everywhere");

  try {
    const res = await fetch(`${API_BASE}/meme`, {
      method: "POST",
      body: form,
    });

    if (!res.ok) {
      const msg = await res.text().catch(() => "");
      throw new Error(`Backend error ${res.status}: ${msg}`);
    }

    const blob = await res.blob();
    if (!blob.type.startsWith("image/")) {
      throw new Error(`Expected image/* but got ${blob.type || "unknown"}`);
    }

    setResultFromBlob(blob);
    setStatus("Done ✅");
  } catch (err) {
    console.error(err);
    clearResult();
    setStatus("Failed 💀 Check backend terminal + CORS.");
  } finally {
    // ✅ hide overlay
    hideFlamingOverlay();
    generateBtn.disabled = false;
  }
});

// Start clean
resetUI();
