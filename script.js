const imageInput = document.getElementById('imageInput');
const outputDiv = document.getElementById('output');

imageInput.addEventListener('change', (e) => {
    const file = imageInput.files[0];
    const reader = new FileReader();
    reader.onload = () => {
        const imageData = reader.result;
        const image = new Image();
        image.src = imageData;

        image.onload = () => {
            const imageData = getBase64Image(image);
            Tesseract.recognize(imageData)
                .then((result) => {
                    outputDiv.innerText = result.text;
                })
                .catch((err) => {
                    console.error(err);
                });
        };
    };
    reader.readAsDataURL(file);
});

function getBase64Image(img) {
    const canvas = document.createElement('canvas');
    canvas.width = img.width;
    canvas.height = img.height;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(img, 0, 0);
    const dataURL = canvas.toDataURL('image/png');
    return dataURL.replace(/^data:image\/(png|jpg);base64,/, '');
}