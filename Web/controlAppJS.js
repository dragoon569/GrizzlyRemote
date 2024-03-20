document.addEventListener("DOMContentLoaded", function () {
    // Add event listener to volume slider
    var volumeSlider = document.getElementById("volume-slider");
    var volumePercentage = document.getElementById("volume-percentage");

    function updateVolumePercentage() {
        var volumeLevel = volumeSlider.value; // Get the current volume level from the slider
        volumePercentage.textContent = volumeLevel + '%';
    }

    volumeSlider.addEventListener("input", function () {
        updateVolumePercentage();
        sendCommand("adjust_volume_" + this.value); // Send the volume level to the server
    });

    // Add event listener to mute/unmute button
    var muteUnmuteBtn = document.getElementById("mute-unmute-btn");
    muteUnmuteBtn.addEventListener("click", function () {
        var currentState = muteUnmuteBtn.textContent.toLowerCase();
        var command = currentState === "mute" ? "mute_volume" : "unmute_volume";
        sendCommand(command);
    });

document.getElementById('mute-unmute-btn').addEventListener('click', function() {
    var isMuted = this.classList.contains('unmuted');
    this.setAttribute('aria-label', isMuted ? 'Unmute' : 'Mute');
});


    // Add event listeners to volume up/down 5% buttons
    document.getElementById("volume-down-5-btn").addEventListener("click", function () {
        volumeSlider.value -= 5;
        updateVolumePercentage();
        sendCommand("volume_down_5_percent");
    });

    document.getElementById("volume-up-5-btn").addEventListener("click", function () {
        volumeSlider.value = parseInt(volumeSlider.value) + 5;
        updateVolumePercentage();
        sendCommand("volume_up_5_percent");
    });

    // Add event listeners to buttons
    document.getElementById("screen-off-btn").addEventListener("click", function () {
        console.log("Screen off button clicked");
        sendCommand("turn_screen_off");
    });

    document.getElementById("shutdown-btn").addEventListener("click", function () {
        console.log("Shutdown button clicked");
        sendCommand("shutdown_computer");
    });

    document.getElementById('mute-unmute-btn').addEventListener('click', function() {
        this.classList.toggle('unmuted');
    });

    document.addEventListener('DOMContentLoaded', function() {
        var muteUnmuteBtn = document.getElementById('mute-unmute-btn');
        var isMuted = false; // Keep track of mute state
        
        muteUnmuteBtn.addEventListener('click', function() {
            if (isMuted) {
                // Unmute logic
                // Add your unmute logic here
                isMuted = false;
            } else {
                // Mute logic
                // Add your mute logic here
                isMuted = true;
            }
        });
    });
    
    // Function to send commands
    function sendCommand(command) {
        fetch('/command', {
            method: 'POST',
            headers: {
                'Content-Type': 'text/plain'
            },
            body: command
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(data => {
            console.log(data);
            // Update mute/unmute button text if needed
            if (command === "mute_volume" || command === "unmute_volume") {
                var newState = command === "mute_volume" ? "Unmute" : "Mute";
                muteUnmuteBtn.textContent = newState;
            }
        })
        .catch(error => {
            console.error('There was an error!', error);
        });
    }
    
    // Call discoverServices function when the page loads
    discoverServices();

    // Call updateVolumePercentage initially to set the initial volume percentage
    updateVolumePercentage();

    // Fetch the current master volume level from the server
    fetch('/get_master_volume')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(data => {
            // Set the slider and percentage display to the fetched volume level
            volumeSlider.value = parseInt(data);
            updateVolumePercentage();
        })
        .catch(error => {
            console.error('There was an error!', error);
        });

    // Toggle dark mode
    var body = document.body;
    var darkModeBtn = document.getElementById('dark-mode-btn');


    // Function to fetch and update Grizzly remote information
    function updateGrizzlyInfo() {
        fetch("/fetch_grizzly_info") // Fetch the Grizzly remote information from the server
        .then(response => response.json())
        .then(data => {
            // Update the HTML elements with the fetched information
            document.getElementById("bear-name").textContent = data.bear_name;
            document.getElementById("device-name").textContent = data.device_name;
            document.getElementById("device-type").textContent = data.device_type;
            document.getElementById("local-ip").textContent = data.local_ip;
        })
        .catch(error => {
            console.error("Error fetching Grizzly remote information:", error);
        });
    }

    // Call updateGrizzlyInfo function when the page loads
    updateGrizzlyInfo();

});
