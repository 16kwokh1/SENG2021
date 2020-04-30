if (document.readyState == 'loading') {
    document.addEventListener('DOMContentLoaded', ready)
} else {
    console.log('ready')
    ready()
}

function ready() {

    var addToCartButtons = document.getElementsByClassName('addtocart-coles')
    for (var i = 0; i < addToCartButtons.length; i++) {
        var button = addToCartButtons[i]
        button.addEventListener('click', addToCartClicked)
    }

    var addToCartButtons = document.getElementsByClassName('addtocart-woolies')
    for (var i = 0; i < addToCartButtons.length; i++) {
        var button = addToCartButtons[i]
        button.addEventListener('click', addToCartClicked)
    }

}

function addToCartClicked(event) {
    var button = event.target
    var shopItem = button.parentElement
    var title = shopItem.getElementsByClassName('font')[0].innerText
    postData = {shop: button.className, name: title}
    console.log(postData)

    $.ajax({
        url: "/remove_cart",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify(postData),
        success: function (data) {
            console.log(data.title);
            console.log(data.article);
        },
    }); 

}

