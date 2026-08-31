let cart = {};

// Элементы
const cartButton = document.getElementById('cart-button');
const cartSidebar = document.getElementById('cart-sidebar');
const overlay = document.getElementById('overlay');
const cartItemsContainer = document.getElementById('cart-items');
const cartTotal = document.getElementById('cart-total');
const cartCount = document.getElementById('cart-count');
const closeCartBtn = document.getElementById('close-cart');
const checkoutBtn = document.getElementById('checkout-btn');
const orderModal = document.getElementById('order-modal');
const closeModalBtn = document.getElementById('close-modal');
const orderForm = document.getElementById('order-form');
const categoryButtons = document.querySelectorAll('.category-btn');
const productCards = document.querySelectorAll('.product-card');

// --- Корзина ---

function saveCart() {
    localStorage.setItem('cafe_cart', JSON.stringify(cart));
}

function loadCart() {
    const saved = localStorage.getItem('cafe_cart');
    if (saved) {
        cart = JSON.parse(saved);
    }
}

function updateCartUI() {
    cartItemsContainer.innerHTML = '';
    let total = 0;
    let count = 0;

    for (const [id, item] of Object.entries(cart)) {
        total += item.price * item.qty;
        count += item.qty;

        const div = document.createElement('div');
        div.className = 'cart-item';
        div.innerHTML = `
            <div class="cart-item-info">
                <strong>${item.name}</strong>
                <p>${item.price} ₽ x ${item.qty} = ${item.price * item.qty} ₽</p>
            </div>
            <div class="cart-item-controls">
                <button class="decrease" data-id="${id}">−</button>
                <span>${item.qty}</span>
                <button class="increase" data-id="${id}">+</button>
                <button class="remove" data-id="${id}">✕</button>
            </div>
        `;
        cartItemsContainer.appendChild(div);
    }

    cartTotal.textContent = total;
    cartCount.textContent = count;
    saveCart();
}

function addToCart(id, name, price) {
    if (cart[id]) {
        cart[id].qty += 1;
    } else {
        cart[id] = { name, price, qty: 1 };
    }
    updateCartUI();
}

function changeQty(id, delta) {
    if (cart[id]) {
        cart[id].qty += delta;
        if (cart[id].qty <= 0) {
            delete cart[id];
        }
        updateCartUI();
    }
}

function removeFromCart(id) {
    delete cart[id];
    updateCartUI();
}

// --- Фильтр категорий ---

categoryButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        categoryButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const category = btn.dataset.category;

        productCards.forEach(card => {
            if (category === 'all' || card.dataset.category === category) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    });
});

// --- Открытие/закрытие корзины и модалки ---

function openCart() {
    cartSidebar.classList.add('open');
    overlay.classList.add('show');
}

function closeCart() {
    cartSidebar.classList.remove('open');
    overlay.classList.remove('show');
}

function openModal() {
    orderModal.classList.add('open');
    overlay.classList.add('show');
    cartSidebar.classList.remove('open');
}

function closeModal() {
    orderModal.classList.remove('open');
    overlay.classList.remove('show');
}

// --- Обработчики событий ---

productCards.forEach(card => {
    const btn = card.querySelector('.add-to-cart');
    btn.addEventListener('click', () => {
        const id = card.dataset.id;
        const name = card.dataset.name;
        const price = parseFloat(card.dataset.price);
        addToCart(id, name, price);
    });
});

cartItemsContainer.addEventListener('click', (e) => {
    const target = e.target;
    const id = target.dataset.id;
    if (target.classList.contains('increase')) {
        changeQty(id, 1);
    } else if (target.classList.contains('decrease')) {
        changeQty(id, -1);
    } else if (target.classList.contains('remove')) {
        removeFromCart(id);
    }
});

cartButton.addEventListener('click', openCart);
closeCartBtn.addEventListener('click', closeCart);
overlay.addEventListener('click', () => {
    closeCart();
    closeModal();
});

checkoutBtn.addEventListener('click', () => {
    if (Object.keys(cart).length === 0) {
        alert('Корзина пуста!');
        return;
    }
    openModal();
});

closeModalBtn.addEventListener('click', closeModal);

orderForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(orderForm);
    const customer = {
        name: formData.get('name'),
        phone: formData.get('phone'),
        address: formData.get('address'),
        comment: formData.get('comment'),
    };

    const items = Object.entries(cart).map(([id, item]) => ({
        id: parseInt(id),
        name: item.name,
        price: item.price,
        qty: item.qty,
    }));

    try {
        const response = await fetch('/order', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ customer, items }),
        });
        const result = await response.json();
        if (result.success) {
            alert(result.message);
            cart = {};
            updateCartUI();
            orderForm.reset();
            closeModal();
        }
    } catch (error) {
        alert('Ошибка отправки заказа');
        console.error(error);
    }
});

// Инициализация
loadCart();
updateCartUI();
