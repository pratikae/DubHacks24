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
    let imagesHtml = '';
    
    if (data.similar_images && data.similar_images.length > 0) {
        data.similar_images.forEach(img => {
            imagesHtml += `
                <div class="similar-image">
                    <img src="${img.url}" alt="${img.label}" onerror="this.onerror=null; this.src='/static/placeholder.jpg';" style="width:200px;height:auto;">
                    <p>${img.label}</p>
                </div>
            `;
        });
    } else {
        imagesHtml = '<p>No similar images found</p>';
    }

    resultDiv.innerHTML = `
        <h2>Analysis Results:</h2>
        <pre>${data.description}</pre>
        <h3>Similar Conditions:</h3>
        <div class="similar-images">
            ${imagesHtml}
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
