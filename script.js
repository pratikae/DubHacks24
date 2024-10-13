document.getElementById('uploadForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const formData = new FormData(this);

    try {
        const response = await fetch('/upload', {
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
    resultDiv.innerHTML = `
        <h2>Clinical Analysis Results:</h2>
        <pre>${data.description}</pre>
        <h3>Similar Conditions:</h3>
        <div class="similar-images">
            ${data.similar_images.map(img => `
                <div class="similar-image">
                    <img src="${img.url}" alt="${img.label}" style="width:200px;height:auto;">
                    <p>${img.label}</p>
                </div>
            `).join('')}
        </div>
    `;
}

document.getElementById('imageInput').addEventListener('change', function(event) {
    const file = event.target.files[0];
    const imageUrl = URL.createObjectURL(file);
    const uploadedImage = document.getElementById('uploadedImage');
    
    uploadedImage.src = imageUrl;
    uploadedImage.style.display = 'block';
});
