document.getElementById('add-gift').onclick = function() {
    document.getElementById('gift-modal').style.display = 'block';
};

function closeModal() {
    document.getElementById('gift-modal').style.display = 'none';
}

function addGift() {
    var newGift = document.getElementById('new-gift').value;
    if (newGift) {
        var giftList = document.querySelector('.presentes-ideas');
        var newGiftItem = document.createElement('div');
        newGiftItem.classList.add('gift-item');
        newGiftItem.innerHTML = `<p>🎁 <span>${newGift}</span></p>`;
        giftList.appendChild(newGiftItem);
        document.getElementById('gift-modal').style.display = 'none';
    }
}
