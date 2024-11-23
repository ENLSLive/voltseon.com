

const https = require('https');
const fs = require('fs');
const path = require('path');

// Function to generate numbers with leading zeros
function generatePaddedNumbers(start, end, width) {
    const numbers = [];
    for (let i = start; i <= end; i++) {
        numbers.push(i.toString().padStart(width, '0'));
    }
    return numbers;
}

// Function to download a file
function downloadFile(url, dest) {
    return new Promise((resolve, reject) => {
        const file = fs.createWriteStream(dest);
        https.get(url, (response) => {
            if (response.statusCode !== 200) {
                reject(`Failed to download file: ${url}. Status code: ${response.statusCode}`);
                return;
            }
            response.pipe(file);
            file.on('finish', () => {
                file.close(resolve);
            });
        }).on('error', (err) => {
            fs.unlink(dest, () => reject(err.message)); // Delete the file if an error occurs
        });
    });
}

// Main function to loop through and download GIFs
async function downloadGifs() {
    const numbers = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "-exclamation", "-question"]; // Generate numbers 000 to 100
    const outputDir = path.join(__dirname, 'gifs');
    fs.mkdirSync(outputDir, { recursive: true }); // Ensure the output directory exists

    for (const num of numbers) {
        const url = `https://www.pokencyclopedia.info/sprites/menu-icons/ico-a_old/ico-a_old_201-${num}.gif`; // Replace with your URL template
        const dest = path.join(outputDir, `201-${num}.gif`);

        try {
            console.log(`Downloading ${url}...`);
            await downloadFile(url, dest);
            console.log(`Saved to ${dest}`);
        } catch (error) {
            console.error(`Error downloading ${url}: ${error}`);
        }
    }
}

downloadGifs().then(() => {
    console.log('All downloads completed.');
}).catch((error) => {
    console.error('Error during downloads:', error);
});
