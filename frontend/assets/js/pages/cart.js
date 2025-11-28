//

(function(w){
    const KEY = 'cart.v1';

    function load(){
        try{
            const raw = localStorage.getItem(KEY);
            const parsed = raw ? JSON.parse(raw) : null;
            if (parsed && Array.isArray(parsed.items)){
                return parsed
            } else {
                return { items: [] };
            }
        } catch (e){
            return { item: [] };
        } 
    }

    function count_items(state){
        state = state || load();
        return (state || []).reduce((s, it) => s + (parseInt(it.qty, 10) || 0)  ,0)
    }

    function save(state){
        // 把現況的購物車內容存到localstorage
        localStorage.setItem(KEY, JSON.stringify(state));
        const count = count_items();
        // 通知全站有人變動購物車，變動訊息為count用來更新購物車縮圖數量
        w.dispathEvent(new CustomEvent('cart:changed', {detail: {count}}));
    }

    function add_or_merge(item){
        // item: { variant_id, product_id, name, label, price, qty, image, stock? } 還要找是從哪邊來的
        const state = load();
        const id = Number(item.variant_id);
    }



})();