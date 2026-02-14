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

  // hide empty overlay
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
  resultImg.style.display = "block";      // show ONLY on success
  resultEmpty.style.display = "none";     // remove placeholder

  downloadA.href = url;
  downloadA.style.display = "inline";
}

function clearResult() {
  resultImg.style.display = "none";       // hide so no broken icon
  resultImg.removeAttribute("src");

  // show placeholder text
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

// =====================================================
// ONE clean set of "open file picker" listeners
// (prevents the "upload twice" issue)
// =====================================================

pickBtn?.addEventListener("click", (e) => {
  e.preventDefault();
  e.stopPropagation();
  fileInput?.click();
});

fileInput?.addEventListener("click", (e) => {
  e.stopPropagation();
});

drop?.addEventListener("click", (e) => {
  // Only trigger if user clicked the drop area itself (not button/input)
  if (e.target.closest("button") || e.target === fileInput) return;
  fileInput?.click();
});

// =====================================================
// File selected -> show preview, enable buttons
// =====================================================

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

// =====================================================
// Generate Meme
// - Keep placeholder visible initially
// - Show image ONLY after successful response
// =====================================================

generateBtn?.addEventListener("click", async (e) => {
  e.preventDefault();

  if (!fileInput.files?.length) {
    alert("Upload an image first!");
    return;
  }

  const file = fileInput.files[0];
  const intensity = intensitySel?.value || "medium";

  // user clicked generate: hide previous result image (no broken icon)
  clearResult();
  // optional: hide placeholder while generating (comment out if you want it to stay)
  // resultEmpty.style.display = "none";

  generateBtn.disabled = true;
  setStatus("Cooking your meme... 🔥");

  const form = new FormData();
  form.append("image", file);
  form.append("intensity", intensity);     // only if backend accepts it
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

    // Safety: ensure it's actually an image
    if (!blob.type.startsWith("image/")) {
      throw new Error(`Expected image/* but got ${blob.type || "unknown"}`);
    }

    setResultFromBlob(blob);
    setStatus("Done ✅");
  } catch (err) {
    console.error(err);

    // show placeholder again, keep image hidden (no broken icon)
    clearResult();
    setStatus("Failed 💀 Check backend terminal + CORS.");
  } finally {
    generateBtn.disabled = false;
  }
});

// Start clean
resetUI();
