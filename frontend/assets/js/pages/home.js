(async function () {
    try{
        const response = await fetch("/api/daily-discover/highlights?limit=5");
        if (!response.ok) throw new Error (`HTTP ${response.status}`);
        const json = await response.json();
        const list = document.querySelector("#product-list");

        if (!json.data || json.data.length === 0){
            list.innerHTML = "<p>Can't find any product</p>";
            return;
        }
        list.innerHTML = json.data.map(renderCard).join("");
    }catch (err){
        console.error(err);
        const list = document.querySelector("#product-list");
        list.innerHTML = "<p>Fail to load in products</p>"
    }
})();

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
                <div class="price">${p.price}</div>
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