// Fetch the latest earnings date from the backend
function fetchEarningsDate() {
  fetch('http://localhost:3000/scrape-earnings-date') // Ensure correct backend URL
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      if (data.earningsDate) {
        console.log('next event', data.earningsDate);
      } else {
        console.error('Error fetching earnings date:', data.error);
      }
    })
    .catch(error => {
      console.error('Error:', error.message);
      // Display error message in the UI (optional)
      const errorElement = document.getElementById('error-message');
      if (errorElement) {
        errorElement.textContent = `Failed to fetch earnings date: ${error.message}`;
      }
    });
}

// Call the function to fetch earnings date
fetchEarningsDate();