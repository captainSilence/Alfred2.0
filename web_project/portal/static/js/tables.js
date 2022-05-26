

// Load the Data
const data = JSON.parse(document.querySelector('#params').getAttribute('value').replace(/'/g, '"'));


// Apply Filter to Data
let filterElement = document.querySelector('#filter')

let filteredData = data;
filterElement.addEventListener('keyup', () => {   
    filteredData = []     
    let filterString = filterElement.value.toUpperCase();
    for (key in data) {                
        if (data[key].customer_name.toUpperCase().includes(filterString)) { 
            filteredData.push(data[key])            
        }
    }
    sliceData(filteredData)
})


let currentPage = 1

let maxPageNumber = 4
let chunk = 5;
let arrayData = [];
let pages = [];

sliceData(filteredData);


let activeButton;
let buttonOne = document.querySelector(`#page-1`)
buttonOne.focus();



// Current Page Selection

function clickedButton(object){    
    currentPage = object.text  
    renderTable(arrayData)
    
}

// Data Slicing

function sliceData(filteredData){

    arrayData = []
    pages = []
    let i, j, dataSlice;
    
    for (i=0, j=filteredData.length; i < j; i += chunk) {
        dataSlice = filteredData.slice(i, i + chunk);
        arrayData.push(dataSlice)    
    }
            
    for (let i =1; i<=arrayData.length && i <= maxPageNumber; i++) {    
        pages.push(i)
    }    
    
    renderTable(arrayData)
    buildPaginator(pages)
}


// Pagination
function buildPaginator(pages){
    let paginationList = document.querySelector('#pagination-list');
    paginationList.innerHTML = ''
    let previousButton = document.createElement('li.page-item')
    previousButton.innerHTML ='\
    <a class="page-link" aria-label="Previous" id="chevron-left">\
    <span aria-hidden="true">&laquo;</span>\
    </a>'
    paginationList.appendChild(previousButton)
    
    
    for (let i = 0; i <= maxPageNumber-1 && typeof pages[i] !== "undefined"; i++) {             
        let listElement = document.createElement('li.page-item');
        listElement.innerHTML=`<a id="page-${pages[i]}" href="#" class="page-link"  onclick="clickedButton(this)">${pages[i]}</a>`    
        paginationList.appendChild(listElement)        
    }
    
    let nextButton = document.createElement('li.page-item')
    nextButton.innerHTML ='\
    <a class="page-link" aria-label="Next" id="chevron-rigth">\
    <span aria-hidden="true">&raquo;</span>\
    </a>'
    paginationList.appendChild(nextButton)
    
    let previous = document.querySelector('#chevron-left')
    let next = document.querySelector('#chevron-rigth')
    previous.addEventListener('click', chevronLeft)
    next.addEventListener('click', chevronRigth)
}

function chevronRigth() {
    if (pages[pages.length -1] < arrayData.length){
        pages = pages.map(i => 1 + i)    
    }
    buildPaginator(pages)
    try {
        
        activeButton = document.querySelector(`#page-${currentPage}`)        
        activeButton.focus()
    } catch {}
    
}

function chevronLeft(){
    if (pages[0] > 1) {
        pages = pages.map(i => i - 1)
    }
    buildPaginator(pages)
    try {
        
        activeButton = document.querySelector(`#page-${currentPage}`)        
        activeButton.focus()
    } catch {}

    
    
}




// Render Table

function renderTable(arrayData) {    
    let tbody = document.querySelector('#tbody');
    tbody.innerHTML = '';
    let data;
    

    if (arrayData.length == 1){
        data = arrayData[0]        
    } else {
        data = arrayData[currentPage - 1]    
    }
    
    
    for (key in data){        
        let row = document.createElement('tr')                                          
        html = `\
        <td>${data[key].id}</td>\
        <td>${data[key].customer_name}</td>\
        <td>${data[key].vlan_number}</td>\
        <td>${data[key].switch}</td>\
        <td>${data[key].router}</td>\
        <td>${data[key].last_state}</td>\
        <td>${data[key].ticket}</td>\
        <td><a href="/details/${data[key].customer_name}/${data[key].vlan_number}"><input type="button" class="btn btn-primary" value="Details"></a></td>\
        <td><a href="/config/${data[key].customer_name}/${data[key].vlan_number}"><input type="button" class="btn btn-primary" value="Configuation"></a></td>`
            
        
        row.innerHTML = html
        tbody.appendChild(row)

    }
}


