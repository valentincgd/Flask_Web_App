inputEmail = document.getElementById('email-txt');
labelEmail = document.getElementById('email-label');

inputPass = document.getElementById('password-txt');
labelPass = document.getElementById('password-label');

viewPass = document.getElementById('viewPass');

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

viewPass.addEventListener('click', (event) =>{
    if(inputPass.type == 'password'){
        inputPass.type = "text";
        viewPass.innerHTML = '<ion-icon name="eye-outline"></ion-icon>';
    }else{
        inputPass.type = "password";
        viewPass.innerHTML = '<ion-icon name="eye-off-outline"></ion-icon>';
    }
});

if(document.getElementById('username-txt')){

    inputUser = document.getElementById('username-txt');
    labelUser = document.getElementById('username-label');

    inputUser.addEventListener("keyup", (event) => {
        labelUser.setAttribute('class', '');
        if(inputUser.value != ""){
            labelUser.setAttribute('class', 'focus');
        }
    });

}
