(function (){
    function makeHeaderItem(text){
        const d = document.createElement('div');
        d.className = 'header-item';
        d.textContent = text;
        return d;
    }

    function buildHeader(){
        const header = document.createElement('header');

        const main_width = document.createElement('div');
        main_width.className = 'main-width';

        const first_row = document.createElement('div');
        first_row.className = 'flex header-1';

        const left1 = document.createElement('div');
        left1.className = 'left';

        left1.append(
            makeHeaderItem('賣家中心'),
            makeHeaderItem('開始隨拍即賣囉！'),
            makeHeaderItem('下載'),
            makeHeaderItem('追蹤我們')
        );

        const right1 = document.createElement('div');
        right1.className = 'right';
        
        right1.append(
            makeHeaderItem('通知'),
            makeHeaderItem('幫助中心'),
            makeHeaderItem('繁體中文'),
            makeHeaderItem('註冊'),
            makeHeaderItem('登入'),
        );

        first_row.append(left1, right1);

        const second_row = document.createElement('div');
        second_row.className = 'flex header-2';

        const left2 = document.createElement('a');
        left2.id = 'left';
        left2.href = '/'
        const imgShop = document.createElement('img');
        imgShop.id = 'shopme';
        imgShop.src = '/static/shopme.jpg';
        left2.appendChild(imgShop);

        const middle = document.createElement('div');
        middle.id = 'middle';
        const form = document.createElement('form');
        form.id = 'search-bar';
        const input = document.createElement('input');
        input.id = 'search';
        const btn = document.createElement('button');
        btn.type = "button";
        btn.id = 'search-btn';
        const imgSearch = document.createElement('img');
        imgSearch.id = 'search-icon';
        imgSearch.src = '/static/search.png';
        btn.appendChild(imgSearch);
        form.append(input, btn);
        
        const under = document.createElement('div');
        under.className = 'item-undersearch';
        for (let i = 0; i < 6; i++) {
            const s = document.createElement('div');
            s.className = 'small-word';
            s.textContent = '更多商品';
            under.appendChild(s);
            }
        middle.append(form, under);

        const right2 = document.createElement('a');
        right2.id = 'right';
        right2.href = '/';
        const imgCart = document.createElement('img');
        imgCart.id = 'cart';
        imgCart.src = '/static/cart.jpg';
        imgCart.alt = 'Cart';
        right2.appendChild(imgCart);
        second_row.append(left2, middle, right2);

        main_width.append(first_row, second_row);
        header.appendChild(main_width);
        return header;
    }
    
    window.mountHeader = function (target){
        const h = buildHeader();
        if (!target){
            document.body.insertBefore(h, document.body.firstChild);
        }else{
            let root;
            if (typeof target === 'string'){
                root = document.querySelector(target);
                root.append(h);
            }
        }
        return h;
    };

})();