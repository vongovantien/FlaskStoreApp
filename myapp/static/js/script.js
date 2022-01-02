function addToCart(id, name, price) {
    event.preventDefault();
    fetch("/api/add-to-cart", {
        method: 'post',
        body: JSON.stringify({
            "id": id,
            "name": name,
            "price": price
        }),
        headers: {
            "Content-Type": "application/json"
        }
    }).then(function(res) {
        console.info(res)
        return res.json()
    }).then(function(data) {
        console.info(data)

        let counter = document.getElementsByClassName("cart-counter")
        for(let i = 0; i < counter.length; i++){
            counter[i].innerText = data.total_quantity
        }
    }).catch(function(err) {
        console.error(err)
    })
}

function updateCart(id, obj){
    fetch('/api/update-cart', {
        method: 'put',
        body: JSON.stringify({
            'id': id,
            'quantity': parseInt(obj.value)
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(res => res.json()).then(data => {
        let counter = document.getElementsByClassName("cart-counter")
        for(let i = 0; i < counter.length; i++)
            counter[i].innerText = data.total_quantity

        let amount = document.getElementById('total-amount')
        amount.innerText = new Intl.NumberFormat().format(data.total_amount)
    })
}

function deleteCart(id) {
    if(confirm("Bạn có muốn xóa sản phẩm này không ?") == true){
        fetch("/api/delete-cart/" + id, {
            method: 'delete',
            headers: {
                "Content-Type": "application/json"
            }
        }).then(function(data) {
            let counter = document.getElementsByClassName("cart-counter")
            for(let i = 0; i < counter.length; i++)
                counter[i].innerText = data.total_quantity

            let amount = document.getElementById('total-amount')
            amount.innerText = new Intl.NumberFormat().format(data.total_amount)

            let e = document.getElementById("product" + id)
            e.style.display = "none"
        }).catch(function(err) {
            console.error(err)
        })
    }
}

function pay() {
    if(confirm("Bạn có muốn thanh toán không ??") == true){
        fetch("/api/pay", {
            method: 'post'
        }).then(res => res.json()).then(data => {
            if(data.code = 200){
                location.reload()
            }
        }).catch(err => console.error(err))
    }
}

function addComment(product_id){
    let content = document.getElementById('commentId');
    if (content !== null){
        fetch('/api/comments', {
            method: "post",
            body: JSON.stringify({
                   'product_id':product_id,
                   'content' :content.value
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(res => res.json()).then(data => {
            console.log(data)
            if(data.status = 201)
            {
                let c = data.comment
                let area = document.getElementById('commentArea')
                area.innerHTML = ` <li>
                                        <div class="review-heading">
                                            <h5 class="name">${ c.user.username }</h5>
                                            <p class="date my-date"><em>${ moment(c.created_date).fromNow() }</em></p>
                                            <div class="review-rating">
                                                <i class="fa fa-star"></i>
                                                <i class="fa fa-star"></i>
                                                <i class="fa fa-star"></i>
                                                <i class="fa fa-star"></i>
                                                <i class="fa fa-star-o empty"></i>
                                            </div>
                                        </div>
                                        <div class="review-body">
                                            <p>${ c.content }</p>
                                        </div>
                                    </li>` + area.innerHTML
            }
            else if(data.status = 404){
                console.log(data.err_msg)
            }
        })
    }
}