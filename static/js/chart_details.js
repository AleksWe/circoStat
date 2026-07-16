function toggleSendButton() {
    const pDivChecked = document.getElementById('P_DIV').checked;
    const nucDiv = document.getElementById('NUC_DIV');

    nucDiv.disabled = !pDivChecked;

    if (nucDiv.disabled) {
        nucDiv.checked = false;
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