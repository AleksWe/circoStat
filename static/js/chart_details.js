function toggleSendButton() {
    const pDivChecked = document.getElementById('P_DIV').checked;
    const nucDiv = document.getElementById('NUC_DIV');

    nucDiv.disabled = !pDivChecked;

    if (nucDiv.disabled) {
        nucDiv.checked = false;
    }
}

document.getElementById('form2').addEventListener('submit', function (event) {
    var checkboxes = this.querySelectorAll('input[type="checkbox"]');
    var allUnchecked = Array.from(checkboxes).every(checkbox => !checkbox.checked);
    var anyRadioSelected = this.querySelector('input[type="radio"]:checked') !== null;

    window.allUnchecked = allUnchecked;
    window.anyRadioSelected = anyRadioSelected;

    if (window.allUnchecked || !window.anyRadioSelected) {
        event.preventDefault();
        alert('Please check any of the boxes before submitting.');
        return;
    }

    const submitBtn = document.getElementById("submitBtn");
    const loading = document.getElementById("loading");

    submitBtn.disabled = true;
    loading.classList.remove("d-none");

});