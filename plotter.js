
const btnSubmit = document.getElementById("btnSubmit");
const btnAdd = document.getElementById("btnAdd");
const string0 = document.getElementById("out0");

// Key for saving comments in localStorage
const COMMENTS_KEY = "tab1_comments";

// Utility: get comments object from localStorage
function getSavedComments() {
    try {
        return JSON.parse(localStorage.getItem(COMMENTS_KEY) || "{}");
    } catch (e) {
        return {};
    }
}

// Utility: save comments object to localStorage
function setSavedComments(obj) {
    localStorage.setItem(COMMENTS_KEY, JSON.stringify(obj));
}

function generateTables() {
    const vystupek = localStorage.getItem("vstup");
    string0.value = vystupek;

    const string2 = string0.value;

    function transformToArray(input) {
        const tokens = input.trim().split(/\s+/);
        const result = [];
        for (let i = 0; i < tokens.length; i += 2) {
            result.push(tokens[i]);
            if (tokens[i + 1] !== undefined) {
                result.push(tokens[i + 1]);
            }
            result.push(""); // Insert empty string after each pair
        }
        return result;
    }

    const array0 = transformToArray(string2);

    function removeLettersIfConditionMet(inputString) {
        if ((inputString.includes('6250') || inputString.includes('6240')) && !inputString.includes('m')) {
            return inputString.replace(/[a-zA-Z]/g, '');
        }
        return inputString;
    }

    const array1 = array0.map(removeLettersIfConditionMet);
    const filteredArray = array1.filter(item => item.trim() !== "");

    function insertBetweenAdjacentStrings(array, letterList1, letterList2) {
        for (let i = 0; i < array.length - 1; i++) {
            if (letterList1.includes(array[i][0]) && letterList2.includes(array[i + 1][0])) {
                array.splice(i + 1, 0, "M101?!?"); // Insert "M101?!?" between the adjacent strings
                i++; // Skip the next index since we've inserted a new string
            }
        }
        return array;
    }

    const originalArray = [...filteredArray];
    const letterList1 = ["625"];
    const letterList2 = ["P", "V"];
    const result = insertBetweenAdjacentStrings(originalArray, letterList1, letterList2);

    function extractAndCleanSubstrings(array) {
        return array
            .filter(str => str.includes("6240") || str.includes("6250"))
            .map(str => str.replace(/[,.-]/g, ''));
    }

    const result2 = extractAndCleanSubstrings(result);
    const filtered = originalArray.filter(value => typeof value === "string" && (value.startsWith("M10") || value.startsWith("M30")));

    // Generate HTML for tab2
    let html = "<table id='tab2'>";
    for (let i = 0; i < result2.length; i++) {
        html += `<tr>
                    <td><i class='fa-solid fa-rectangle-xmark' onclick='removeRow(this)'></i></td>
                    <td>${result2[i]}</td>
                  </tr>`;
    }
    html += "</table>";
    document.getElementById("outputs").innerHTML = html;

    let data = [
        ["M300015", "Pěna 23/10"],["M300013", "Pěna 23/20"],["M300014", "Pěna 23/30"],["M300010", "Pěna 23/40"],["M300011", "Pěna 23/50"],["M300012", "Pěna 24/60"],["M300057", "Pěna 28/70"],["M300066", "Pěna 28/10"],["M300024", "Pěna 35/20"],["M300025", "Pěna 35/50"],["M300086", "Pěna 65/40"],["M300114", "Pěna 24/25"],["M300022", "Pěna 35/30"],["M102780", "2.31 BE"],["M103226", "2.35 BE"],["M105367", "2.41 BE"],["M101447", "2.31 BE"],["M104281", "3.90 AAC"],["M103469", "3.91 AAC"],["M104730", "3.92 AAC"],["M102476", "3.95 AAC"],["M104188", "3.96 AAC"],["M200009", "CP 2mm"],["M200043", "CP 2,5mm"],["M200034", "CP 3mm"],["M200001", "CP 3,5mm"],["M200004", "CP 5mm"],["M200014", "CP 5mm"],["M102112", "2.03 BC"],["M101446", "2.30 BC"],["M106269", "2.30 BC"],["M100197", "2.31 BC"],["M100446", "2.31 BC"],["M102338", "2.31 BC"],["M103231", "2.35 BC N2"],["M101765", "2.40 BC N2"],["M101538", "2.41 BC"],["M101455", "2.50 BC N2"],["M101539", "2.51 BC"],["M103225", "2.60 BC N2"],["M103223", "2.70 BC N2"],["M101448", "2.71 BC"],["M102036", "2.71 BC"],["M101989", "2.90 BC"],["M101990", "2.91 BC"],["M101449", "2.91 BC"],["M103035", "2.91 AC"],["M103945", "2.92 AC"],["M101588", "1.20 B"],["M103229", "1.25 B"],["M100187", "1.30 B"],["M101454", "1.30 B"],["M100062", "1,37 B"],["M102964", "1.31 B"],["M102425", "1.41 B"],["M103232", "1.20 C"],["M101764", "1.30 C"],["M101444", "1.31 C"],["M102086", "1.31 C"],["M100198", "1.41 C"],["M100012", "1.21 E"],["M102364", "1.25 E"]
    ];
    let dataMap = {};
    for (let i = 0; i < data.length; i++) {
        dataMap[data[i][0]] = data[i][1];
    }

    // Get saved comments for editable cells
    const savedComments = getSavedComments();

    let html2 = "<table id='tab1'>";
    for (let i = 0; i < filtered.length; i++) {
        let cellValue = filtered[i];
        html2 += "<tr>";
        html2 += `<td>${cellValue}</td>`;
        // Add extra cell if value matches any in dataMap
        if (dataMap[cellValue]) {
            html2 += `<td>${dataMap[cellValue]}</td>`;
            // Always render editable cell for every row
            const commentVal = savedComments[cellValue + "_" + i] || "";
            html2 += `<td contenteditable="true" class="comment" data-key="${cellValue}_${i}">${commentVal}</td>`;
        } else if (cellValue === "M10000") {
            html2 += "<td>2.2C</td>";
            const commentVal = savedComments[cellValue + "_" + i] || "";
            html2 += `<td contenteditable="true" class="comment" data-key="${cellValue}_${i}">${commentVal}</td>`;
        } else if (cellValue === "M1111") {
            html2 += "<td>1.41B</td>";
            const commentVal = savedComments[cellValue + "_" + i] || "";
            html2 += `<td contenteditable="true" class="comment" data-key="${cellValue}_${i}">${commentVal}</td>`;
        }
        html2 += "</tr>";
    }
    html2 += "</table>";
    document.getElementById("outputs2").innerHTML = html2;

    // Add event listeners to all comment cells
    document.querySelectorAll("#tab1 td.comment").forEach(cell => {
        cell.addEventListener("input", function () {
            const key = cell.getAttribute("data-key");
            const value = cell.textContent.trim();
            const comments = getSavedComments();
            if (value) {
                comments[key] = value;
            } else {
                delete comments[key];
            }
            setSavedComments(comments);
        });
    });

    removeDuplicates(result2);
    replaceTableCellText();
}




// Function to find duplicates and remove them
function removeDuplicates(result2) {
    const seen = {};
    const duplicatesIndices = [];

    for (let i = 0; i < result2.length; i++) {
        const item = result2[i];
        if (seen[item]) {
            duplicatesIndices.push(i); // Store index of duplicate
        } else {
            seen[item] = true; // Mark as seen
        }
    }

    // Now remove duplicates from both tables based on the found indices
    r1(duplicatesIndices);
    r2(duplicatesIndices);
    
}
// Function to search through table cells, replace text, and apply styles
// Only the cell directly left of the first changed cell is replaced, vertical borders are removed from the second changed cell, and "M101?!?" is replaced with "Neuvedeno" without affecting formatting
function replaceTableCellText() {
    // Get all the tables in the document
    const tables = document.querySelectorAll('table');

    let firstChangedCellStyled = false; // Flag to track if the first changed cell has been styled
    let secondChangedCellHandled = false; // Flag to track if the second changed cell has been handled

    // Loop through each table
    tables.forEach((table) => {
        // Get all rows in the table
        const rows = table.querySelectorAll('tr');

        // Loop through each row
        rows.forEach((row) => {
            const cells = row.querySelectorAll('td'); // Get all cells in the row

            cells.forEach((cell, index) => {
                let textChanged = false; // Track if the text in the cell is changed

         

                // Replace "M101???" with "\u2002"
                if (cell.textContent.includes("M101???")) {
                    cell.textContent = cell.textContent.replace("M101???", "\u2002");
                    textChanged = true;
                }

                // Replace "M101?!?" with "Neuvedeno" (without affecting formatting)
                if (cell.textContent.includes("M101?!?")) {
                    cell.textContent = cell.textContent.replace("M101?!?", "No data");
                }

        
            });
        });
    });
}


















// Function to remove the row containing the clicked icon from both tables
function removeRow(icon) {
    const row = icon.closest('tr'); // Get the closest row to the clicked icon
    const rowIndex = row.rowIndex; // Get the index of the row

    const table1 = document.getElementById('tab1');
    const table2 = document.getElementById('tab2');
    
    const tbody1 = table1.tBodies[0];
    const tbody2 = table2.tBodies[0];

    // Remove row from tab1
    if (rowIndex < tbody1.rows.length) {
        tbody1.deleteRow(rowIndex);
    }

    // Remove row from tab2
    if (rowIndex < tbody2.rows.length) {
        tbody2.deleteRow(rowIndex);
    }

   
    
}

// Functions to remove rows based on indices
function r1(indices) {
    const table = document.getElementById('tab2');
    const tbody = table.tBodies[0];
    indices.sort((a, b) => b - a); // Sort descending for safe removal

    for (const index of indices) {
        if (index >= 0 && index < tbody.rows.length) {
            tbody.deleteRow(index);
        }
    }
}

function r2(indices) {
    const table = document.getElementById('tab1');
    const tbody = table.tBodies[0];
    indices.sort((a, b) => b - a); // Sort descending for safe removal

    for (const index of indices) {
        if (index >= 0 && index < tbody.rows.length) {
            tbody.deleteRow(index);
        }
    }
}

// Function to format the input string before saving
function formatClipboardText(inputString) {
  const lines = inputString.trim().split(/\r?\n/);
  const groupedLines = [];
  let currentGroup = [];

  // Group lines based on empty lines
  lines.forEach((line) => {
    if (line.trim()) {
      // Add non-empty lines to the current group
      currentGroup.push(line.trim());
    } else {
      if (currentGroup.length > 0) {
        // Join the current group with spaces and add to groupedLines
        groupedLines.push(currentGroup.join(" "));
        currentGroup = [];
      }
    }
  });

  // Add the last group if it exists
  if (currentGroup.length > 0) {
    groupedLines.push(currentGroup.join(" "));
  }

  // Join all groups into a single string separated by double spaces
  return groupedLines.join("  ");
}

// Set up event listener for the submit button
btnSubmit.onclick = async function () {
  // Function to read clipboard, format the content, and save to localStorage
  async function saveClipboardText() {
    try {
      const text = await navigator.clipboard.readText(); // Read clipboard content
      const formattedText = formatClipboardText(text); // Format the clipboard content
      localStorage.setItem('vstup', formattedText); // Save formatted value to localStorage
      console.log('Formatted clipboard value saved to localStorage:', formattedText);
    } catch (error) {
      console.error('Error reading clipboard:', error);
    }
  }

  // Call the clipboard save function
  await saveClipboardText();

  generateTables(); // Generate tables after setting the key
};















  

// Load tables on page load if there is a value in local storage
window.onload = function() {
    if (localStorage.getItem("vstup")) {
        generateTables();
    }

    // Highlight cells on click 
    let btns = document.querySelectorAll("tr td:not(:nth-child(1),:nth-child(3))");
    for (let i of btns) {
        i.addEventListener('click', function() {
            this.style.background = this.style.background === "white" ? "yellow" : "white";
        });
    }


    

};

// Highlight duplicates in the 2nd table cell with unique colors
function colour() {
    const table = document.querySelectorAll('table')[1];
    const rows = table.getElementsByTagName('tr');
    const valueCount = {};
    const colors = ['#ff9999', '#99ff99', '#9999ff', '#ffff99', '#ffcc99','#99f6ff','#e100fa','#0081fa', '#A3E3A3','#CCCC00','#C4BDD8','#7404DF','#FF5992']; // Array of unique colors

    // Count occurrences of each value in 2nd cell
    for (let i = 0; i < rows.length; i++) {
        const cells = rows[i].getElementsByTagName('td');
        if (cells.length > 1) {
            const value = cells[1].textContent.trim();
            valueCount[value] = (valueCount[value] || 0) + 1;
        }
    }

    // Highlight duplicates in the 2nd cell
    for (let i = 0; i < rows.length; i++) {
        const cells = rows[i].getElementsByTagName('td');
        if (cells.length > 1) {
            const value = cells[1].textContent.trim();
            if (valueCount[value] > 1) {
                const index = Object.keys(valueCount).indexOf(value);
                // Use a color from the colors array based on the index of the value
                cells[1].style.backgroundColor = colors[index % colors.length];
            } else {
                // Optional: clear background if not duplicate
                cells[1].style.backgroundColor = '';
            }
        }
    }
}