
let selectedFiles = [];
let isSelectMode = false;

// Toggle seleksi file
function toggleSelectFile(path, isSelected, event) {
    event.stopPropagation();

    if (isSelected) {
        if (!selectedFiles.includes(path)) selectedFiles.push(path);
    } else {
        selectedFiles = selectedFiles.filter(file => file !== path);
    }

    updateToolbarState();
}

// Toggle mode Select/Unselect
function toggleSelectMode() {
    isSelectMode = !isSelectMode;

    const checkboxes = document.querySelectorAll('.file-checkbox');
    const containers = document.querySelectorAll('.select-checkbox-container');

    containers.forEach(container => container.style.display = isSelectMode ? 'block' : 'none');
    if (!isSelectMode) {
        checkboxes.forEach(checkbox => checkbox.checked = false);
        selectedFiles = [];
    }

    // Tampilkan/sembunyikan tombol toolbar
    document.querySelectorAll('.toolbar-default').forEach(btn => {
        btn.classList.toggle('d-none', isSelectMode);
    });
    document.querySelectorAll('.toolbar-select').forEach(btn => {
        btn.classList.toggle('d-none', !isSelectMode);
    });

    updateToolbarState();
}

// Navigasi folder/file
function openItem(path, isDir, event) {
    if (isSelectMode) {
        event.stopPropagation();
        return;
    }

    window.location.href = isDir
        ? `/?path=${encodeURIComponent(path)}`
        : `/open?path=${encodeURIComponent(path)}`;
}

// Perbarui status tombol toolbar
function updateToolbarState() {
    const count = selectedFiles.length;

    // Tombol Rename hanya aktif saat 1 file dipilih
    const renameBtn = document.getElementById("renameBtn");
    if (renameBtn) {
        renameBtn.classList.toggle("disabled", count !== 1);
        renameBtn.disabled = (count !== 1);
    }

// Tombol select mode lainnya aktif jika minimal 1 file dipilih
document.querySelectorAll('.toolbar-select').forEach(btn => {
    if (btn.id !== "renameBtn" && btn.id !== "unselectBtn") {
        btn.classList.toggle("disabled", count === 0);
        btn.disabled = (count === 0);
    }
});
}

// Tombol Rename → buka modal
document.getElementById("renameBtn").addEventListener("click", function () {
    if (selectedFiles.length === 1 && !this.classList.contains("disabled")) {
        const currentName = selectedFiles[0].split("/").pop();
        document.getElementById("newNameInput").value = currentName;
        const modal = new bootstrap.Modal(document.getElementById('renameModal'));
        modal.show();
    }
});

// Kirim request rename
function confirmRename() {
    const newName = document.getElementById("newNameInput").value.trim();
    if (!newName) return alert("Nama tidak boleh kosong.");

    const file = selectedFiles[0];
    fetch('/rename', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `path=${encodeURIComponent(file)}&new_name=${encodeURIComponent(newName)}`
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert(data.error || "Terjadi kesalahan saat mengubah nama.");
        }
    });
}

// Tombol Folder Baru → buka modal
document.getElementById("newFolderBtn").addEventListener("click", function () {
    document.getElementById("newFolderName").value = "";
    const modal = new bootstrap.Modal(document.getElementById('newFolderModal'));
    modal.show();
});

// Kirim request buat folder baru
function createNewFolder() {
    const folderName = document.getElementById("newFolderName").value.trim();
    if (!folderName) {
        alert("Nama folder tidak boleh kosong.");
        return;
    }

    fetch('/create-folder', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `name=${encodeURIComponent(folderName)}&path=${encodeURIComponent(currentPath)}`
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert(data.error || "Gagal membuat folder.");
        }
    });
}

// Konfirmasi dan hapus file/folder
function deleteSelectedFiles() {
    if (selectedFiles.length === 0) return;

    Swal.fire({
        title: 'Yakin ingin menghapus?',
        text: `Aksi ini akan menghapus ${selectedFiles.length} item.`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Ya, hapus',
        cancelButtonText: 'Batal'
    }).then(result => {
        if (result.isConfirmed) {
            fetch('/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ paths: selectedFiles })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    Swal.fire('Gagal', data.error || 'Gagal menghapus item.', 'error');
                }
            });
        }
    });
}

function changeRoot(selectElement) {
    const path = selectElement.value;
    fetch('/set-root', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `root_path=${encodeURIComponent(path)}`
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/';
        } else {
            alert(data.error || "Gagal mengubah folder root.");
        }
    });
}



// Event listener tombol hapus
document.getElementById("deleteBtn").addEventListener("click", deleteSelectedFiles);