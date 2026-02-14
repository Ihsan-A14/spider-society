// --- SCROLL REVEALS ---
const revealEls = document.querySelectorAll(".reveal");
const io = new IntersectionObserver((entries) => {
  for (const e of entries) {
    if (e.isIntersecting) {
      e.target.classList.add("in");
      io.unobserve(e.target);
    }
  }
}, { threshold: 0.12 });

revealEls.forEach(el => io.observe(el));

// --- PARALLAX (simple, smooth) ---
const hero = document.querySelector(".hero");
const parallaxTargets = document.querySelectorAll("[data-parallax]");

function onScroll() {
  const y = window.scrollY || 0;

  parallaxTargets.forEach((el) => {
    const speed = Number(el.getAttribute("data-parallax")) || 0.15;
    el.style.transform = `translateY(${y * speed}px)`;
  });

  // tiny tilt on hero as you scroll (editorial feel)
  if (hero) hero.style.transform = `translateY(${y * 0.03}px)`;
}

window.addEventListener("scroll", onScroll, { passive: true });
onScroll();

document.querySelectorAll(".panel")[1]?.classList.add("loaded");

// =====================================================
// ✅ MEME GENERATION WIRING (Frontend -> FastAPI -> Image)
// =====================================================

const API_BASE = "http://127.0.0.1:8000";

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

// helper UI
function setStatus(msg) {
  if (statusEl) statusEl.textContent = msg || "";
}

function setPreview(file) {
  const url = URL.createObjectURL(file);
  previewImg.src = url;
  previewImg.style.display = "block";
  previewImg.style.visibility = "visible";
  previewImg.style.opacity = "1";
  previewImg.style.position = "relative";
  previewImg.style.zIndex = "2";

  previewEmpty.style.display = "none";
  previewEmpty.style.visibility = "hidden";
  previewEmpty.style.opacity = "0";
  previewEmpty.style.zIndex = "0";

  previewEmpty.style.display = "none";
}

function setResultFromBlob(blob) {
  const url = URL.createObjectURL(blob);
  resultImg.src = url;
  resultEmpty.style.display = "none";

  downloadA.href = url;
  downloadA.style.display = "inline";
}

function resetUI() {
  fileInput.value = "";
  fileNameEl.textContent = "No file selected";

  // preview
  previewImg.style.display = "none";
  previewImg.removeAttribute("src");
  previewEmpty.style.display = "block";
  previewEmpty.style.visibility = "visible";
  previewEmpty.style.opacity = "1";

  // result
  resultImg.removeAttribute("src");
  resultEmpty.style.display = "block";

  // download
  downloadA.style.display = "none";
  downloadA.removeAttribute("href");

  generateBtn.disabled = true;
  resetBtn.disabled = true;

  setStatus("");



  // --- ONE set of listeners for opening file picker ---

pickBtn?.addEventListener("click", (e) => {
  e.preventDefault();
  e.stopPropagation();
  fileInput.click();
});

fileInput?.addEventListener("click", (e) => {
  e.stopPropagation();
});

drop?.addEventListener("click", (e) => {
  // Only trigger if user clicked the drop area itself (not button/input)
  if (e.target.closest("button") || e.target === fileInput) return;
  fileInput.click();
});

  previewImg.style.display = "none";
  previewImg.removeAttribute("src");

  previewEmpty.style.display = "block";
  previewEmpty.style.visibility = "visible";
  previewEmpty.style.opacity = "1";

}


// When user selects a file
fileInput?.addEventListener("change", () => {
  if (!fileInput.files?.length) return;

  const file = fileInput.files[0];
  fileNameEl.textContent = file.name;

  setPreview(file);

  generateBtn.disabled = false;
  resetBtn.disabled = false;

  setStatus("Ready to roast.");
});

// Reset button
resetBtn?.addEventListener("click", resetUI);

// Generate meme
generateBtn?.addEventListener("click", async () => {
  if (!fileInput.files?.length) {
    alert("Upload an image first!");
    return;
  }

  const file = fileInput.files[0];
  const intensity = intensitySel?.value || "medium";

  generateBtn.disabled = true;
  setStatus("Cooking your meme... 🔥");

  const form = new FormData();
  form.append("image", file);
  form.append("intensity", intensity); // only works if your backend accepts it
  form.append("top_text", "CS student debugging"); // temp text
  form.append("bot_text", "Adds print() everywhere"); // temp text

  try {
    const res = await fetch(`${API_BASE}/meme`, {
      method: "POST",
      body: form
    });

    if (!res.ok) {
      const msg = await res.text().catch(() => "");
      throw new Error(`Backend error ${res.status}: ${msg}`);
    }

    const blob = await res.blob();
    setResultFromBlob(blob);

    setStatus("Done ✅");
  } catch (err) {
    console.error(err);
    setStatus("Failed 💀 Check backend terminal + CORS.");
  } finally {
    generateBtn.disabled = false;
  }
});

// Start clean
resetUI();
