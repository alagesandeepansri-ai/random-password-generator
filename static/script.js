function copyPassword() {

    const passwordBox = document.querySelector(".password-box");

    if (!passwordBox) {
        return;
    }

    const password = passwordBox.dataset.password;

    navigator.clipboard.writeText(password)
        .then(function () {
            alert("Password copied!");
        })
        .catch(function () {
            alert("Copy failed!");
        });
}


function togglePassword() {

    const passwordBox = document.querySelector(".password-box");

    if (!passwordBox) {
        return;
    }

    const password = passwordBox.dataset.password;

    if (passwordBox.dataset.hidden === "true") {

        passwordBox.innerText = password;
        passwordBox.dataset.hidden = "false";

    } else {

        passwordBox.innerText = "••••••••••••••";
        passwordBox.dataset.hidden = "true";

    }
}


function setLength(length) {

    const lengthInput = document.getElementById("length");

    if (!lengthInput) {
        return;
    }

    lengthInput.value = length;
}


function toggleMenu() {

    const menu = document.getElementById("menu");

    if (!menu) {
        return;
    }

    menu.classList.toggle("show");
}


document.addEventListener("click", function(event) {

    const menu = document.getElementById("menu");
    const button = document.querySelector(".menu-button");

    if (!menu || !button) {
        return;
    }

    if (
        !menu.contains(event.target) &&
        !button.contains(event.target)
    ) {

        menu.classList.remove("show");

    }

});