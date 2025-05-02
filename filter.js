const inpKey = document.getElementById("inpKey");
const btnSubmit = document.getElementById("btnSubmit");
const string0 = document.getElementById("out0");

// Function to detect swipe gestures and handle them
function handleSwipeEvents() {
    let touchstartX = 0;
    let touchendX = 0;
    const table = document.getElementById('tab1');

    if (!table) return;
    
    const rows = table.getElementsByTagName('tr');

    for (let row of rows) {
        // Add touch event listeners to each table cell
        const cells = row.getElementsByTagName('td');
        for (let cell of cells) {
            cell.addEventListener('touchstart', function (event) {
                touchstartX = event.changedTouches[0].screenX;
            });

            cell.addEventListener('touchend', function (event) {
                touchendX = event.changedTouches[0].screenX;
                handleSwipe(cell);
            });
        }
    }

    function handleSwipe(cell) {
        if (touchendX < touchstartX - 50) {
            // Swipe Left: Remove the cell
            const row = cell.parentElement;
            row.removeChild(cell);

            // If the row becomes empty, remove the row itself
            if (row.children.length === 0) {
                row.parentElement.removeChild(row);
            }
        } else if (touchendX > touchstartX + 50) {
            // Swipe Right: Add a new cell
            const row = cell.parentElement;
            const newCell = row.insertCell(-1); // Append at the end
            newCell.textContent = 'New Cell';
            addSwipeListenersToCell(newCell);
        }
    }

    function addSwipeListenersToCell(cell) {
        // Ensure new cell also has swipe listeners
        cell.addEventListener('touchstart', function (event) {
            touchstartX = event.changedTouches[0].screenX;
        });

        cell.addEventListener('touchend', function (event) {
            touchendX = event.changedTouches[0].screenX;
            handleSwipe(cell);
        });
    }
}






// Function to generate tables
function generateTables() {
    const vystupek = localStorage.getItem("vstup");
    string0.value = vystupek;

    const string1 = string0.value;

    function replaceLetters(inputString) {
        return inputString
            .replace(/d/gi, '')
            .replace(/l/gi, '')
            .replace(/á/gi, '')
            .replace(/o/gi, '0')
            .replace(/i/gi, '1')
            .replace(/a/gi, '4');
    }

    const string2 = replaceLetters(string1);
    let array0 = string2.split(' ');

    function removeLettersIfConditionMet(inputString) {
        if ((inputString.includes('6250') || inputString.includes('6240')) && !inputString.includes('m')) {
            return inputString.replace(/[a-zA-Z]/g, '');
        }
        return inputString;
    }

    const array1 = array0.map(removeLettersIfConditionMet);
    const filteredArray = array1.filter(item => item.trim() !== "");

    function removeAdjacentStringsStartingWith(array, letterList1, letterList2) {
        for (let i = 0; i < array.length - 1; i++) {
            if (letterList1.includes(array[i][0]) && letterList2.includes(array[i + 1][0])) {
                array.splice(i, 2);
                i--;
            }
        }
        return array;
    }

    const originalArray = [...filteredArray];
    const letterList1 = ["6"];
    const letterList2 = ["P", "V"];
    const result = removeAdjacentStringsStartingWith(originalArray, letterList1, letterList2);

    function extractAndCleanSubstrings(array) {
        return array
            .filter(str => str.includes("6240") || str.includes("6250"))
            .map(str => str.replace(/[,.-]/g, ''));
    }

    const result2 = extractAndCleanSubstrings(result);
    const filtered = originalArray.filter(value => typeof value === "string" && value.startsWith("M10"));
    
    // Generate HTML for tables
    let html = "<table id='tab2'>";
    for (let i = 0; i < result2.length; i++) {
        html += `<tr>
                    <td><i class='fa-solid fa-rectangle-xmark' onclick='removeRow(this)'></i></td>
                    <td>${result2[i]}</td>
                  </tr>`;
    }
    html += "</table>";
    document.getElementById("outputs").innerHTML = html;

    let html2 = "<table id='tab1'>";
    for (let i = 0; i < filtered.length; i++) {
        html2 += `<tr><td>${filtered[i]}</td></tr>`;
    }
    html2 += "</table>";
    document.getElementById("outputs2").innerHTML = html2;

    // Call function to find and remove duplicates
    removeDuplicates(result2);
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

// Set up event listener for the submit button
btnSubmit.onclick = function() {
    const key = inpKey.value;
    if (key) {
        localStorage.setItem("vstup", key);
        generateTables(); // Generate tables after setting the key
    }
};

// Load tables on page load if there is a value in local storage
window.onload = function() {
    if (localStorage.getItem("vstup")) {
        generateTables();
    }

    // Highlight cells on click 
    let btns = document.querySelectorAll("tr td:not(:nth-child(1))");
    for (let i of btns) {
        i.addEventListener('click', function() {
            this.style.background = this.style.background === "white" ? "yellow" : "white";
        });
    }

// Add swipe gesture handling
handleSwipeEvents();


};

// Highlight duplicates with unique colors
function colour() {
    const table = document.querySelectorAll('table')[1];
    const rows = table.getElementsByTagName('tr');
    const valueCount = {};
    const colors = ['#ff9999', '#99ff99', '#9999ff', '#ffff99', '#ffcc99','#99f6ff','#e100fa','#0081fa', '#A3E3A3','#CCCC00','#C4BDD8',' #7404DF',' #FF5992']; // Array of unique colors
    
    // Count occurrences of each value
    for (let i = 0; i < rows.length; i++) {
        const value = rows[i].textContent.trim();
        valueCount[value] = (valueCount[value] || 0) + 1;
    }
    
    // Highlight duplicates with unique colors
    for (let i = 0; i < rows.length; i++) {
        const value = rows[i].textContent.trim();
        if (valueCount[value] > 1) {
            const index = Object.keys(valueCount).indexOf(value);
            // Use a color from the colors array based on the index of the value
            rows[i].style.backgroundColor = colors[index % colors.length];
        }
    }
}
document.getElementById('translateButton').addEventListener('click', function() {
    // Open Google Translate in a new tab
    window.open('https://translate.google.com', '_blank');
});
