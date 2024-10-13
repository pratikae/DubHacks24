document.getElementById('uploadForm').addEventListener('submit', async function(event) {
    event.preventDefault(); // Prevent the form from submitting normally

    const imageInput = document.getElementById('imageInput');
    const ageInput = document.getElementById('ageInput').value;
    const sexInput = document.getElementById('sexInput').value;

    const formData = new FormData();
    formData.append('image', imageInput.files[0]);
    formData.append('age', ageInput);
    formData.append('sex', sexInput);

    try {
        const response = await fetch('http://localhost:5000/upload', { // Adjust the URL if needed
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        displayResult(result);
    } catch (error) {
        console.error('Error:', error);
    }
});

function displayResult(data) {
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = `<h2>Clinical Description</h2><p>${data.description}</p>`;
    if (data.images && data.images.length > 0) {
        resultDiv.innerHTML += `<h3>Similar Images:</h3>`;
        data.images.forEach(image => {
            resultDiv.innerHTML += `<img src="${image}" alt="Similar Condition" style="width:100px;height:auto;margin:5px;">`;
        });
    }
}

// script.js

document.getElementById('imageInput').addEventListener('change', function(event) {
    const file = event.target.files[0];
    const imageUrl = URL.createObjectURL(file); // Create a URL for the uploaded image
    const uploadedImage = document.getElementById('uploadedImage');
    
    uploadedImage.src = imageUrl; // Set the source of the image
    uploadedImage.style.display = 'block'; // Show the image
});
