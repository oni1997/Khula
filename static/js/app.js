// script for landing buttons.
        // Add event listeners for the buttons
        document.getElementById('uploadButton').addEventListener('click', function() {
            alert("Redirecting to Upload Image Page...");
            // You can redirect to the upload page or implement a popup here.
            window.location.href = "/upload";
        });

        document.getElementById('analysisButton').addEventListener('click', function() {
            alert("Redirecting to Condition Analysis Page...");
            // You can redirect to the analysis page or implement a popup here.
            window.location.href = "/analysis";
        });