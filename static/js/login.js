document.addEventListener('DOMContentLoaded', () => {
  const pwToggle = document.getElementById('pw-toggle');
  const pwInput = document.getElementById('id_password');
  if (!pwToggle || !pwInput) return;

  pwToggle.addEventListener('click', () => {
    const isPwd = pwInput.getAttribute('type') === 'password';
    pwInput.setAttribute('type', isPwd ? 'text' : 'password');
    pwToggle.textContent = isPwd ? '🙈' : '👁️';
  });
});

document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("forgetModal");
    const overlay = modal.querySelector(".forgetpassword-modal__overlay");
    const closeButtons = modal.querySelectorAll("[data-close-modal]");

    // OPEN MODAL when clicking "Forgot password?"
    document.addEventListener("click", function (e) {
        if (e.target.closest(".forgot-link")) {
            e.preventDefault();
            openForgetModal();
        }
    });

    function openForgetModal() {
        modal.classList.add("forgetpassword-modal--open");
        modal.setAttribute("aria-hidden", "false");

        // Focus first input
        const firstInput = modal.querySelector("input");
        if (firstInput) firstInput.focus();
    }

    function closeForgetModal() {
        modal.classList.remove("forgetpassword-modal--open");
        modal.setAttribute("aria-hidden", "true");
    }

    // Close when clicking overlay or close buttons
    overlay.addEventListener("click", closeForgetModal);
    closeButtons.forEach(btn => {
        btn.addEventListener("click", closeForgetModal);
    });

    // Close on ESC key
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && modal.classList.contains("forgetpassword-modal--open")) {
            closeForgetModal();
        }
    });
});
