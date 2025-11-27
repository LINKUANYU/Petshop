const form = document.querySelector('#form-signup');
const msg = document.querySelector('#msg');

form.addEventListener('submit', async function(e){
    e.preventDefault();
    msg.textContent = '';
    const name = document.querySelector('#signup-name').value.trim();
    const email = document.querySelector('#signup-email').value.trim();
    const password = document.querySelector('#signup-pw-1').value;
    const password_2 = document.querySelector('#signup-pw-2').value;
    
    if (!name || !email || !password || !password_2) return msg.textContent = "請輸入完整資訊";
    if (password.length < 8) return msg.textContent = "密碼最少為8個字元";
    if (password != password_2) return msg.textContent = "密碼確認失敗";

    try {
        const body = await fetch_data("/api/signup", {
            method: "POST",
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name, email, password})
        });

        msg.textContent = `${body.message}`;
        if (body.ok){
            const link = document.createElement('a');
            link.href = '/login';
            link.textContent = "前往登入"
            msg.append(link);
        }
    } catch(e) {
        const err_msg = handle_api_error(e);
        if (err_msg){
            msg.textContent = err_msg;
        }
    }
});
