document.addEventListener("DOMContentLoaded", function () {
    const vTypeEl = document.getElementById("v_type");
    const seatSelect = document.getElementById("seats");
    const agencySelect = document.getElementById("travellers");
    const modelSelect = document.getElementById("v_model");

    const originalModelOptions = [...modelSelect.querySelectorAll("option")].map(o => o.cloneNode(true));

    function clearModels() {
        modelSelect.innerHTML = '<option value="" disabled selected>— Select Car Model —</option>';
    }

    // Assign seat ranges based on vehicle type
    function loadSeats(vType) {
        seatSelect.innerHTML = '<option value="" disabled selected>— Select Seats —</option>';
        let seats = [];

        if (vType === "car") seats = [4, 5, 7];
        if (vType === "tourist-bus(mini)") seats = [12, 17, 25];
        if (vType === "tourist-bus") seats = [30, 35, 40, 45, 50];
        if (vType === "luxury-bus") seats = [9, 15];

        seats.forEach(s => {
            let opt = document.createElement("option");
            opt.value = s;
            opt.textContent = `${s} Seats`;
            seatSelect.appendChild(opt);
        });
    }

    // Try filtering using data-attributes
    function filterModelsClient(agency, vType, seats) {
        const hasData = originalModelOptions.some(o => o.dataset.agency || o.dataset.vtype || o.dataset.seats);
        if (!hasData) return false;

        clearModels();

        originalModelOptions.forEach(opt => {
            if (!opt.value) return;

            let ok = true;

            if (opt.dataset.agency && opt.dataset.agency !== String(agency)) ok = false;
            if (opt.dataset.vtype && opt.dataset.vtype !== String(vType)) ok = false;

            if (opt.dataset.seats) {
                const list = opt.dataset.seats.split(",").map(x => x.trim());
                if (!list.includes(String(seats))) ok = false;
            }

            if (ok) modelSelect.appendChild(opt.cloneNode(true));
        });

        return true;
    }

    // Server API fallback
    function fetchModelsServer(agency, vType, seats) {
        clearModels();
        modelSelect.innerHTML = '<option selected>Loading...</option>';

        const params = new URLSearchParams({
            agency: agency,
            v_type: vType,
            seats: seats
        });

        fetch(`/api/get-vehicles/?${params.toString()}`, {
            credentials: "same-origin"
        })
            .then(res => res.json())
            .then(data => {
                clearModels();

                const list = data.vehicles || [];

                if (!list.length) {
                    modelSelect.innerHTML = '<option disabled>No models available</option>';
                    return;
                }

                list.forEach(v => {
                    let opt = document.createElement("option");
                    opt.value = v.id;
                    opt.textContent = v.v_model;
                    modelSelect.appendChild(opt);
                });
            })
            .catch(() => {
                clearModels();
                modelSelect.innerHTML = '<option disabled>Error loading models</option>';
            });
    }

    // Master function called after any change
    function loadModels() {
        const agency = agencySelect.value;
        const vType = vTypeEl.value;
        const seats = seatSelect.value;

        const clientOK = filterModelsClient(agency, vType, seats);
        if (!clientOK) fetchModelsServer(agency, vType, seats);
    }

    // Event listeners
    vTypeEl.addEventListener("change", function () {
        loadSeats(this.value);
        clearModels();
    });

    seatSelect.addEventListener("change", loadModels);
    agencySelect.addEventListener("change", loadModels);

    // Auto-load for edit mode
    if (agencySelect.value && vTypeEl.value && seatSelect.value) {
        loadModels();
    }
});

document.addEventListener("DOMContentLoaded", function () {

    /* ---------- VEHICLE FILTER ---------- */
    const travellers = document.getElementById("travellers");
    const seats = document.getElementById("seats");

    if (travellers && seats) {
        travellers.addEventListener("change", loadVehicleModels);
        seats.addEventListener("change", loadVehicleModels);
    }
});

function loadVehicleModels() {
    const v_type = document.getElementById("v_type").value;
    const agency = document.getElementById("travellers").value;
    const seats = document.getElementById("seats").value;

    if (!v_type || !agency || !seats) return;

    fetch(`/api/get-vehicles/?v_type=${v_type}&agency=${agency}&seats=${seats}`)
        .then(res => res.json())
        .then(data => {
            const vModelSelect = document.getElementById("v_model");
            vModelSelect.innerHTML = `<option disabled selected>— Select car model —</option>`;

            data.vehicles.forEach(v => {
                vModelSelect.innerHTML += `<option value="${v.id}">${v.v_model}</option>`;
            });
        });
}

setTimeout(() => {
  document.querySelectorAll('.toast-message').forEach(t => t.remove());
}, 4000);

let map, marker, selectedLatLng = null;
let locationFetched = false;

document.addEventListener("DOMContentLoaded", function () {

    const mapBtn = document.getElementById("getMyLocationBtn");
    const pickupInput = document.getElementById("pickup");

    mapBtn.addEventListener("click", () => {

        // FIRST CLICK → AUTO LOCATION (NO MODAL)
        if (!locationFetched) {
            getAutoLocation();
        } 
        // SECOND CLICK → SHOW MAP MODAL
        else {
            openMapModal();
        }
    });

    function getAutoLocation() {
        if (!navigator.geolocation) {
            alert("Geolocation not supported");
            return;
        }

        navigator.geolocation.getCurrentPosition(
            pos => {
                selectedLatLng = {
                    lat: pos.coords.latitude,
                    lng: pos.coords.longitude
                };

                locationFetched = true;

                // Reverse geocode
                fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${selectedLatLng.lat}&lon=${selectedLatLng.lng}`)
                    .then(res => res.json())
                    .then(data => {
                        pickupInput.value = data.display_name || "Current Location";
                    });
            },
            () => alert("Please allow location permission"),
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    }

    function openMapModal() {
        const modal = new bootstrap.Modal(document.getElementById("mapModal"));
        modal.show();

        setTimeout(() => {
            if (!map) {
                map = L.map("map").setView([selectedLatLng.lat, selectedLatLng.lng], 16);

                L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
                    attribution: "© OpenStreetMap"
                }).addTo(map);
            } else {
                map.setView([selectedLatLng.lat, selectedLatLng.lng], 16);
            }

            if (marker) map.removeLayer(marker);

            marker = L.marker(
                [selectedLatLng.lat, selectedLatLng.lng],
                { draggable: true }
            ).addTo(map);

            marker.on("dragend", () => {
                const pos = marker.getLatLng();
                selectedLatLng = { lat: pos.lat, lng: pos.lng };

                fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${pos.lat}&lon=${pos.lng}`)
                    .then(res => res.json())
                    .then(data => {
                        pickupInput.value = data.display_name || "Selected Location";
                    });
            });

        }, 300);
    }
});
