function openVehicleModal() {
    var modal = document.getElementById('addVehicleModal');
    modal.classList.add('show');
    modal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('modal-open');
}

function closeVehicleModal() {
    var modal = document.getElementById('addVehicleModal');
    modal.classList.remove('show');
    modal.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('modal-open');
}

// document.getElementById("add-vehicle-btn").addEventListener("click", function (e) {
//     e.preventDefault();
//     openVehicleModal();
// });

// document.querySelector(".modal-close").addEventListener("click", function () {
//     closeVehicleModal();
// });

function openVehicalsViewModal() {
    var modal = document.getElementById('view-vehicle-modal');
    modal.classList.add('show');
    modal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('modal-open');
}
function closeVehicalsViewModal() {
    var modal = document.getElementById('view-vehicle-modal');
    modal.classList.remove('show');
    modal.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('modal-open');
}
// document.getElementById("view-vehicle-details").addEventListener("click", function (e) {
//     e.preventDefault();
//     openVehicalsViewModal();
// });

// document.querySelector("#view-vehicle-modal .modal-close").addEventListener("click", function () {
//     closeVehicalsViewModal();
// });

document.addEventListener("DOMContentLoaded", function () {

    const addVehicleBtn = document.getElementById("add-vehicle-btn");
    if (addVehicleBtn) {
        addVehicleBtn.addEventListener("click", function (e) {
            e.preventDefault();
            openVehicleModal();
        });
    }

    const modalClose = document.querySelector(".modal-close");
    if (modalClose) {
        modalClose.addEventListener("click", closeVehicleModal);
    }

    const viewBtn = document.getElementById("view-vehicle-details");
    if (viewBtn) {
        viewBtn.addEventListener("click", function (e) {
            e.preventDefault();
            openVehicalsViewModal();
        });
    }

    const viewClose = document.querySelector("#view-vehicle-modal .modal-close");
    if (viewClose) {
        viewClose.addEventListener("click", closeVehicalsViewModal);
    }

});

function confirmDelete(type, id) {
    if (!confirm("Delete this item? This action cannot be undone.")) return;

    let url = "";
    let label = type === "driver" ? "Driver" : "Vehicle";

    if (type === "driver") {
        url = `/agency/driver/${id}/delete/`;
    } else if (type === "vehicle") {
        url = `/agency/vehicles/${id}/delete/`;
    }

    fetch(url, {
        method: "POST",
        headers: {
            "X-CSRFToken": document.getElementById("csrfToken").value,
            "X-Requested-With": "XMLHttpRequest"
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.ok) {
            // Remove row/card
            const el = document.querySelector(`[data-${type}-id="${id}"]`);
            if (el) el.remove();

            showToast(`${label} deleted successfully`, "success");
        } else {
            showToast(data.message || `Failed to delete ${label}`, "error");
        }
    })
    .catch(() => {
        showToast("Server error. Please try again.", "error");
    });
}

(function(){
    const dob = document.getElementById('driver_dob');
    const age = document.getElementById('driver_age');
    const dobWrapper = document.getElementById('dobWrapper');
    const ageWrapper = document.getElementById('ageWrapper');

    // Start: both disabled (keeps form markup explicit)
    dob.disabled = false;
    age.disabled = true;

    // Visual helper: add / remove "active" styling
    function setActiveWrapper(which) {
        dobWrapper.style.boxShadow = (which === 'dob') ? '0 0 0 3px rgba(13,110,253,0.12)' : '';
        ageWrapper.style.boxShadow = (which === 'age') ? '0 0 0 3px rgba(13,110,253,0.12)' : '';
    }

    // Click DOB wrapper → enable DOB, disable Age
    dobWrapper.addEventListener('click', () => {
        // enable DOB input
        dob.disabled = false;
        dob.focus();
        // disable age input and clear any previous focus
        age.disabled = true;
        // optional: clear age when switching to DOB so the computed age will be authoritative
        age.value = '';
        setActiveWrapper('dob');
    });

    // Click Age wrapper → enable Age, disable DOB
    ageWrapper.addEventListener('click', () => {
        age.disabled = false;
        age.focus();
        dob.disabled = true;
        // when enabling manual age entry, clear DOB so it's not conflicting
        dob.value = '';
        setActiveWrapper('age');
    });

    // When DOB changes, auto-calc age and fill it (age remains disabled)
    dob.addEventListener('change', function () {
        const val = this.value;
        if (!val) {
            age.value = '';
            return;
        }
        const dobDate = new Date(val);
        const today = new Date();

        // Prevent future DOBs
        if (dobDate > today) {
            alert('DOB cannot be in the future.');
            this.value = '';
            age.value = '';
            return;
        }

        let calc = today.getFullYear() - dobDate.getFullYear();
        const m = today.getMonth() - dobDate.getMonth();
        if (m < 0 || (m === 0 && today.getDate() < dobDate.getDate())) {
            calc--;
        }

        // sanity clamp
        if (calc < 0) calc = 0;
        if (calc > 150) calc = 150;

        age.value = calc;
    });
})();