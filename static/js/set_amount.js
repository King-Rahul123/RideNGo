document.addEventListener('DOMContentLoaded', function () {
    const vehicleSelect = document.getElementById('vehicleSelect');
    const amountForm = document.getElementById('amountForm');
    const vehicleIdInput = document.getElementById('vehicle_id');

    // Controls
    const modeFixed = document.getElementById('mode_fixed');
    const modeManual = document.getElementById('mode_manual');
    const fixedOptions = document.getElementById('fixedOptions');
    const manualNote = document.getElementById('manualNote');

    const fixedPerKm = document.getElementById('fixed_per_km');
    const fixedFlat = document.getElementById('fixed_flat');

    const blockPerKm = document.getElementById('block_per_km');
    const blockFlat = document.getElementById('block_flat');
    const postFlatExtra = document.getElementById('postFlatExtra');

    const amountPerKm = document.getElementById('amount_per_km');
    const flatAmount = document.getElementById('flat_amount');
    const flatMaxKm = document.getElementById('flat_max_km');
    const extraAfterFlat = document.getElementById('extra_after_flat_per_km');
    const saveBtn = document.getElementById('saveAmountBtn');

    // NEW: minimum KM input for Fixed -> Amount/KM
    const minKmInput = document.getElementById('min_km');

    // safe-guard: if element IDs changed in template, abort gracefully
    if (!amountForm) return;

    // initial hide/show states
    amountForm.style.display = 'none';
    if (fixedOptions) fixedOptions.style.display = 'block'; // default to visible (will be corrected by syncUI)
    if (blockFlat) blockFlat.style.display = 'none';
    if (postFlatExtra) postFlatExtra.style.display = 'none';
    if (manualNote) manualNote.style.display = 'none';

    // Helper: ensure UI state matches current selections
    function updateModeUI() {
        // If radios are missing, do nothing
        if (!modeFixed || !modeManual) return;

        if (modeFixed.checked) {
            if (fixedOptions) fixedOptions.style.display = 'block';
            if (manualNote) manualNote.style.display = 'none';
        } else if (modeManual.checked) {
            if (fixedOptions) fixedOptions.style.display = 'none';
            if (manualNote) manualNote.style.display = 'block';
        } else {
            // fallback - treat as fixed
            if (fixedOptions) fixedOptions.style.display = 'block';
            if (manualNote) manualNote.style.display = 'none';
        }
    }

    function updateFixedTypeUI() {
        if (fixedPerKm && fixedPerKm.checked) {
            // Show amount/km box (with min_km)
            if (blockPerKm) blockPerKm.style.display = "block";

            // Hide flat box
            if (blockFlat) blockFlat.style.display = "none";
            if (postFlatExtra) postFlatExtra.style.display = "none";
        }

        else if (fixedFlat && fixedFlat.checked) {
            // Hide per km section
            if (blockPerKm) blockPerKm.style.display = "none";

            // Show flat section
            if (blockFlat) blockFlat.style.display = "block";
            if (postFlatExtra) postFlatExtra.style.display = "block";
        } else {
            // defaults
            if (blockPerKm) blockPerKm.style.display = "block";
            if (blockFlat) blockFlat.style.display = "none";
            if (postFlatExtra) postFlatExtra.style.display = "none";
        }
    }

    // keep UI in sync (called whenever mode/type/selection changes)
    function syncUI() {
        updateModeUI();
        updateFixedTypeUI();
    }

    // Attach listeners to radios early so UI reacts even before form is shown
    if (modeFixed) modeFixed.addEventListener('change', syncUI);
    if (modeManual) modeManual.addEventListener('change', syncUI);
    if (fixedPerKm) fixedPerKm.addEventListener('change', syncUI);
    if (fixedFlat) fixedFlat.addEventListener('change', syncUI);

    // When vehicle selected -> show form and attach vehicle id
    if (vehicleSelect) {
        vehicleSelect.addEventListener('change', function () {
            const selected = vehicleSelect.options[vehicleSelect.selectedIndex];
            if (!selected || !selected.value) {
                amountForm.style.display = 'none';
                return;
            }

            // set hidden vehicle identifier (you use v.v_number as option value)
            if (vehicleIdInput) vehicleIdInput.value = selected.value;

            // show form
            amountForm.style.display = 'block';

            // sync UI based on current radio selections
            syncUI();

            // optionally pre-focus first visible input
            setTimeout(() => {
                if (modeManual && modeManual.checked) {
                    // nothing to focus for manual
                } else {
                    if (fixedPerKm && fixedPerKm.checked) {
                        // focus min_km first (new requirement), then amount_per_km
                        if (minKmInput) {
                            minKmInput.focus();
                        } else {
                            amountPerKm?.focus();
                        }
                    } else {
                        flatAmount?.focus();
                    }
                }
            }, 50);
        });
    }

    // form validation before submit
    amountForm.addEventListener('submit', function (e) {
        // If manual mode, nothing to validate
        if (modeManual && modeManual.checked) {
            return; // allow submit
        }

        // Fixed mode validations
        if (fixedPerKm && fixedPerKm.checked) {
            // Validate minimum KM (must be integer >= 1)
            const minKmVal = minKmInput ? parseInt(minKmInput.value, 10) : NaN;
            if (isNaN(minKmVal) || minKmVal < 1) {
                e.preventDefault();
                alert('Please enter a valid Minimum KM (integer >= 1).');
                if (minKmInput) minKmInput.focus();
                return;
            }

            // Validate amount per KM
            const rate = parseFloat(amountPerKm.value);
            if (isNaN(rate) || rate < 0) {
                e.preventDefault();
                alert('Please enter a valid Amount per KM (>= 0).');
                amountPerKm.focus();
                return;
            }

        } else if (fixedFlat && fixedFlat.checked) {
            const flat = parseFloat(flatAmount.value);
            const maxKm = parseInt(flatMaxKm.value, 10);

            if (isNaN(flat) || flat < 0) {
                e.preventDefault();
                alert('Please enter a valid Flat amount (>= 0).');
                flatAmount.focus();
                return;
            }
            if (isNaN(maxKm) || maxKm <= 0) {
                e.preventDefault();
                alert('Please enter a valid Max KM for the flat (integer > 0).');
                flatMaxKm.focus();
                return;
            }

            // optional: if extraAfterFlat set verify numeric
            if (extraAfterFlat && extraAfterFlat.value) {
                const extra = parseFloat(extraAfterFlat.value);
                if (isNaN(extra) || extra < 0) {
                    e.preventDefault();
                    alert('Please enter a valid Extra per KM after flat limit (>= 0).');
                    extraAfterFlat.focus();
                    return;
                }
            }
        }

        // success: allow submit
    });

    // Run once on load to ensure initial state matches any pre-checked radios
    syncUI();
});
