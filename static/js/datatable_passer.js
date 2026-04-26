function getTableData() {
    const table = document.getElementById("fastaTable");
    const data = [];
    for (let row of table.rows) {
        const rowData = [];

        for (let cell of row.cells) {
            const input = cell.querySelector("input");

            if (input) {
                rowData.push(input.value);
            } else {
                rowData.push(cell.innerText);
            }
        }

        data.push(rowData);
    }
    return data;
}

document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("#form2");

    form.addEventListener("submit", function () {
        const tableData = getTableData();

        console.log(getTableData());

        const input = document.createElement("input");
        input.type = "hidden";
        input.name = "table_data";
        input.value = JSON.stringify(tableData);

        form.appendChild(input);
    });
});