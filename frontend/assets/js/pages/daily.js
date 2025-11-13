(function (){
    // findout which page_number currently at 
    // get element from URL ex:page_number
    const params = new URLSearchParams(location.search);
    // if URL has page_number get the value, else "1"
    const pageParam = params.get("page_number") || "1";
    // turn string into number and decimal
    const parsed = Number.parseInt(pageParam, 10);
    // Choose the big number between page and 1, *parsed could be NaN
    const page_number = Math.max(1,parsed);

    const show_page = document.querySelector('#show_page');
    // show_page.textContent = page_number;

    const list = document.querySelector('#product-list');
    const next_link = document.querySelector('#next_link');
    const previous_link = document.querySelector('#previous_link');
    
    fetch(`/api/daily-discover?page_number=${page_number}`)
        .then(res => {
            if (!res.ok) throw new Error (`HTTP ${res.status}`);
            return res.json();
        }).then(json => {
            // Render card for current page
            list.innerHTML = json.data.map(renderCard).join("");
            
            // bulid previous/next page
            // calculate total pages and show below the card
            const total_pages = Math.max(1, (Math.ceil((json.total || 0) / (json.page_size || 5))));
            show_page.textContent = `${json.page_number} / ${total_pages}`;

            // previous page
            if (json.page_number <= 1){
                previous_link.setAttribute("aria-disabled", "true");
                previous_link.removeAttribute("href");
                previous_link.removeAttribute("rel");
            }else{
                previous_link.removeAttribute("aria-disabled");
                previous_link.href = `/daily_discover?page_number=${json.page_number - 1}`;
                previous_link.setAttribute("rel", "prev");
            }

            // next page
            if (json.has_next && json.next_page_number){
                next_link.removeAttribute("aria-disabled");
                next_link.href = `/daily_discover?page_number=${json.next_page_number}`;
                next_link.setAttribute("rel", "next");
            }else{
                next_link.setAttribute("aria-disabled", "true");
                next_link.removeAttribute("href");
                next_link.removeAttribute("rel");
            }

        }).catch(() => {
            list.textContent = "載入失敗";
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