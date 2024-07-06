const swiftinkToken = document.currentScript.getAttribute("swiftink-token");

const captureInput = document.getElementById("captureInput");
const todoCheck = document.getElementById("todoCheck");
const audioInput = document.getElementById("formFile");
const submitButton = document.getElementById("submitButton");

const displayToast = (failType, isAudio) => {
    const uploadType = isAudio ? "audio" : "note";
    let toast = document.getElementById(uploadType + "-result-toast");
    const toastBootstrap = bootstrap.Toast.getOrCreateInstance(toast);
    let toastBody = document.getElementById(uploadType + "-result-toast-body");
    if (failType) {
        toastBody.innerText = uploadType + " " + failType + " failed." ;
        if (toast.classList.contains("text-bg-primary")) {
            toast.classList.add("text-bg-danger");
            toast.classList.remove("text-bg-primary");
        }
    } else {
        toastBody.innerText = uploadType + " uploaded successfully.";
        if (toast.classList.contains("text-bg-danger")) {
            toast.classList.add("text-bg-primary");
            toast.classList.remove("text-bg-danger");
        }
    }
    toastBootstrap.show()
    
}

const submitButtonToggle = () => {
    if (submitButton.disabled) {
        submitButton.disabled = false;
        submitButton.innerHTML = "Submit";
    } else {
        submitButton.disabled = true;
        submitButton.innerHTML = `<span class="spinner-border spinner-border-sm" aria-hidden="true"></span>
        <span role="status"> Submitting...</span>`
    }
}

submitButton.addEventListener('click', (event) => {
    event.preventDefault();
    if (audioInput.files.length) {
        submitButtonToggle();

        let reader = new FileReader();
        reader.readAsDataURL(audioInput.files[0]);
        reader.onload = () => {
            fetch("/capture/create", {
                method: "POST",
                body: JSON.stringify({
                    capture_type : 'audio',
                    data: {
                        audio: reader.result,
                        file_name: audioInput.files[0].name
                    },
                }),
                headers: { 
                    "Content-type": "application/json; charset=UTF-8",
                    "Authorization": swiftinkToken
                }
            }).then((data) => {
                submitButtonToggle();
                if (data.ok) {
                    displayToast(failType=null, isAudio=true)
                } else {
                    displayToast(failType="transcription", isAudio=true)
                }
            }).catch((error) => {
                submitButtonToggle();
                displayToast(failType="upload", isAudio=true)
            });
        }
    };

    if (captureInput.value) {
        fetch("/capture/create", {
            method: "POST",
            body: JSON.stringify({
                capture_type : 'note',
                data: {
                    text: captureInput.value
                },
                todo: todoCheck.checked
            }),
            headers: { 
                "Content-type": "application/json; charset=UTF-8",
                "Authorization": swiftinkToken
            }
        }).then((data) => {
            if (data.ok){
                displayToast(failType=null, isAudio=false)
                captureInput.value = "";
            } else {
                displayToast(failType="upload", isAudio=false)
            }
        }).catch((error) => {
            displayToast(failType="upload", isAudio=false)
        });
    };
});