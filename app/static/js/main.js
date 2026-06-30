"use strict";

/* =====================================================================
   main.js — Citylight Sindhi Samaj Marriage Bureau
   POWERED BY SERENIA UPTIME BOTS | TECH SERENIA
   ===================================================================== */

document.addEventListener("DOMContentLoaded", function () {

  /* ── 1. Dark / Light theme toggle ─────────────────────────────────── */
  const root = document.documentElement;
  const toggleBtn = document.getElementById("themeToggle");
  let theme = sessionStorage.getItem("cssmb_theme") || "light";
  root.setAttribute("data-theme", theme);

  function updateThemeIcon() {
    if (!toggleBtn) return;
    toggleBtn.innerHTML = theme === "dark"
      ? '<i class="bi bi-sun"></i>'
      : '<i class="bi bi-moon-stars"></i>';
  }
  updateThemeIcon();

  if (toggleBtn) {
    toggleBtn.addEventListener("click", function () {
      theme = theme === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", theme);
      sessionStorage.setItem("cssmb_theme", theme);
      updateThemeIcon();
    });
  }

  /* ── 2. Auto-dismiss flash alerts after 6 s ─────────────────────── */
  document.querySelectorAll(".alert.fade.show").forEach(function (el) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      if (bsAlert) bsAlert.close();
    }, 6000);
  });

  /* ── 3. Confirm dialogs on [data-confirm] forms ──────────────────── */
  document.querySelectorAll("form[data-confirm]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (!confirm(form.getAttribute("data-confirm"))) {
        e.preventDefault();
      }
    });
  });

  /* ── 4. Drag-and-drop file zones ─────────────────────────────────── */
  document.querySelectorAll(".drop-zone").forEach(function (zone) {
    const input = zone.querySelector("input[type=file]");
    const label = zone.querySelector(".drop-zone-label");
    if (!input) return;

    zone.addEventListener("click", function () { input.click(); });

    ["dragenter", "dragover"].forEach(function (ev) {
      zone.addEventListener(ev, function (e) { e.preventDefault(); zone.classList.add("drag-over"); });
    });
    ["dragleave", "drop"].forEach(function (ev) {
      zone.addEventListener(ev, function () { zone.classList.remove("drag-over"); });
    });

    zone.addEventListener("drop", function (e) {
      e.preventDefault();
      if (e.dataTransfer.files.length) {
        input.files = e.dataTransfer.files;
        updateLabel(input, label);
        previewFiles(input, zone);
      }
    });

    input.addEventListener("change", function () {
      updateLabel(input, label);
      previewFiles(input, zone);
    });
  });

  function updateLabel(input, label) {
    if (!label) return;
    if (input.files.length > 1) {
      label.textContent = input.files.length + " files selected";
    } else if (input.files.length === 1) {
      label.textContent = input.files[0].name;
    }
  }

  function previewFiles(input, zone) {
    let grid = zone.querySelector(".photo-preview-grid");
    if (!grid) {
      grid = document.createElement("div");
      grid.className = "photo-preview-grid mt-2";
      zone.appendChild(grid);
    }
    grid.innerHTML = "";
    Array.from(input.files).slice(0, 12).forEach(function (file) {
      if (!file.type.startsWith("image/")) return;
      const img = document.createElement("img");
      const reader = new FileReader();
      reader.onload = function (e) { img.src = e.target.result; };
      reader.readAsDataURL(file);
      grid.appendChild(img);
    });
  }

  /* ── 5. Profile compare checkbox guard (max 2) ───────────────────── */
  document.querySelectorAll("[data-compare-checkbox]").forEach(function (cb) {
    cb.addEventListener("change", function () {
      const checked = document.querySelectorAll("[data-compare-checkbox]:checked");
      if (checked.length > 2) {
        cb.checked = false;
        alert("You can only compare 2 profiles at a time.");
      }
      const btn = document.getElementById("compareBtn");
      if (!btn) return;
      const ids = Array.from(document.querySelectorAll("[data-compare-checkbox]:checked"))
        .map(function (c) { return c.value; });
      if (ids.length === 2) {
        btn.href = btn.dataset.baseUrl + "?a=" + ids[0] + "&b=" + ids[1];
        btn.classList.remove("disabled");
      } else {
        btn.classList.add("disabled");
      }
    });
  });

  /* ── 6. Keyboard shortcut: Ctrl+K / Cmd+K → global search ──────── */
  document.addEventListener("keydown", function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key === "k") {
      e.preventDefault();
      const searchInput = document.querySelector("input[name='q']");
      if (searchInput) { searchInput.focus(); searchInput.select(); }
    }
  });

  /* ── 7. Live DOB → age display on registration form ─────────────── */
  const dobField = document.getElementById("dob");
  const ageDisplay = document.getElementById("age_display");
  if (dobField && ageDisplay) {
    function calcAge() {
      const dob = new Date(dobField.value);
      if (!isNaN(dob.getTime())) {
        const today = new Date();
        let age = today.getFullYear() - dob.getFullYear();
        const m = today.getMonth() - dob.getMonth();
        if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) age--;
        ageDisplay.textContent = age > 0 ? age + " years" : "";
      }
    }
    dobField.addEventListener("change", calcAge);
    calcAge();
  }

  /* ── 8. Bootstrap Tooltip initialisation ──────────────────────────── */
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
    new bootstrap.Tooltip(el);
  });

  /* ── 9. Auto-submit filter selects ──────────────────────────────── */
  document.querySelectorAll("[data-auto-submit]").forEach(function (el) {
    el.addEventListener("change", function () {
      const form = el.closest("form");
      if (form) form.submit();
    });
  });

  /* ── 10. Highlight active sidebar link ───────────────────────────── */
  const currentPath = window.location.pathname;
  document.querySelectorAll(".dash-sidebar .nav-link").forEach(function (link) {
    const href = link.getAttribute("href");
    if (href && href !== "/" && currentPath.startsWith(href)) {
      link.classList.add("active");
    }
  });

});
