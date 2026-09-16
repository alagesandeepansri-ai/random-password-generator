function copyPassword() {

    const passwordBox =
        document.querySelector(".password-box");

    if (!passwordBox) {
        return;
    }

    const password =
        passwordBox.dataset.password;

    navigator.clipboard.writeText(password)
        .then(function () {

            alert("Password copied!");

        })
        .catch(function () {

            alert("Copy failed. Please try again.");

        });
}


function togglePassword() {

    const passwordBox =
        document.querySelector(".password-box");

    if (!passwordBox) {
        return;
    }

    const password =
        passwordBox.dataset.password;


    if (passwordBox.dataset.hidden === "true") {

        passwordBox.innerText = password;

        passwordBox.dataset.hidden = "false";

    }

    else {

        passwordBox.innerText =
            "••••••••••••";

        passwordBox.dataset.hidden = "true";

    }
}


function setLength(length) {

    document.getElementById("length").value =
        length;

}