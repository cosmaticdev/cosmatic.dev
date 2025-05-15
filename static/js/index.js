let currentState = 'intro';
let lastScrollY = window.scrollY;

window.addEventListener('wheel', (event) => {
    const topSection = document.getElementById('topSection');
    const mainContent = document.getElementById('mainContent');
    const cornerWidget = document.getElementById('corner-widget');

    const scrollDirection = event.deltaY > 0 ? 'down' : 'up';
    const nearTop = window.scrollY <= mainContent.getBoundingClientRect().top + window.scrollY + 10;

    if (scrollDirection === 'down' && currentState === 'intro') {
        topSection.classList.add('out');
        mainContent.classList.add('show');
        currentState = 'main';

        const preventScroll = (event) => {
            event.preventDefault();
        };
        window.addEventListener('wheel', preventScroll, { passive: false });

        // Snap to top of main content
        setTimeout(() => {
            window.scrollTo({
                top: mainContent.offsetTop - 10,
                behavior: 'smooth'
            });
        }, 100);
        window.removeEventListener('wheel', preventScroll);
    }

    if (scrollDirection === 'up' && currentState === 'main' && nearTop) {
        topSection.classList.remove('out');
        mainContent.classList.remove('show');
        currentState = 'intro';

        const preventScroll = (event) => {
            event.preventDefault();
        };
        window.addEventListener('wheel', preventScroll, { passive: false });

        setTimeout(() => {
            window.scrollTo({
                top: window.top,
                behavior: 'smooth'
            });
        }, 100);

        window.removeEventListener('wheel', preventScroll);
    }

    lastScrollY = window.scrollY;
});

window.addEventListener('load', () => {
    window.scrollTo(0, 0);
});

window.addEventListener('beforeunload', () => {
    window.scrollTo(0, 0);
});

let connectionScore = 2;

const data = await loadJson();

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

if (data.Spotify["@attr"] != null) {
    if (data.Spotify["@attr"].nowplaying == "true") {
        const recordImage = document.getElementById("recordImage");
        recordImage.src = data.Spotify.image[2]["#text"];
        document.getElementById("currentlyListening").textContent = await condenseString(`Currently listening to ${data.Spotify.name} by ${data.Spotify.artist["#text"]}`, 50);
        document.getElementById("corner-widget").style.visibility = "visible";
    }
}

document.getElementById("greenbutton").onclick = acceptCat;
document.getElementById("redbutton").onclick = declineCat;

async function updateCountdown() {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    const bannedUntil = parts.pop().split(';')[1].split("=")[1];

    const expireTime = new Date(Number(bannedUntil * 1000)).getTime();
    function tick() {
        const now = new Date().getTime();
        const timeLeft = expireTime - now;

        if (timeLeft <= 0) {
            document.cookie = "BANNED=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
            window.location.reload();
            return;
        }

        const seconds = Math.floor((timeLeft / 1000) % 60);
        const minutes = Math.floor((timeLeft / 1000 / 60) % 60);
        const hours = Math.floor((timeLeft / 1000 / 60 / 60) % 24);

        document.getElementById("banCountdown").innerHTML = `This is what you get for being a cat hater<br>You're banned for another ${hours} hours ${minutes} minutes ${seconds} seconds`;
        setTimeout(tick, 1000);
    }
    tick();
}

if ((document.cookie.split("; ").some(cookie => cookie.startsWith("BANNED=")))) {
    document.getElementById('catVert').style.background =
        "radial-gradient(circle, transparent 55%, rgba(255, 0, 0, 0.7) 100%)";

    document.getElementById('angryCatPopup').style.display = 'block';
    document.body.style.overflow = "hidden"; // Disable scrolling
    const catPopup = document.getElementById('catVert');
    let x = document.createElement('h1');
    x.textContent = '. . .';
    x.id = "banCountdown";
    catPopup.appendChild(x);
    document.getElementById('angryCatPopup').style.visibility = 'visible';
    document.getElementById('angryCatPopup').style.opacity = '1';
    await updateCountdown();
}

// cat cookie stuff
if (!(document.cookie.split("; ").some(cookie => cookie.startsWith("cat=")))) {
    document.getElementById('cookiePopup').style.visibility = 'visible';
    document.getElementById('cookiePopup').style.opacity = '1';

} else {
    document.getElementById('cookiePopup').style.display = 'none';
}

function acceptCat() {
    document.getElementById('angryCatPopup').remove();
    document.querySelectorAll("#cookiePopupText > *:not(h1)").forEach(el => {
        el.style.display = "none";
    });
    document.getElementById('cookiePopup').remove();
    document.body.style.overflow = ""; // Restore scrolling

    const d = new Date();
    d.setTime(d.getTime() + (100 * 24 * 60 * 60 * 1000));
    const expires = "; expires=" + d.toUTCString();
    document.cookie = "cat=ᓚᘏᗢ  ₍^. .^₎⟆;" + expires + ";path=/";
}

async function declineCat() {
    document.getElementById('catVert').style.background =
        "radial-gradient(circle, transparent 55%, rgba(255, 0, 0, 0.7) 100%)";

    document.getElementById('angryCatPopup').style.display = 'block';
    document.body.style.overflow = "hidden"; // Disable scrolling
    const catPopup = document.getElementById('catVert');
    let x = document.createElement('h1');
    x.textContent = '. . .';
    catPopup.appendChild(x);
    document.getElementById('angryCatPopup').style.visibility = 'visible';
    document.getElementById('angryCatPopup').style.opacity = '1';
    await delay(2000);
    x.textContent = 'I think you hit the wrong button. Wanna try again?';
    let catHori = document.createElement('div');
    catHori.classList = 'center';
    catPopup.appendChild(catHori);
    let b1 = document.createElement('button');
    let b2 = document.createElement('button');
    b1.textContent = "Hell no";
    b1.classList = "redbutton"
    b2.textContent = "I've repent and I love cats";
    b2.classList = "greenbutton"
    b2.onclick = acceptCat;
    catHori.appendChild(b1);
    catHori.appendChild(b2);

    b1.onclick = async function () {
        b1.style.visibility = "hidden";
        b2.style.visibility = "hidden";
        x.textContent = '. . .';
        await delay(2000);
        x.innerHTML = 'How about I give you one more try?<br>There *will* be consequences if you answer wrong.';
        await delay(1500);
        b1.textContent = "I really hate cats"
        b2.textContent = "I really love cats"
        b1.style.visibility = "visible";
        b2.style.visibility = "visible";

        b1.onclick = async function () {
            b1.style.visibility = "hidden";
            b2.style.visibility = "hidden";
            x.innerHTML = "Thats the last straw, nerd. <br>Come back when you're ready to love cats.<br>Take this next day to reflect on your life.";
            let y = document.createElement('h2');
            y.textContent = "You're banned for 24 hours";
            catPopup.append(y);

            const d = new Date();
            d.setTime(d.getTime() + (1 * 24 * 60 * 60 * 1000));
            document.cookie = "BANNED=" + String(Math.floor(Date.now() / 1000) + 60 * 60 * 24) + ";path=/";
        }
    }
}

function updateESTTime() {
    let estTime = new Date().toLocaleString("en-US", {
        timeZone: "America/New_York",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: true // Ensures AM/PM format
    });
    document.getElementById("est-time").textContent = estTime + " EST";
}

updateESTTime();
setInterval(updateESTTime, 1000);

function updateServerConnection() {
    if (connectionScore == 2) {
        document.getElementById("serverConnection").querySelector("circle").setAttribute("fill", "#00ff11");
    } else if (connectionScore == 1) {
        document.getElementById("serverConnection").querySelector("circle").setAttribute("fill", "#fff700");
    } else {
        document.getElementById("serverConnection").querySelector("circle").setAttribute("fill", "#ff1100");
    }
}
updateServerConnection();
setInterval(updateServerConnection, 1000 * 30)

async function loadJson() {
    try {
        const response = await fetch('/data');
        return await response.json();
    } catch (error) {
        connectionScore -= 1;
        console.error('Error loading JSON:', error);
    }
}

let resultString = '';

if (data.activity) {
    if (data.activity.name) resultString += `Playing ${data.activity.name}`;
    if (data.activity.details) resultString += ` - ${data.activity.details}<br>`;
}

if (data.listening) {
    if (data.listening.songName) resultString += `Listening to "${data.listening.songName}" `;
    if (Array.isArray(data.listening.artist) && data.listening.artist.length > 0) {
        resultString += `by ${data.listening.artist.join(', ')} `;
    }
    if (data.listening.album) resultString += `on "${data.listening.album}"<br>`;
}

const dcStatus = document.getElementById('dcStatus');
if (dcStatus) {
    dcStatus.innerHTML = resultString;
}


let socket;
if (window.location.protocol === "https:") {
    socket = new WebSocket(`wss://${window.location.hostname}/ws`);
} else if (window.location.protocol === "http:") {
    console.log("Local or insecure connection detected. This server needs to be run over HTTPS to connect to it's socket.");
    connectionScore = 1;
} else {
    console.log("Unknown protocol: " + window.location.protocol + "\nAttempting to connect to WSS");
    socket = new WebSocket(`wss://${window.location.hostname}/ws`);
}

if (socket) {
    socket.onopen = () => {
        console.log('Connected to WebSocket');
    };

    socket.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            let statusData = data; // Update the JSON variable
            let resultString = '';

            if (statusData.activity) {
                if (statusData.activity.name) resultString += `Playing ${statusData.activity.name}`;
                if (statusData.activity.details) resultString += ` - ${statusData.activity.details}<br>`;
            }

            if (statusData.listening) {
                if (statusData.listening.songName) resultString += `Listening to "${statusData.listening.songName}" `;
                if (Array.isArray(statusData.listening.artist) && statusData.listening.artist.length > 0) {
                    resultString += `by: ${statusData.listening.artist.join(', ')} `;
                }
                if (statusData.listening.album) resultString += `on "${statusData.listening.album}"<br>`;
            }

            const dcStatus = document.getElementById('dcStatus');
            if (dcStatus) {
                dcStatus.innerHTML = resultString;
            }

            if (data.Spotify["@attr"] != null) {
                if (data.Spotify["@attr"].nowplaying == "true") {
                    const recordImage = document.getElementById("recordImage");
                    recordImage.src = data.Spotify.image[2]["#text"];
                    document.getElementById("currentlyListening").textContent = condenseString(`Currently listening to ${data.Spotify.name} by ${data.Spotify.artist["#text"]}`, 50);
                    document.getElementById("corner-widget").style.visibility = "visible";
                }
            }
        } catch (error) {
            connectionScore -= 1;
            console.error('Error parsing JSON:', error);
        }
    };

    socket.onerror = (error) => {
        connectionScore -= 1;
        console.error('WebSocket error:', error);
    };

    socket.onclose = () => {
        connectionScore -= 1;
        console.log('WebSocket connection closed');
    };
}

async function condenseString(str, len) {
    if (str.length > len) {
        return str.slice(0, len) + '...'; // Takes first 32 characters and adds "..."
    }
    return str;
}

function msToDHM(ms) {
    const days = Math.floor(ms / (24 * 60 * 60 * 1000));
    ms %= (24 * 60 * 60 * 1000);

    const hours = Math.floor(ms / (60 * 60 * 1000));
    ms %= (60 * 60 * 1000);

    const minutes = Math.floor(ms / (60 * 1000));

    let result = '';
    if (days > 0) result += `${days} days, `;
    if (hours > 0 || days > 0) result += `${hours} hours, `;
    result += `${minutes} minutes`;

    return result;
}

let statsFMLastClicked = "fourWeek"
document.getElementById("fourWeek").style.borderColor = "green";

async function handleStatsFMChange(buttonClicked) {
    if (buttonClicked == statsFMLastClicked) {
        return;
    }
    else {
        if (buttonClicked == "sixMonth") {
            statsFMLastClicked = "sixMonth"
            document.getElementById("sixMonth").style.borderColor = "green";
            document.getElementById("fourWeek").style.borderColor = "";
            document.getElementById("thisWeek").style.borderColor = "";
            await statsFMUpdate("6months");
        } else if (buttonClicked == "fourWeek") {
            statsFMLastClicked = "fourWeek"
            document.getElementById("sixMonth").style.borderColor = "";
            document.getElementById("fourWeek").style.borderColor = "green";
            document.getElementById("thisWeek").style.borderColor = "";
            await statsFMUpdate("4week");
        } else if (buttonClicked == "thisWeek") {
            statsFMLastClicked = "thisWeek"
            document.getElementById("sixMonth").style.borderColor = "";
            document.getElementById("fourWeek").style.borderColor = "";
            document.getElementById("thisWeek").style.borderColor = "green";
            await statsFMUpdate("thisweek");
        }
    }
}

async function statsFMUpdate(period) {
    let container = document.getElementById("artist-container");
    container.innerHTML = '<h3>Artists</h3>';

    for (const item of data.statsFM[period].artists.items) {
        const rowDiv = document.createElement("div");
        rowDiv.style.display = "flex";
        rowDiv.style.alignItems = "flex-start";
        rowDiv.style.gap = "10px";
        rowDiv.style.marginBottom = "10px";

        const img = document.createElement("img");
        img.src = item.artist.image;
        img.alt = item.artist.name;
        img.height = 75;
        img.width = 75;
        img.style.borderRadius = "10px";

        const infoDiv = document.createElement("div");
        infoDiv.style.display = "flex";
        infoDiv.style.flexDirection = "column";
        infoDiv.style.justifyContent = "center";
        infoDiv.style.alignItems = "flex-start";
        infoDiv.style.height = "75px";

        const nameHeading = document.createElement("h3");
        nameHeading.textContent = await condenseString(item.artist.name, 35);
        nameHeading.style.margin = "0";
        nameHeading.style.textAlign = "left";

        const playedMsHeading = document.createElement("h3");
        playedMsHeading.textContent = await msToDHM(item.playedMs);
        playedMsHeading.style.margin = "0";
        playedMsHeading.style.textAlign = "left";

        infoDiv.appendChild(nameHeading);
        infoDiv.appendChild(playedMsHeading);
        rowDiv.appendChild(img);
        rowDiv.appendChild(infoDiv);
        container.appendChild(rowDiv);
    };

    container = document.getElementById("tracks-container");
    container.innerHTML = '<h3 style="padding-left: 55px">Tracks</h3>';

    let pos = 1;

    for (const item of data.statsFM[period].tracks.items) {
        const rowDiv = document.createElement("div");
        rowDiv.style.display = "flex";
        rowDiv.style.alignItems = "flex-start";
        rowDiv.style.gap = "10px";
        rowDiv.style.marginBottom = "10px";

        const posText = document.createElement("h1");
        posText.textContent = pos;
        posText.style.width = "45px";
        posText.style.textAlign = "center";
        posText.style.height = "75px";
        posText.style.justifyContent = "center";
        posText.style.display = "flex";
        posText.style.alignItems = "center";

        if (pos == 1) {
            posText.style.color = "gold";
        } else if (pos == 2) {
            posText.style.color = "DimGray";
        } else if (pos == 3) {
            posText.style.color = "SaddleBrown";
        }

        const img = document.createElement("img");
        img.src = item.track.albums[0].image;
        img.alt = item.track.albums[0].name;
        img.height = 75;
        img.width = 75;
        img.style.borderRadius = "10px";

        const infoDiv = document.createElement("div");
        infoDiv.style.display = "flex";
        infoDiv.style.flexDirection = "column";
        infoDiv.style.justifyContent = "center";
        infoDiv.style.alignItems = "flex-start";
        infoDiv.style.height = "75px";

        const nameHeading = document.createElement("h3");
        nameHeading.textContent = await condenseString(item.track.name, 35);
        nameHeading.style.margin = "0";
        nameHeading.style.textAlign = "left";

        const authorHeading = document.createElement("h3");
        authorHeading.textContent = await condenseString((item.track.artists.map(x => ` ${x.name}`)).join(", "), 35);
        authorHeading.style.margin = "0";
        authorHeading.style.textAlign = "left";

        const playedMsHeading = document.createElement("h3");
        playedMsHeading.textContent = await msToDHM(item.playedMs);
        playedMsHeading.style.margin = "0";
        playedMsHeading.style.textAlign = "left";

        infoDiv.appendChild(nameHeading);
        infoDiv.appendChild(authorHeading);
        infoDiv.appendChild(playedMsHeading);
        rowDiv.appendChild(posText);
        rowDiv.appendChild(img);
        rowDiv.appendChild(infoDiv);
        container.appendChild(rowDiv);

        pos += 1;
    };

    container = document.getElementById("album-container");
    container.innerHTML = '<h3>Albums</h3>';

    for (const item of data.statsFM[period].albums.items) {
        const rowDiv = document.createElement("div");
        rowDiv.style.display = "flex";
        rowDiv.style.alignItems = "flex-start";
        rowDiv.style.gap = "10px";
        rowDiv.style.marginBottom = "10px";

        const img = document.createElement("img");
        img.src = item.album.image;
        img.alt = item.album.name;
        img.height = 75;
        img.width = 75;
        img.style.borderRadius = "10px";

        const infoDiv = document.createElement("div");
        infoDiv.style.display = "flex";
        infoDiv.style.flexDirection = "column";
        infoDiv.style.justifyContent = "center";
        infoDiv.style.alignItems = "flex-start";
        infoDiv.style.height = "75px";

        const nameHeading = document.createElement("h3");
        nameHeading.textContent = await condenseString(item.album.name, 35);
        nameHeading.style.margin = "0";
        nameHeading.style.textAlign = "left";

        const authorHeading = document.createElement("h3");
        authorHeading.textContent = await condenseString((item.album.artists.map(x => ` ${x.name}`)).join(", "), 35);
        authorHeading.style.margin = "0";
        authorHeading.style.textAlign = "left";

        const playedMsHeading = document.createElement("h3");
        playedMsHeading.textContent = await msToDHM(item.playedMs);
        playedMsHeading.style.margin = "0";
        playedMsHeading.style.textAlign = "left";

        infoDiv.appendChild(nameHeading);
        infoDiv.appendChild(authorHeading);
        infoDiv.appendChild(playedMsHeading);
        rowDiv.appendChild(img);
        rowDiv.appendChild(infoDiv);
        container.appendChild(rowDiv);
    };
}


await statsFMUpdate("4week");
document.getElementById("fourWeek").addEventListener('click', () => handleStatsFMChange('fourWeek'));
document.getElementById("thisWeek").addEventListener('click', () => handleStatsFMChange('thisWeek'));
document.getElementById("sixMonth").addEventListener('click', () => handleStatsFMChange('sixMonth'));


const monkeyType = document.getElementById('monkeyType');
if (monkeyType) {
    monkeyType.textContent = Math.round(data["monkeyType"]["typingStats"]["timeTyping"] / 60) + ' minutes doing typing tests';
}

// formula for green-red color change: y=-0.0001235x^{3}+0.05188x^{2}-1.354x-0.2005
let green = 255;
let val = data["RAMInfo"]["RAM Usage"];
if (val > 50) {
    green = 200 - (val - 50);
}
let red = -0.0001235 * (val * val * val) + 0.05188 * (val * val) - 1.354 * val - 0.2005;
if (red < 0) { red = 0; } document.getElementById("ramIcon").querySelectorAll(".cls-1").forEach(element => {
    element.setAttribute("stroke", `rgb(${red}, ${green}, ${0})`);
    element.setAttribute("fill", null);
});

document.getElementById('ramText').textContent = (data["RAMInfo"]["Used RAM"] / 1024).toFixed(2) + " / " + (data["RAMInfo"]["Total RAM"] / 1024).toFixed(2) + `GB (${data["RAMInfo"]["RAM Usage"]}%)`


green = 255;
val = data["CPUInfo"]["CPU Usage"];
if (val > 50) {
    green = 200 - (val - 50);
}
red = -0.0001235 * (val * val * val) + 0.05188 * (val * val) - 1.354 * val - 0.2005;
if (red < 0) { red = 0; } const cpuIcon = document.getElementById("CPU"); if (cpuIcon) {
    cpuIcon.querySelectorAll("path").forEach(element => {
        element.setAttribute("fill", `rgb(${red}, ${green}, ${0})`);
        element.setAttribute("stroke", `rgb(${red}, ${green}, ${0})`);
    });
}

document.getElementById('CPUText').textContent = `${data["CPUInfo"]["CPU Cores"]}-core @${data["CPUInfo"]["CPU Frequency"]} (${data["CPUInfo"]["CPU Usage"]}%)`


let totalSpace = 0;
let usedSpace = 0;

data["storageDrives"].forEach(drive => {
    totalSpace += drive.total;
    usedSpace += drive.used;
});

val = (usedSpace / totalSpace) * 100;
val = Math.round(val * 100) / 100;

green = 255;
if (val > 50) {
    green = 200 - (val - 50);
}
red = -0.0001235 * (val * val * val) + 0.05188 * (val * val) - 1.354 * val - 0.2005;
if (red < 0) { red = 0; } const storageIcon = document.getElementById("storage"); if (storageIcon) {
    storageIcon.querySelectorAll("path").forEach(element => {
        element.setAttribute("fill", `rgb(${red}, ${green}, ${0})`);
        element.setAttribute("stroke", `rgb(${red}, ${green}, ${0})`);
    });
}

document.getElementById('storageText').textContent = `${usedSpace.toFixed(2)}GB /
                    ${totalSpace.toFixed(2)}GB (${val}%)`

try {
    if ((data["wifiSpeed"]["down"] < 200) || (data["wifiSpeed"]["up"]
        < 100)) { red = 255; green = 97; } else if ((data["wifiSpeed"]["down"] < 100) ||
            (data["wifiSpeed"]["up"] < 50)) { red = 255; green = 0; } else {
        red = 79; green = 255;
    } const wifiIcon = document.getElementById("wifi"); if (wifiIcon) {
        wifiIcon.querySelectorAll("path").forEach(element => {
            element.setAttribute("fill", `rgb(${red}, ${green}, ${0})`);
            element.setAttribute("stroke", `rgb(${red}, ${green}, ${0})`);
        });

        document.getElementById('wifiText').textContent = `${(data["wifiSpeed"]["down"]).toFixed(2)}Mbps down / ${(data["wifiSpeed"]["up"]).toFixed(2)}Mbps up`
    }
}
catch (error) {
    const wifiIcon = document.getElementById("wifi"); if (wifiIcon) {
        wifiIcon.querySelectorAll("path").forEach(element => {
            element.setAttribute("fill", `rgb(255, 0, 0)`);
            element.setAttribute("stroke", `rgb(255, 0, 0)`);
        });
    }

    document.getElementById('wifiText').innerHTML = `Couldn't fetch wifi speed...<br>geez I hope it's working`;
}


const languageColors = {
    "JavaScript": "#f1e05a",
    "Python": "#3572A5",
    "Java": "#b07219",
    "C++": "#f34b7d",
    "C#": "#178600",
    "TypeScript": "#2b7489",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "Go": "#00ADD8",
    "Ruby": "#701516",
    "PHP": "#4F5D95",
    "Shell": "#89e051",
    "Rust": "#dea584",
    "Kotlin": "#A97BFF",
    "Swift": "#ffac45",
    "Dart": "#00B4AB",
    "Other": "#cccccc"
};

function parseRepoUrl(url) {
    try {
        const parts = new URL(url).pathname.split('/');
        return {
            owner: parts[1],
            repo: parts[2]
        };
    } catch (e) {
        return null;
    }
}

async function loadRepo(input) {
    const repoInfo = parseRepoUrl(input);
    const container = document.getElementById('previewContainer');
    container.innerHTML = '';

    if (!repoInfo) {
        container.innerHTML = "<p style='color: red;'>Invalid GitHub URL.</p>";
        return;
    }

    const { owner, repo } = repoInfo;

    try {
        const [repoData, langData] = await Promise.all([
            fetch(`https://api.github.com/repos/${owner}/${repo}`).then(res => res.json()),
            fetch(`https://api.github.com/repos/${owner}/${repo}/languages`).then(res => res.json())
        ]);

        const totalBytes = Object.values(langData).reduce((a, b) => a + b, 0);
        const languageBar = Object.entries(langData).map(([lang, bytes]) => {
            const color = languageColors[lang] || languageColors["Other"];
            const percent = (bytes / totalBytes) * 100;
            return `<div style="width: ${percent}%; background-color: ${color};"></div>`;
        }).join('');

        const legend = Object.entries(langData).map(([lang, bytes]) => {
            const color = languageColors[lang] || languageColors["Other"];
            return `<div class="legend-item"><span class="legend-color" style="background-color:${color}"></span>${lang}</div>`;
        }).join('');

        container.innerHTML += `
          <div class="preview">
            <a class="repo-name" href="${repoData.html_url}" target="_blank">${repoData.full_name}</a>
            <div class="description" style="max-width: 400px;">${repoData.description || ''}</div>
            <div class="language-bar">${languageBar}</div>
            <div class="language-legend">${legend}</div>
          </div>
        `;

    } catch (err) {
        container.innerHTML = "<p style='color: red;'>Failed to fetch repository data.</p>";
        console.error(err);
    }
}

// define repos to be loaded
loadRepo("https://www.github.com/cosmaticdev/cosmatic.dev");
loadRepo("https://www.github.com/cosmaticdev/pld-embeds");
loadRepo("https://github.com/cosmaticdev/MedalLocalBackup");