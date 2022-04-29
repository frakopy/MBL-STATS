

const date = new Date();

//We use slice(-2) for getMonth and gateDate because wen we have a number with 2 digits for example in the day number 30
//it will result in 030 so when we say slice(-2) we are getting only the 2 last digits and for month and day with only one digit
//we again are only getting the 2 last digits of course in this situation there is only 2.
const today = (date.getFullYear() + "-"  + ("0"+(date.getMonth()+1)).slice(-2) + "-" + ("0" + date.getDate()).slice(-2));
const inputDate =  document.getElementById('input-date');
inputDate.value = today;

const divStats = document.getElementById('stats-results');
const tbodyTableGames = document.getElementById('tbody-table-games');
const animation = document.getElementById('animation');

const tblGamesHeaders = document.getElementById('table-games-headers')
const tblGames = document.getElementById('table-games')
const tblGamesPlayed = document.getElementById('tbl-games-played')

const tbodyGamesResults = document.getElementById('tbody-games-results')

//-------------------- Displaying the statistics in the web page ----------------------------------
function showStats (sts) {
    
    //convert the object in array of objects for use sort method and later order by id
    const arrayObjects = Object.keys(sts).map(key => { 
        return sts[key];
    })

    arrayObjects.sort((a, b) => a.id - b.id) //Order the array of Objects
    
    const fragment = document.createDocumentFragment()
    for(const obj of arrayObjects) {
        const h2 =  document.createElement('h2')
        h2.textContent = obj.title
        fragment.appendChild(h2)

        const divTable = document.createElement('div')
        divTable.classList.add('table-sts')
        divTable.innerHTML = `${obj.stats_data}`
        fragment.appendChild(divTable)

    }
    divStats.appendChild(fragment)
    //For display pretty the tables after scroll
    ScrollReveal().reveal('.table-sts', { delay: 500 });
    animation.classList.toggle('hide') //hide our animation after all stas has been displayed
    inputDate.disabled =  false //Enable again input date box for choose another date
    inputDate.style.color = 'black' //Change the color text
}

//-------------------- Sending get request to the backend for getting stats -------------------------
const getStats = async (urls_stats) => {

    const fetchSettings = {
        method : 'POST',
        body: JSON.stringify({urls_sts: urls_stats}),
        headers: {"content-type": "application/json; charset=UTF-8"}
    }

    try{
        const request = await fetch('/get_stats', fetchSettings)
        const result = await request.json()
        return result
    }catch(error){
        return error
    }
}

//--------------------- Change the first letter of the team1 and team2 to Upper ------------------------
function changeToUpperCase(str){
    const stringParts = str.split('-')
    let wordToUpperCase = ''
    for(let cad of stringParts){
        const firstLetter = cad.charAt(0).toUpperCase()
        wordToUpperCase += firstLetter + cad.slice(1) + ' '
    }
    return wordToUpperCase
}

//------------------------- Displaying the Games schedules in the web page ------------------------------------
function showGames (games) {
    const fragment = document.createDocumentFragment()
    const urls_stats = games['urls_stats']
    let team1, team2, pitchers
    for(key in games){
        if(key !== 'urls_stats'){
            [team1, team2, pitchers] = games[key]
            const tr = document.createElement('tr')
            if(team1.includes('-')){
                team1 = changeToUpperCase(team1)
            }else{
                const firstLetter = team1.charAt(0).toUpperCase()
                team1 = firstLetter + team1.slice(1)
            }
            
            if(team2.includes('-')){
                team2 = changeToUpperCase(team2)
            }else{
                const firstLetter = team1.charAt(0).toUpperCase()
                team1 = firstLetter + team1.slice(1)
            }
    
            tr.innerHTML = `
                <td>${team1}</td>
                <td><span>VS</span></td>
                <td>${team2}</td>
                <td>${pitchers}</td>
            `
            fragment.appendChild(tr)
        }
    }
    tbodyTableGames.appendChild(fragment)

    //Initially this element has the class hide so toggle remove it for show the animation
    animation.classList.toggle('hide')

    // calling the function that request to the backend for pitchersvsbatter stats
    getStats(urls_stats).then(result => showStats(result))

}



//----------- Sending Post to the backend with the date data for get the games scheduled -----------------------------

const get_games = async (dateToSend, route) => {

    //Disable for wait to load all stats data, it is enable after at the end of the function showStats()
    inputDate.disabled =  true

    //Change the color text of the input date element
    inputDate.style.color = 'white' 

    const fetchSettings = {
        method : 'POST',
        body: JSON.stringify({date: dateToSend}),
        headers: {"content-type": "application/json; charset=UTF-8"}
    }

    try{
        const request = await fetch(route, fetchSettings)
        const result = await request.json()
        return result
    }catch(error){
        return error
    }
}

//Getting the date from the input date element 
let dateToSend = inputDate.value

//Call the async function for get the games
get_games(dateToSend, '/get_games').then(result => {showGames(result)})


//------------------------- Displaying the Games Results in the web page ------------------------------------
function showGamesResults (games) {
    const fragment = document.createDocumentFragment()
    for(key in games){
        let [team1, team2, result, win, loss] = games[key]
        const tr = document.createElement('tr')
        
        if(team1.includes('-')){
            team1 = changeToUpperCase(team1)
        }else{
            const firstLetter = team1.charAt(0).toUpperCase()
            team1 = firstLetter + team1.slice(1)
        }
        
        if(team2.includes('-')){
            team2 = changeToUpperCase(team2)
        }else{
            const firstLetter = team1.charAt(0).toUpperCase()
            team1 = firstLetter + team1.slice(1)
        }

        tr.innerHTML = `
            <td>${team1}</td>
            <td>${team2}</td>
            <td>${result}</td>
            <td>${win}</td>
            <td>${loss}</td>
        `
        fragment.appendChild(tr)
    }
    tbodyGamesResults.appendChild(fragment)

    //Initially this element has the class hide so toggle remove it for show the animation
    animation.classList.toggle('hide')
    
    // calling the function that request to the backend for pitchersvsbatter stats
    getStats().then(result => showStats(result))
}



//-------------------- Compare the date from the input date element with the actual date----------------------------------
const compareDate = (date) => {
    const dateSelected = new Date(date)
    const dateToday =  new Date(today)
    return dateSelected < dateToday ? true : false
}

//Listen when the input change, this will happen when the user choose anoter date
inputDate.addEventListener('change', (e) => {

    tbodyTableGames.innerHTML = '' //Deleting all HTML content from the table that display games
    divStats.innerHTML = '' //Deleting all HTML content from the table that display Pitchers vs Batters Stats
    tbodyGamesResults.innerHTML = '' //Deleting all HTML content from the table that display the results of the games

    dateToSend = e.target.value
    const dateIsOlder = compareDate(dateToSend) //call the function that compares the date selected with actual date

    if(dateIsOlder){
        tblGamesHeaders.classList.add('hide') //This class will be added to
        tblGames.classList.add('hide') //This class will be added to
        tblGamesPlayed.classList.remove('hide') //This class will be removed
        get_games(dateToSend, '/get_games_results').then(result => {showGamesResults(result)}) //call the function that make the request to the backend for get the games
    }else{
        tblGamesHeaders.classList.remove('hide') //This class will be added to
        tblGames.classList.remove('hide') //This class will be added to
        tblGamesPlayed.classList.add('hide') //This class will be removed
        //call the function that make the request to the backend for get the games
        get_games(dateToSend, '/get_games').then(result => {showGames(result)})
    }

})

//Avoide user write in the input field, so he just choose the calendar option
inputDate.addEventListener("keydown", (e) => {
    e.preventDefault()
})


