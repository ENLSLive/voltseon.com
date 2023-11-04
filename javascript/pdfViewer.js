const pdfContainer = document.getElementById('pdfContainer');

function displayPDF(pdfTitle, pdfPath) {
    const divider = document.createElement('div');
    divider.classList.add('line');

    const divider2 = document.createElement('div');
    divider2.classList.add('line');

    const pdfElement = document.createElement('div');
    pdfElement.classList.add('pdf-container');

    const title = document.createElement('h2');
    title.classList.add('pdf-title');
    title.textContent = pdfTitle;

    const embed = document.createElement('embed');
    embed.classList.add('pdf-embed');
    embed.setAttribute('src', pdfPath);

    pdfElement.appendChild(title);
    pdfElement.appendChild(divider);
    pdfElement.appendChild(embed);
    pdfContainer.appendChild(pdfElement);
    pdfContainer.appendChild(divider2);
}

// Parse query parameters from the URL
const urlParams = new URLSearchParams(window.location.search);
urlParams.forEach((value, key) => {
    if (key.startsWith('pdfTitle') && value && urlParams.has('pdfPath' + key.substr(8))) {
        const pdfPath = urlParams.get('pdfPath' + key.substr(8));
        displayPDF(value, pdfPath);
    }
});