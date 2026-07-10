function toggleSendButton() {
    const checkbox1 = document.getElementById('SNP').checked;
    const checkbox2 = document.getElementById('NUC_DIV').checked;

    document.getElementById('P_DIV').disabled = !(checkbox1 || checkbox2);
    if (document.getElementById('P_DIV').disabled){
        document.getElementById("P_DIV").checked = false;
    }
}
document.getElementById('form2').addEventListener('submit', function(event) {
    var checkboxes = this.querySelectorAll('input[type="checkbox"]');
    var allUnchecked = Array.from(checkboxes).every(checkbox => !checkbox.checked);

    if (allUnchecked) {
        alert('Please check any of the boxes before submitting.');
        event.preventDefault(); // Prevent form submission
    }
});