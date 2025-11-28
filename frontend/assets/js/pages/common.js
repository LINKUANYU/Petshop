// 送出API
async function fetch_data(url, opts) {
    const res = await fetch(url, opts); // 等待 fetch 完成，拿到 Response 物件（不等於成功，只是請求回來了）
    const ct = res.headers.get('content-type') || ''; // 讀回應標頭的 Content-Type，沒有就用空字串避免 null
    const body = ct.includes('application/json') ? await res.json() : await res.text(); // 判斷是哪一種形式
    
    if (!res.ok){ // 非 2xx（例如 400/401/500）都到這裡
        const err = new Error (`HTTP ${res.status}`); // 建一個 Error，訊息先放狀態碼
        err.status = res.status; // 把 HTTP 狀態碼掛在 Error 物件上，方便上層判斷
        err.payload = body; // 把伺服器的錯誤內容（JSON 或文字）也掛上去，別把細節丟掉
        throw err; // 丟給呼叫端的 try/catch 統一處理
    }
    return body  // 2xx 成功：直接回傳剛剛解析好的 body（通常是物件）
}
// 最後依照自己想表達的方式處理

// 處理錯誤function
function handle_api_error(e, options){
    options = options || {};

    let redirect_on_401;
    if (typeof options.redirect_on_401 === 'boolean'){
        redirect_on_401 = options.redirect_on_401;
    } else {
        redirect_on_401 = true;
    }
    
    if (e.status === 400){
        const err_msg = e?.payload?.detail || "已存在email";
        return err_msg;
    }
    if (e.status === 401){
        // 需轉跳首頁
        if (redirect_on_401){
            const err_msg = e?.payload?.detail || "請先登入";
            window.location.href = "/?msg=" + encodeURIComponent(err_msg);
            return;
        // 不需轉跳首頁(在首頁登入時發生錯誤)
        } else {
            const err_msg = e?.payload?.detail || "帳號或密碼輸入錯誤";
            return err_msg;
        }
    }

    if (e.status === 500){
        const err_msg = e?.payload?.detail || "資料庫錯誤，請稍後再試";
        return err_msg;
    }
    const err_msg = 
    e?.payload?.detail ||
    (typeof e?.payload === 'string' ? e.payload : "") ||
    e?.message || "發生錯誤，稍後再試";
    return err_msg;
}

window.fetch_data = fetch_data;
window.handle_api_error = handle_api_error;

// 這裡的 ?. 是 Optional Chaining（選擇性鏈結） 操作符。功用是：
// e?.payload?.detail 會安全地取值：
// 若 e 是 null 或 undefined ⇒ 整個表達式直接回 undefined（不會丟 TypeError）。
// 否則看 e.payload，若也是 null/undefined ⇒ 回 undefined。
// 否則回 e.payload.detail 的值。
// 後面的 || 又在幹嘛？
// 當 e?.payload?.detail 拿不到值（是 undefined、null、''、0、false 等 falsy）時，就會用右邊的備援