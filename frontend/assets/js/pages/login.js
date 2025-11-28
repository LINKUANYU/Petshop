// common.js
import { fetch_data, handle_api_error} from "./common.js";

// login
const login_form = document.querySelector('#login-form');
const msg = document.querySelector('#msg');

login_form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.querySelector('#email').value.trim();
    const password = document.querySelector('#pw').value;
    if (!email || !password) return msg.textContent = "請輸入完整資訊";
    if (password.length < 8) return msg.textContent = "密碼最少為8個字元";

    try{
        const res = await fetch_data("/api/login", {
            method: "POST",
            headers: {'content-type': 'application/json'},
            body:JSON.stringify({email, password})
        });
        // 後端回傳ok，轉跳
        let second = 3;
        msg.textContent = `登入成功，${second}秒後轉跳`;
        const timer = setInterval(() => {
            second -= 1;
            if (second < 0){
                clearInterval(timer);
                window.location.href = "/";
                return
            } else {
                msg.textContent = `登入成功，${second}秒後轉跳`;
            }
        }, 1000);
    }catch (e){
        // 在登入頁面不轉跳首頁，設定options的redirect_on_401屬性為false
        const err_msg = handle_api_error(e, {redirect_on_401: false});
        if (err_msg){
        msg.textContent = err_msg;
        }
    }

});
