const fileInput = document.getElementById("fileInput");
const fastaTable = document.getElementById("fastaTable");

fileInput.addEventListener("change", (e) => {

  console.log("files:", fileInput.files);

  fastaTable.innerHTML = "";

  let isPremadeTable = 0;

  for (const file of fileInput.files) {

    console.log(file.name)

    if (file.name.includes('.csv')){
      isPremadeTable++;

      file.text().then(text => {
        const rows = text.split(/\r?\n/);
        console.log(rows);

        rows.forEach(line => {
          if (!line.trim()) return;

          const { left, right } = splitLine(line);

          const row = document.createElement("tr");
          row.innerHTML = `
                    <td>${left}</td>
                    <td><input class="form-control form-control-sm" value="${right}"></td>
                  `;

          fastaTable.appendChild(row);
        });
      });
    }

    else if (file.name.includes('.fasta') || file.name.includes('.fa')){
        const row = document.createElement("tr");

        row.innerHTML = `
          <td>${file.name}</td>
          <td><input></td>
        `;

        fastaTable.appendChild(row);
    }

    else {
      console.log("Provided file is neither a .fasta or .csv file.")
    }
  }

  if (!isPremadeTable){
    console.log("No .csv file detected.")
  }
});

function splitLine(line) {
  const match = line.match(/[,;]/); // finds first , or ;

  if (!match) {
    return { left: line.trim(), right: "" };
  }

  const sepIndex = match.index;

  return {
    left: line.slice(0, sepIndex).trim(),
    right: line.slice(sepIndex + 1).trimStart()
  };
}