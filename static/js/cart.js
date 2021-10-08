var updateBtns = document.getElementsByClassName('update-cart')

for (i = 0; i< updateBtns.length; i++){
    updateBtns[i].addEventListener('click', function(){
        var productId = this.dataset.productId
        var action = this.dataset.action
        console.log("productId:", productId, 'Action:', action)

        console.log('USER',user)
        if (user === "AnonymousUser"){
            console.log('No logged in')
        }else
            console.log("user is logged in sending data")
    })
}   

function updateUserOrder(productId, action){
    console.log('User is logged in, sending data')

    var url ='/update_item'
}