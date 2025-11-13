(function (){
    
    // get element from URL ex:page_number
    const params = new URLSearchParams(location.search);
    // if URL has page_number get the value, else "1"
    const pageParam = params.get("page_number") || "1";
    // turn string into number and decimal
    const parsed = Number.parseInt(pageParam, 10);
    // Number at least would be 1, *parsed could be NaN
    const page_number = Math.max(1,parsed);
    const showPage = document.querySelector('#showPage');
    showPage.textContent = page_number;

    const list = document.querySelector('#product-list');
    const nextLink = document.querySelector('#nextLink');
    const previousLink = document.querySelector('#previousLink');
    
    fetch(`/api/daily-discover?page_number=${page_number}`)
        .then(res => {
            if (!res.ok) throw new Error (`HTTP ${res.status}`);
            return res.json();
        }).then(json => {
            list.innerHTML = json.data.map(renderCard).join("");
            
            // build previous page
            if (json.page_number === 1){
                previousLink.style.display = "none";
            }else{
                previousLink.href = `/daily_discover?page_number=${json.page_number - 1}`;
            }

            // bulid nextpage link if it's exsist
            if (json.has_next && json.next_page_number){
                nextLink.href = `/daily_discover?page_number=${json.next_page_number}`;
            } else {
                nextLink.style.display = "none";
            }
        }).catch(() => {
            list.textContent = "載入失敗";
            nextLink.style.display = "none";
        });
    
    function renderCard(p){
        const imgkey = p.img;
        const imgsrc = imgkey ? `/static/${imgkey}`: `/static/search.png`;
        return `
            <article class="card">
                <div class="thumb-wrapper">
                    <img class="thumb" src="${imgsrc}" alt="${escapeHtml(p.name)}">
                </div>
                <p class="name">${escapeHtml(p.name)}</p>
                <div class="flex">
                    <div class="price">NT$${p.price}</div>
                    <button class="btn-add">add to cart</button>
                </div>
            </article>
        `;
    }
    const HTML_ENT = Object.freeze({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    });

    function escapeHtml(input){
        const s = input == null ? "" : String(input);
        return s.replace(/[&<>"']/g, ch => HTML_ENT[ch])
    }

})();