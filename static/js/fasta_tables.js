const fileInput = document.getElementById("fileInput");
const fastaTable = document.getElementById("fastaTable");
let storedFiles = [];

document.getElementById("fileInput").addEventListener("change", (event) => {
    const newFiles = Array.from(event.target.files);
    newFiles.forEach(file => {
        if (!storedFiles.some(f => f.name === file.name && f.size === file.size)) {
            storedFiles.push(file);
        }
    });
    renderFileList();
    rebuildFastaTable();
    console.log(storedFiles);
});

function renderFileList() {
    const list = document.getElementById("fileList");
    list.innerHTML = "";

    storedFiles.forEach((file, index) => {
        const li = document.createElement("li");
        li.className = "list-group-item list-group-item-light d-flex justify-content-between align-items-center";
        li.innerHTML = `
            <span>${file.name}</span>
            <button class="btn btn-primary btn-sm" data-index="${index}">
                X
            </button>
        `;
        list.appendChild(li);
    });

    document.querySelectorAll("#fileList button").forEach(btn => {
        btn.addEventListener("click", () => {
            const idx = btn.dataset.index;
            storedFiles.splice(idx, 1);
            renderFileList();
        });
    });
}

function rebuildFastaTable() {
    fastaTable.innerHTML = "";
    let isPremadeTable = 0;

    for (const file of storedFiles) {
        if (file.name.includes('.csv')) {
            isPremadeTable++;
            file.text().then(text => {
                const rows = text.split(/\r?\n/);

                rows.forEach(line => {
                    if (!line.trim()) return;

                    const {left, right} = splitLine(line);
                    const row = document.createElement("tr");
                    row.innerHTML = `
                    <td>${left}</td>
                    <td><input class="form-control form-control-sm" value="${right}"></td>
                  `;

                    fastaTable.appendChild(row);
                });
            });
        }
    }
    if (!isPremadeTable) {
        console.log("No .csv file detected.")
    }
}

function splitLine(line) {
    const match = line.match(/[,;]/); // finds first , or ;

    if (!match) {
        return {left: line.trim(), right: ""};
    }

    const sepIndex = match.index;

    return {
        left: line.slice(0, sepIndex).trim(),
        right: line.slice(sepIndex + 1).trimStart()
    };
}

document.getElementById("form2").addEventListener("submit", (e) => {
    e.preventDefault();

    const formData = new FormData();

    // extracting options from index.html
    document.querySelectorAll('input[name="options"]:checked')
        .forEach(cb => formData.append("options", cb.value));

    // extracting table_data
    const tableData = getTableData();
    formData.append("table_data", JSON.stringify(tableData));

    // extracting all files
    storedFiles.forEach(file => {
        formData.append("files", file);
    });

    fetch("/upload", {
        method: "POST",
        body: formData
    })
        .then(r => r.json())
        .then(data => console.log("FastAPI response:", data));
});
