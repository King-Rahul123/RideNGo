document.getElementById("v_type").addEventListener("change", function () {
    const vType = this.value;
    const seatSelect = document.getElementById("seats");

    // CLEAR previous options
    seatSelect.innerHTML = '<option value="" disabled selected>--- Select Seat ---</option>';

    let seats = [];

    // Define seat options per vehicle type
    if (vType === "car") {
        seats = [4, 5, 7];
    } 
    else if (vType === "tourist-bus(mini)") {
        seats = [12, 17, 25];
    } 
    else if (vType === "tourist-bus") {
        seats = [30, 35, 40, 45, "50+"];
    } 
    else if (vType === "luxury-bus") {
        seats = [9, 15];
    }

    // Push seat values to dropdown
    seats.forEach(seat => {
        const option = document.createElement("option");
        option.value = seat;
        option.textContent = seat + " Seats";
        seatSelect.appendChild(option);
    });
});

document.querySelectorAll(".viewBtn").forEach(btn => {
    btn.addEventListener("click", function () {

        document.getElementById("detailImg").src = this.dataset.img;
        document.getElementById("detailModel").innerText = this.dataset.model;
        document.getElementById("detailPlate").innerText = this.dataset.plate;
        document.getElementById("detailType").innerText = this.dataset.type;
        document.getElementById("detailSeats").innerText = this.dataset.seats;
        document.getElementById("detailPollution").innerText = this.dataset.pollution;
        document.getElementById("detailInsurance").innerText = this.dataset.insurance;
        document.getElementById("detailFitness").innerText = this.dataset.fitness;
        document.getElementById("detailPermit").innerText = this.dataset.permit;
        document.getElementById("detailAuthorize").innerText = this.dataset.authorize;

        document.getElementById("detailDriver").innerText = this.dataset.driver || "Not Assigned";
        document.getElementById("detailLicence").innerText = this.dataset.licence || "-";
        document.getElementById("detailPhone").innerText = this.dataset.phone || "-";

        // Driver Image
        const driverImg = document.getElementById("detailDriverImg");
        if (this.dataset.driverimg) {
            driverImg.src = this.dataset.driverimg;
            driverImg.style.display = "block";
        } else {
            driverImg.src = "";
            driverImg.style.display = "none";
        }
        
        // Scroll to bottom details
        document.getElementById("vehicleDetails").scrollIntoView({ behavior: "smooth" });
    });
});

function openUpdateVehicleModal(vehicleId) {
    const form = document.getElementById("updateVehicleForm");

    // ✅ set correct update URL with pk
    form.action = `/agency/vehicles/${vehicleId}/update/`;

    // optional hidden field (not required, but ok)
    document.getElementById("update_vehicle_id").value = vehicleId;
}

function openUpdateVehicleModal(vehicleId, vehicleName, agencyName) {
    const form = document.getElementById("updateVehicleForm");

    // ✅ correct update URL
    form.action = `/agency/vehicles/${vehicleId}/update/`;

    // optional hidden field
    document.getElementById("update_vehicle_id").value = vehicleId;

    // ✅ show correct names
    document.getElementById("updateAgencyName").innerText = agencyName;
    document.getElementById("updateVehicleName").innerText = "Vehicle: " + vehicleName;
}
