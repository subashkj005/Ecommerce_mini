function togglePaginationDivs(hasProducts) {
    const initialPaginationContainer = document.getElementById('initialPaginationContainer');
    const newPaginationTemplate = document.getElementById('paginationTemplate');

    if (hasProducts) {
        initialPaginationContainer.style.display = 'none';
        newPaginationTemplate.style.display = 'block';
    } else {
        initialPaginationContainer.style.display = 'block';
        newPaginationTemplate.style.display = 'none';
    }
}



// Filtering function

const filterCheckBoxes = document.querySelectorAll(".category-checkbox");


let checkedFilterCheckBox = [];

for(const checkbox of filterCheckBoxes) {
    checkbox.addEventListener("change", ()=> {
        if(checkbox.checked) {
            checkedFilterCheckBox.push(checkbox.value);
        } else {
            checkedFilterCheckBox = checkedFilterCheckBox.filter(id => id !== checkbox.value);
        }
        fetchData();
    })
}

async function fetchData () {
    const body = {
        categories: checkedFilterCheckBox
    }

    const url = '/product_list/filter-products';
    const option = {
        method: 'POST',
        headers: {
            'Content-Type' : 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(body)
    }
    try {
        const response = await fetch(url, option);
        if (response.ok) {
            const data = await response.json();
            buildProducts(data.products); // Assuming data.products contains the products array
            togglePaginationDivs(data.products.length > 0); // Assuming you have a function called insertPagination for handling the pagination
            insertPagination(data);
        } else {
            console.log('Error fetching data:', response.statusText);
        }
    } catch (error) {
        console.log('Error fetching data:', error);
    }
}


const ProductTemp = document.getElementById('product-template');
const productContainer = document.getElementById('filteredProducts');


function buildProducts (data){
    productContainer.innerHTML = '';
    for(let product of data) {
        const productCard = ProductTemp.content.cloneNode(true);
        productCard.querySelector('.product-image').src = product.image_url;
        productCard.querySelector('.product-link').href = `/product_list/product${product.variant_id}`;
        productCard.querySelector('.product-category').innerText = product.category_name; 
        productCard.querySelector('.product-name').innerText = product.name;
        productCard.querySelector('.product-color').innerText = product.colour_name;

         // Check if the product has a valid and active offer
         if (product.has_offer) {
            // Display offer price and original price
            productCard.querySelector('.label-sale').innerText = 'Sale';
            productCard.querySelector('.offer-price').innerText = 'Rs. '+product.offer_price;
            productCard.querySelector('.offer-orginal-price').innerText = 'Rs. '+product.original_price;
        } else {
            // Display regular price
            productCard.querySelector('.label-sale').classList.add('hidden');
            productCard.querySelector('.offer-price-two').innerText = 'Rs. '+product.offer_price;
        }

        productContainer.appendChild(productCard);
    }
}


// pagination

function insertPagination(data) {
    const paginationContainer = document.getElementById('paginationContainer');
    paginationContainer.innerHTML = '';

    if (data.has_previous) {
        const prevPageLink = createPaginationLink(data.previous_page_number, 'Previous');
        paginationContainer.appendChild(prevPageLink);
    }

    for (let num of data.paginator.page_range) {
        const pageLink = createPaginationLink(num, num);
        if (data.products.number === num) {
            pageLink.classList.add('active');
        }
        paginationContainer.appendChild(pageLink);
    }

    if (data.has_next) {
        const nextPageLink = createPaginationLink(data.next_page_number, 'Next');
        paginationContainer.appendChild(nextPageLink);
    }
}

function createPaginationLink(pageNumber, text) {
    const link = document.createElement('a');
    link.classList.add('page-link');
    if (pageNumber >= 1) {
        link.href = `?page=${pageNumber}`;
    } else {
        link.href = '#'; // Use a placeholder link for page numbers less than 1
        link.classList.add('disabled'); // Add a class to indicate that the link is disabled
    }
    link.textContent = text;
    return link;
}
