
document.addEventListener("DOMContentLoaded", function () {
    // 1. Back-to-top button
    const topButton = document.getElementById("back-to-top");
    if (topButton) {
        window.addEventListener("scroll", function () {
            topButton.style.display = window.scrollY > 200 ? "block" : "none";
        });
        topButton.addEventListener("click", function () {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    }

    // 2. Auto-dismiss alerts after 5 seconds
    document.querySelectorAll(".alert").forEach(function (alertBox) {
        setTimeout(function () {
            bootstrap.Alert.getOrCreateInstance(alertBox).close();
        }, 5000);
    });

    // 3. Client-side validation for forms marked with .needs-validation
    document.querySelectorAll(".needs-validation").forEach(function (form) {
        form.addEventListener("submit", function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add("was-validated");
        });
    });
});