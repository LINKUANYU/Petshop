// common.js
import { fetch_data } from "./common.js";
import { handle_api_error } from "./common.js";
import { update_header } from "./common.js";

update_header();

const main = document.querySelector('#product-list');

(async function(){
    try{
        const res = await fetch_data("/api/home/product");
        res.data.forEach((d) => {
            const a_box = document.createElement('a');
            a_box.className = "card";
            a_box.href = `/product/${d.id}`;
            const box_1 = document.createElement('div');
            box_1.className = "thumb-wrapper";
            const img = document.createElement('img');
            img.className = "thumb";
            img.src = `/static/${d.main_image}`;
            img.alt = `${d.name}`
            const p = document.createElement('p');
            p.className = "name";
            p.textContent = `${d.name}`;
            const box_2 = document.createElement('div');
            box_2.className = "flex";
            const price = document.createElement('div');
            price.className = "price";
            price.textContent = `NT$${d.price / 100}`;
            
            box_1.appendChild(img);
            box_2.appendChild(price);
            a_box.append(box_1, p, box_2);
            main.appendChild(a_box);
        });
    } catch (e){
        console.log(e);
    }
})();