let progressStep = ['12', '24', '45', '60', '75','100'];
let steps = ['step1', 'step2', 'step3', 'step4', 'step5', 'step6']

setInterval(()=>{
    location.reload()
}, 10000)


renderProgress();

function renderProgress(){
    let data = document.querySelector('#planComponent').getAttribute('value').replace(/'/g, '"');
    data = data.replaceAll('False', 'false')
    data = data.replaceAll('True', 'true')
    data = JSON.parse(data);
    for (item in data[0]['state']){    
        if (data[0]['state'][item]['status'] === 'reached') {
            let progressElement = document.querySelector('div.progress-bar');
            progressElement.setAttribute('style', `width: ${progressStep[item]}%;`);
            let stepItem = document.querySelector(`#${steps[item]}`)
            stepItem.className = 'active'
        }
    }    
}

