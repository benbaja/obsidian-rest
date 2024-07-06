const showHideAPI = document.getElementById("show_hide_api");
const showHideSwiftInk = document.getElementById("show_hide_swiftink");
const copyBtn = document.getElementById("api_key_copy");

const toggleEye = (source) => {
    if (document.getElementById(source + "_input").getAttribute("type") == "password") {
        document.getElementById(source + "_input").setAttribute("type", "text");
        document.getElementById(source + "_eyei").classList.add("bi-eye");
        document.getElementById(source + "_eyei").classList.remove("bi-eye-slash");
    } else if (document.getElementById(source + "_input").getAttribute("type") == "text") {
        document.getElementById(source + "_input").setAttribute("type", "password");
        document.getElementById(source + "_eyei").classList.add("bi-eye-slash");
        document.getElementById(source + "_eyei").classList.remove("bi-eye");
    }
};

showHideAPI.addEventListener('click', (event) => {
    toggleEye("api")
});
showHideSwiftInk.addEventListener('click', (event) => {
    toggleEye("swiftink")
});
copyBtn.addEventListener('click', (event) => {
    const apiKeyValue = document.getElementById("api_input").value
    navigator.clipboard.writeText(apiKeyValue);
    copyBtn.innerText = "Copied !"
})