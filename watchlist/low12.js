// scraper.js
import puppeteer from "puppeteer";

async function getROICFromYahoo(ticker) {
  const url = `https://finance.yahoo.com/quote/${ticker}/`;

  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(url, { waitUntil: "domcontentloaded" });

  const roicText = await page.evaluate(() => {
    const td = Array.from(document.querySelectorAll("td"))
      .find(el => el.textContent.includes("Return on Invested Capital"));
    if (!td) return null;
    const nextTd = td.nextElementSibling;
    return nextTd ? nextTd.textContent.trim() : null;
  });

  await browser.close();
  return roicText;
}

(async () => {
  console.log(await getROICFromYahoo("AAPL"));
})();
