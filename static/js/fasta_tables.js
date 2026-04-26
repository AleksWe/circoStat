const fileInput = document.getElementById("fileInput");
const fastaTable = document.getElementById("fastaTable");

fileInput.addEventListener("change", (e) => {
  console.log("Fasta files loaded. Saving info to form table...");

  console.log("files:", fileInput.files);

  fastaTable.innerHTML = "";

  for (const file of fileInput.files) {
    const row = document.createElement("tr");

    row.innerHTML = `
      <td>${file.name}</td>
      <td><input></td>
    `;

    fastaTable.appendChild(row);
  }
});