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
