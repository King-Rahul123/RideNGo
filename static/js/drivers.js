(function(){
    const rows = document.querySelectorAll('#driversTable tr[data-driver-id]');
    function showPreview(data){ document.getElementById('noSelection').style.display='none'; document.getElementById('driverPreview').style.display='block';
        document.getElementById('previewName').textContent = data.driver_name;
        document.getElementById('previewPhone').textContent = data.phone || '';
        document.getElementById('previewLicence').textContent = data.licence_number || '-';
        document.getElementById('previewVehicle').textContent = data.vehicle || 'Unassigned';
        document.getElementById('previewStatus').textContent = data.is_active? 'Active' : 'Inactive';
    }

    rows.forEach(r=> r.addEventListener('click', ()=>{
        const id = r.getAttribute('data-driver-id');
        // find driver data from a JSON blob rendered server-side or fetch via AJAX
        const dataset = window.DRIVERS_DATA && window.DRIVERS_DATA[id];
        if(dataset) showPreview(dataset);
    }));

    // Search
    const search = document.getElementById('searchDriver');
    if (search) {
        search.addEventListener('input', () => {
            const q = search.value.toLowerCase();
            rows.forEach(r => {
                const text = r.textContent.toLowerCase();
                r.style.display = text.includes(q) ? '' : 'none';
            });
        });
    }

    // Prepare edit modal
    const editModal = document.getElementById('editDriverModal');
    editModal.addEventListener('show.bs.modal', function(event){
        const button = event.relatedTarget;
        const id = button.getAttribute('data-driver-id');
        if(!id) return;
        const d = window.DRIVERS_DATA && window.DRIVERS_DATA[id];
        if(!d) return;
        document.getElementById('editDriverId').value = d.id;
        document.getElementById('editName').value = d.driver_name || '';
        document.getElementById('editPhone').value = d.phone || '';
        document.getElementById('editLicence').value = d.licence_number || '';
        document.getElementById('editNotes').value = d.notes || '';
        // set action url if needed
        const form = document.getElementById('editDriverForm');
        form.action = form.action.replace(/\d+$/, d.id);
    });

    // View modal
    const viewModal = document.getElementById('viewDriverModal');
    viewModal.addEventListener('show.bs.modal', function(event){
        const button = event.relatedTarget;
        const id = button.getAttribute('data-driver-id');
        const body = document.getElementById('viewDriverBody');
        body.innerHTML = '<div class="text-center p-4">Loading...</div>';
        const d = window.DRIVERS_DATA && window.DRIVERS_DATA[id];
        if(d){
        body.innerHTML = `
            <div class="row">
            <div class="col-md-4 text-center">
                <div class="avatar rounded-circle bg-secondary text-white d-inline-flex justify-content-center align-items-center" style="width:100px;height:100px;font-size:40px;">${d.first_name?d.first_name.charAt(0).toUpperCase():''}</div>
                <h5 class="mt-2">${d.driver_name || ''}</h5>
                <p class="text-muted small">${d.phone || ''}</p>
            </div>
            <div class="col-md-8">
                <p><strong>Licence:</strong> ${d.licence_number || '-'}</p>
                <p><strong>Vehicle:</strong> ${d.vehicle || 'Unassigned'}</p>
                <p><strong>Status:</strong> ${d.is_active? 'Active':'Inactive'}</p>
                <p><strong>Notes:</strong><br>${d.notes || '-'}</p>
                <hr>
                <p class="small text-muted">Uploaded documents</p>
                ${d.licence_file?`<a href='${d.licence_file}' target='_blank' class='btn btn-sm btn-outline-secondary'>View Licence</a>`:''}
            </div>
            </div>
        `;
        document.getElementById('viewEditBtn').href = `{{ request.path }}#`;
        }
    });
})();

function showDriverPreview(btn) {

    // Show preview card
    document.getElementById("noSelection").style.display = "none";
    document.getElementById("driverPreview").style.display = "block";

    // Read dataset
    const name = btn.dataset.name || '-';
    const phone = btn.dataset.phone || '-';

    const age = btn.dataset.age || '';
    const dob = btn.dataset.dob || '';

    const licenceNo = btn.dataset.licenceno || '-';
    const licenceType = btn.dataset.licencetype || '-';
    const validity = btn.dataset.validity || '-';

    const salary = btn.dataset.salary || 'Not Set';
    const status = btn.dataset.status || '-';

    const img = btn.dataset.img || '';
    const licenceFile = btn.dataset.licencefile || '';

    // Fill text fields
    document.getElementById("previewName").innerText = name;
    document.getElementById("previewPhone").innerText = phone;
    document.getElementById("previewLicenceNo").innerText = licenceNo;
    document.getElementById("previewLicenceType").innerText = licenceType;
    document.getElementById("previewLicenceValidity").innerText = validity;
    document.getElementById("previewSalary").innerText = salary;
    document.getElementById("previewStatus").innerText = status;

    // Age / DOB logic
    const ageDobEl = document.getElementById("previewAgeDob");
    if (dob) {
        ageDobEl.innerText = dob;
    } else if (age) {
        ageDobEl.innerText = age + " years";
    } else {
        ageDobEl.innerText = "-";
    }

    // Driver avatar
    const avatar = document.getElementById("previewAvatar");
    avatar.innerHTML = "";
    if (img) {
        avatar.innerHTML = `<img src="${img}" style="width:56px;height:56px;border-radius:50%;object-fit:cover;">`;
    } else {
        avatar.innerHTML = `<i class="fas fa-user" style="font-size:22px;"></i>`;
    }

    // Licence file preview / link
    const licencePreview = document.getElementById("previewLicenceImage");
    if (licenceFile) {
        licencePreview.innerHTML = `
            <a href="${licenceFile}" target="_blank" class="btn btn-sm btn-outline-info mt-1">
                <i class="fas fa-id-card"></i> View Licence
            </a>
        `;
    } else {
        licencePreview.innerHTML = `
            <span class="text-danger medium">Licence file not uploaded!</span>
        `;
    }
}
