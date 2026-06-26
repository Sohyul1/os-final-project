document.addEventListener("DOMContentLoaded", () => {

    initializeDesktop();

    initializeStartButton();

    initializeClock();

});


/* ==============================
   Desktop Icons
============================== */

function initializeDesktop() {

    const icons = document.querySelectorAll(".desktop-icon");

    icons.forEach(icon => {

        let clickTimer = null;

        icon.addEventListener("click", function (event) {

            event.preventDefault();

            if (clickTimer) {
                clearTimeout(clickTimer);
                clickTimer = null;
                return;
            }

            clickTimer = setTimeout(() => {
                clearSelectedIcons();
                icon.classList.add("selected");
                clickTimer = null;
            }, 250);

        });

        icon.addEventListener("dblclick", function (event) {

            event.preventDefault();

            if (clickTimer) {
                clearTimeout(clickTimer);
                clickTimer = null;
            }

            window.location.href = icon.href;

        });

    });

    document.addEventListener("click", function (event) {

        if (!event.target.closest(".desktop-icon")) {
            clearSelectedIcons();
        }

    });

}


function clearSelectedIcons() {

    document.querySelectorAll(".desktop-icon").forEach(icon => {
        icon.classList.remove("selected");
    });

}


/* ==============================
   Start Button — Confirm Return to Desktop
============================== */

function initializeStartButton() {

    const startButton = document.getElementById("start-button");

    if (!startButton) return;

    // Build the overlay + dialog once and append to body
    const overlay = document.createElement("div");
    overlay.id = "start-confirm-overlay";
    overlay.className = "start-menu-overlay";

    overlay.innerHTML = `
        <div class="coming-soon-dialog window">
            <div class="title-bar">
                <div class="title-bar-text">Windows 95</div>
                <div class="title-bar-controls">
                    <button aria-label="Close" id="start-confirm-close-btn"></button>
                </div>
            </div>
            <div class="window-body coming-soon-body">
                <h2>Return to Desktop?</h2>
                <p>Any unsaved progress in this window<br>will be lost. Continue?</p>
                <div class="start-confirm-actions">
                    <button class="cs-ok-btn" id="start-confirm-yes-btn">Yes</button>
                    <button class="cs-ok-btn" id="start-confirm-no-btn">No</button>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(overlay);

    function openDialog() {
        overlay.classList.add("show");
        startButton.classList.add("active");
    }

    function closeDialog() {
        overlay.classList.remove("show");
        startButton.classList.remove("active");
    }

    startButton.addEventListener("click", function (event) {
        event.stopPropagation();
        const isOpen = overlay.classList.contains("show");
        isOpen ? closeDialog() : openDialog();
    });

    document.getElementById("start-confirm-close-btn").addEventListener("click", closeDialog);
    document.getElementById("start-confirm-no-btn").addEventListener("click", closeDialog);

    document.getElementById("start-confirm-yes-btn").addEventListener("click", function () {
        window.location.href = "/";
    });

    // Close when clicking outside the dialog
    overlay.addEventListener("click", function (event) {
        if (!event.target.closest(".coming-soon-dialog")) {
            closeDialog();
        }
    });

}


/* ==============================
   Realtime Clock
============================== */

function initializeClock() {

    const clock = document.getElementById("clock");

    if (!clock) return;

    function updateClock() {

        const now = new Date();
        let hours = now.getHours();
        let minutes = now.getMinutes();
        const ampm = hours >= 12 ? "PM" : "AM";

        hours = hours % 12 || 12;
        minutes = minutes.toString().padStart(2, "0");

        clock.textContent = `${hours}:${minutes} ${ampm}`;

    }

    updateClock();
    setInterval(updateClock, 1000);

}


/* ==============================
   Taskbar App Buttons
============================== */

function addTaskbarApp(id, label, iconSrc, onClick) {

    const container = document.getElementById("taskbar-apps");

    if (!container) return;

    if (document.getElementById(`taskbar-app-${id}`)) return;

    const btn = document.createElement("button");

    btn.id = `taskbar-app-${id}`;
    btn.className = "taskbar-app-btn";
    btn.title = label;

    if (iconSrc) {
        const img = document.createElement("img");
        img.src = iconSrc;
        img.alt = "";
        btn.appendChild(img);
    }

    const span = document.createElement("span");
    span.textContent = label;
    btn.appendChild(span);

    btn.addEventListener("click", () => {
        setActiveTaskbarApp(id);
        if (typeof onClick === "function") onClick();
    });

    container.appendChild(btn);

}


function setActiveTaskbarApp(id) {

    document.querySelectorAll(".taskbar-app-btn").forEach(btn => {
        btn.classList.remove("active");
    });

    const btn = document.getElementById(`taskbar-app-${id}`);
    if (btn) btn.classList.add("active");

}


function removeTaskbarApp(id) {

    const btn = document.getElementById(`taskbar-app-${id}`);
    if (btn) btn.remove();

}

/* ═══════════════════════════════
   STARTUP SCREEN LOGIC
   ═══════════════════════════════ */
(function () {
  const overlay = document.getElementById('startup-overlay');
  if (!overlay) return;

    if (sessionStorage.getItem('win95_booted')) {
    return;
  }

  overlay.style.display = 'flex';

  let dismissed = false;

  function dismiss() {
    if (dismissed) return;
    dismissed = true;

    sessionStorage.setItem('win95_booted', '1');

    // Play startup chime
    const audio = new Audio('https://www.myinstants.com/media/sounds/windows-95-startup.mp3');
    audio.volume = 0.6;
    audio.play().catch(() => {});

    // Fade out overlay
    overlay.classList.add('hide');
    setTimeout(() => overlay.remove(), 900);
  }

  // Wait for DOM to be ready before attaching listener
  document.addEventListener('DOMContentLoaded', function () {
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') dismiss();
    });
    document.addEventListener('mousedown', function (e) {
      if (e.button === 0) dismiss();
    });
  });
})();