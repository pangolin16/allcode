const axios = require('axios');
const cheerio = require('cheerio');
const express = require('express');
const cors = require('cors');

const app = express();
const PORT = 3000; // Valid port number

app.use(cors()); // Enable CORS for frontend requests

// Function to scrape data with Cheerio
async function scrapeEarningsDate(url) {
  try {
    console.log(`Fetching URL: ${url}`);
    const { data: html } = await axios.get(url); // Fetch the HTML from the webpage
    const $ = cheerio.load(html); // Load the HTML into Cheerio

    console.log('Extracting earnings date...');
    const element = $('#next-events-card > div:nth-child(3) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1)'); // Update this selector
    const latestEarningsDate = element.text().trim();

    if (!latestEarningsDate) {
      throw new Error('Earnings date element not found on page');
    }

    return latestEarningsDate;
  } catch (error) {
    console.error(`Scraping failed: ${error.message}`);
    throw error;
  }
}

// Endpoint to scrape data
app.get('/scrape-earnings-date', async (req, res) => {
  try {
    const urlToScrape = 'https://www.marketscreener.com/quote/stock/TELEPERFORMANCE-SE-4709/calendar/';
    const earningsDate = await scrapeEarningsDate(urlToScrape);

    res.json({ earningsDate });
  } catch (error) {
    console.error('Error during scraping:', error);
    res.status(500).json({ error: `Server error during scraping: ${error.message}` });
  }
});

// Start the Express server
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});