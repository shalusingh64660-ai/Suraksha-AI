let map;
let marker;
let countdownInterval;

function fakeSOS() {

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {

            const latitude = position.coords.latitude;
const longitude = position.coords.longitude;

showMap(latitude, longitude);

fetch("http://127.0.0.1:5000/sos", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
body: JSON.stringify({
    user: document.getElementById("userEmail").value,
    latitude: latitude,
    longitude: longitude
})
})
.then(response => response.json())
.then(data => {
    startCountdown();
});

        });
    }
}

function startCountdown() {

    let timeLeft = 10;
    const message = document.getElementById("sosMessage");

    message.innerText = `⏳ Escalating in ${timeLeft} seconds...`;

    countdownInterval = setInterval(() => {

        timeLeft--;

        message.innerText = `⏳ Escalating in ${timeLeft} seconds...`;

        if (timeLeft <= 0) {
            clearInterval(countdownInterval);
            escalateEmergency();
        }

    }, 1000);
}

function cancelSOS() {
    clearInterval(countdownInterval);
    document.getElementById("sosMessage").innerText = "✅ SOS Cancelled Successfully.";
}

function escalateEmergency() {
    document.getElementById("sosMessage").innerText =
        "🚨 ESCALATION ACTIVATED! Authorities Notified (Demo)";
}
function showMap(lat, lng) {

    if (!map) {
        map = L.map('map').setView([lat, lng], 15);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
    } else {
        map.setView([lat, lng], 15);
    }

    if (marker) {
        map.removeLayer(marker);
    }

    marker = L.marker([lat, lng]).addTo(map)
        .bindPopup("🚨 Emergency Location")
        .openPopup();
}
function saveContact() {

    const name = document.getElementById("userEmail").value;
    const email = document.getElementById("contactEmail").value;

    fetch("http://127.0.0.1:5000/add_emergency_contact", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            name: name,
            email: email
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("contactMessage").innerText = data.message;
    });
}