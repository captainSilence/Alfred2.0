let errorSection = document.querySelector('#error-section');
let data = document.querySelector('#error_message').getAttribute('value');

data = JSON.parse(data)


let errorRows;
let tableElement = document.createElement('table')
tableElement.setAttribute('class', 'table table-striped table-hover bg-white')
let tableHead = document.createElement('thead');
let tableBody = document.createElement('tbody');
for (key in data) {    
    let row = document.createElement('tr');
    let thValue = document.createElement('th');
    thValue.innerHTML = key;
    row.appendChild(thValue);
    tableHead.appendChild(row)
    console.log(data[key]['error'])
    
    for (errorNumb in data[key]['error']){                        
        let object = data[key]['error'][errorNumb] 
        for (error in object){            
            let row = document.createElement('tr');
            let tdKey = document.createElement('td');
            tdKey.innerText = error
            let tdValue = document.createElement('td');
            tdValue.innerHTML = object[error]
            row.appendChild(tdKey)
            row.appendChild(tdValue)
            tableBody.appendChild(row)    
        }
        
    }
}
tableElement.appendChild(tableHead);
tableElement.appendChild(tableBody);

errorSection.appendChild(tableElement);
// let tableElement = document.querySelector('table');
// console.log(tableElement)
// tableElement.className = 'table table-striped table-hover bg-white'