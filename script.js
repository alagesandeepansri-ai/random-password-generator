function copyPassword() {
    const password = document.querySelector(".password-box").innerText;

    navigator.clipboard.writeText(password).then(function () {
        alert("Password copied!");
    });
}