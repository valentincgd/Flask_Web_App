inputEmail = document.getElementById('email-txt');
labelEmail = document.getElementById('email-label');

inputPass = document.getElementById('password-txt');
labelPass = document.getElementById('password-label');

inputEmail.addEventListener("keyup", (event) => {
    labelEmail.setAttribute('class', '');
    if(inputEmail.value != ""){
        labelEmail.setAttribute('class', 'focus');
    }
});

inputPass.addEventListener("keyup", (event) => {
    labelPass.setAttribute('class', '');
    if(inputPass.value != ""){
        labelPass.setAttribute('class', 'focus');
    }
});