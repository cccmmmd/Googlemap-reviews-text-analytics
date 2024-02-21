let inputElem = document.querySelector('input');
let submitButton = document.querySelector('#submitButton');
submitButton
inputElem.addEventListener('input', () => {
    if(inputElem.value!=''){
        submitButton.classList.remove("disabled");
    }else{
        submitButton.classList.add("disabled");
    }
});
function searchFun(){
    if (inputElem.validity.valid) {
        let mask = document.querySelector('.mask');
        let div1 = document.querySelector('.show1');
        let div2 = document.querySelector('.show2');
        
        let isDiv1Visible = true;

        mask.style.display = 'flex'
        setInterval(() => {
            if (isDiv1Visible) {
                div1.style.display = 'none';
                div2.style.display = 'block';
            } else {
                div1.style.display = 'block';
                div2.style.display = 'none';
            }
            isDiv1Visible = !isDiv1Visible;
        }, 1400);
    }    
}
