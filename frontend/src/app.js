// =====================================================
// 1. UI EFFECTS & SCROLL REVEALS (Visuals)
// =====================================================

// Reveal elements on scroll
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

// Parallax Effect
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


// =====================================================
// 2. FLAMING OVERLAY ENGINE (The Fire Effect)
// =====================================================

function ensureFlamingOverlay() {
  if (document.getElementById("flamingOverlay")) return;

  const overlay = document.createElement("div");
  overlay.id = "flamingOverlay";
  overlay.style.cssText = `
    position: fixed; inset: 0; display: none;
    align-items: center; justify-content: center; flex-direction: column;
    gap: 18px; z-index: 9999; background: rgba(255,255,255,0.85);
    backdrop-filter: blur(10px);
  `;

  const title = document.createElement("div");
  title.textContent = "ROASTING...";
  title.style.cssText = `
    font-family: 'Bebas Neue', sans-serif; font-size: clamp(60px, 8vw, 100px);
    color: #111; letter-spacing: 2px;
  `;

  const lane = document.createElement("div");
  lane.id = "flameLane";
  lane.style.cssText = `
    position: relative; width: 100%; max-width: 600px; height: 140px;
    overflow: hidden; border-radius: 12px;
  `;

  // Inject CSS Animation for flames
  if (!document.getElementById("flameStyle")) {
    const style = document.createElement("style");
    style.id = "flameStyle";
    style.textContent = `
      @keyframes flameFly {
        0%   { transform: translate(0px, var(--y)) rotate(var(--r)); opacity: 0; }
        10%  { opacity: 1; }
        90%  { opacity: 1; }
        100% { transform: translate(100cqw, var(--y)) rotate(calc(var(--r) * -1)); opacity: 0; }
      }
    `;
    document.head.appendChild(style);
  }

  overlay.appendChild(title);
  overlay.appendChild(lane);
  document.body.appendChild(overlay);
}

let flameTimer = null;

function spawnFlame() {
  const lane = document.getElementById("flameLane");
  if (!lane) return;

  const emoji = document.createElement("div");
  emoji.textContent = "🔥";
  
  const size = 30 + Math.random() * 50; 
  const y = Math.random() * 80;       
  const r = -30 + Math.random() * 60; 
  const dur = 1000 + Math.random() * 1000;

  emoji.style.cssText = `
    position: absolute; left: -50px; top: 0;
    font-size: ${size}px; line-height: 1;
    --y: ${y}px; --r: ${r}deg;
    animation: flameFly ${dur}ms linear forwards;
    container-type: inline-size;
  `;

  lane.appendChild(emoji);
  emoji.addEventListener("animationend", () => emoji.remove());
}

function showFlamingOverlay() {
  ensureFlamingOverlay();
  document.getElementById("flamingOverlay").style.display = "flex";
  
  // Burst
  for(let i=0; i<10; i++) setTimeout(spawnFlame, i*100);
  // Stream
  flameTimer = setInterval(spawnFlame, 200);
}

function hideFlamingOverlay() {
  const overlay = document.getElementById("flamingOverlay");
  if (overlay) overlay.style.display = "none";
  if (flameTimer) clearInterval(flameTimer);
}


// =====================================================
// 3. MAIN LOGIC (Connects HTML to Python)
// =====================================================

const API_BASE = "http://127.0.0.1:8000";

// --- Select DOM Elements based on YOUR HTML IDs ---
const fileInput = document.getElementById("file");
const dropZone = document.getElementById("drop");
const pickBtn = document.getElementById("pickBtn");
const fileNameEl = document.getElementById("fileName");
const intensitySelect = document.getElementById("intensity");

const generateBtn = document.getElementById("generate");
const resetBtn = document.getElementById("reset");

const previewImg = document.getElementById("preview");
const previewEmpty = document.getElementById("previewEmpty");
const resultImg = document.getElementById("result");
const resultEmpty = document.getElementById("resultEmpty");
const downloadLink = document.getElementById("download");
const statusEl = document.getElementById("status");

// --- Helper Functions ---

function setStatus(msg) {
  if (statusEl) statusEl.textContent = msg;
}

function showPreview(file) {
  const url = URL.createObjectURL(file);
  previewImg.src = url;
  previewImg.style.display = "block";
  previewEmpty.style.display = "none";
  
  // Enable buttons
  generateBtn.disabled = false;
  resetBtn.disabled = false;
}

function clearAll() {
  fileInput.value = "";
  fileNameEl.textContent = "No file selected";
  
  // Reset Preview
  previewImg.src = "";
  previewImg.style.display = "none";
  previewEmpty.style.display = "block";
  
  // Reset Result
  resultImg.src = "";
  resultImg.style.display = "none";
  resultEmpty.style.display = "block";
  
  // Hide Download
  downloadLink.style.display = "none";
  
  // Disable Buttons
  generateBtn.disabled = true;
  resetBtn.disabled = true;
  
  setStatus("");
}

// --- Event Listeners ---

// 1. File Selection Logic
// Trigger file input when clicking "Choose image" or Drop zone
pickBtn?.addEventListener("click", (e) => {
    e.preventDefault(); 
    fileInput.click();
});

dropZone?.addEventListener("click", (e) => {
    // Prevent triggering if clicking specific internal elements
    if(e.target === pickBtn || e.target === fileInput) return;
    fileInput.click();
});

// Handle File Change
fileInput?.addEventListener("change", () => {
  if (fileInput.files.length > 0) {
    const file = fileInput.files[0];
    fileNameEl.textContent = file.name;
    showPreview(file);
    setStatus("Ready to roast.");
  }
});

// 2. Reset Logic
resetBtn?.addEventListener("click", clearAll);

// 3. Generate Logic (The Bridge)
generateBtn?.addEventListener("click", async (e) => {
  // 🛑 STOP PAGE RELOAD
  e.preventDefault();
  
  const file = fileInput.files[0];
  if (!file) {
      alert("Please select a file first.");
      return;
  }

  const intensity = intensitySelect.value; // mild, medium, savage

  // UI State: Loading
  setStatus("Cooking... 🔥");
  showFlamingOverlay();
  generateBtn.disabled = true;
  resultImg.style.display = "none";
  downloadLink.style.display = "none";

  // Prepare Data
  const formData = new FormData();
  formData.append("file", file);          // Backend expects 'file'
  formData.append("roast_level", intensity); // Backend expects 'roast_level'

  try {
    // --- CALL PYTHON API ---
    const res = await fetch(`${API_BASE}/roast`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(errText || "Server Error");
    }

    // Process Image Response
    const blob = await res.blob();
    const resultUrl = URL.createObjectURL(blob);

    // Show Result
    resultImg.src = resultUrl;
    resultImg.style.display = "block";
    resultEmpty.style.display = "none";
    
    // Setup Download Link
    downloadLink.href = resultUrl;
    downloadLink.style.display = "inline-block";
    
    setStatus("Roast Served! 💀");

  } catch (err) {
    console.error(err);
    alert("Roast failed: " + err.message);
    setStatus("Error ❌ Check Backend.");
  } finally {
    hideFlamingOverlay();
    generateBtn.disabled = false;
  }
});