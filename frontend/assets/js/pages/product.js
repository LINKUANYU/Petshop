// common.js
import { fetch_data, handle_api_error, update_header} from "./common.js";

update_header();

const price = document.querySelector("#price");
const stock = document.querySelector("#stock");
const var_btn = document.querySelectorAll(".var-btn");

function set_active(btn){
    var_btn.forEach(b => {
        b.classList.remove("is-active")
    });

    btn.classList.add("is-active");
    const data_price = Number(btn.dataset.price);
    const data_stock = Number(btn.dataset.stock);

    price.textContent = `NT$${data_price / 100}`;
    stock.textContent = data_stock;
};

var_btn.forEach(b => {
    b.addEventListener('click', function(){
        set_active(b)
    });
});