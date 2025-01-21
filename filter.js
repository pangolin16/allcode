const inpKey = document.getElementById("inpKey");
const btnSubmit = document.getElementById("btnSubmit");
const string0 = document.getElementById("out0");

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
            if (this.style.background === "white") {
                this.style.background = "yellow";
            } else {
                this.style.background = "white";
            }
        });
    }

    // Find duplicates
    const findDuplicates = (result2) => {
        const seen = {};
        const duplicates = [];

        result2.forEach((item, index) => {
            if (seen[item]) {
                duplicates.push(index); // Store the index of the duplicate
            } else {
                seen[item] = true; // Mark the item as seen
            }
        });

        return duplicates;
    };

    const duplicates = findDuplicates(result2);
    // Store duplicate indices for removal
    const duplnew = duplicates.map(index => index);
    localStorage.setItem("indexy", JSON.stringify(duplnew)); // Store as a string
    document.getElementById("myInput").value = duplnew.join(','); // Display indices as a comma-separated string
};

// Remove duplicates
function r1(indices) {
    const table = document.getElementById('tab2');
    const tbody = table.tBodies[0];

    indices.sort((a, b) => b - a); // Sort in descending order

    for (let index of indices) {
        if (index >= 0 && index < tbody.rows.length) {
            tbody.deleteRow(index);
        }
    }
}

function r2(indices) {
    const table = document.getElementById('tab1');
    const tbody = table.tBodies[0];

    indices.sort((a, b) => b - a); // Sort in descending order

    for (let index of indices) {
        if (index >= 0 && index < tbody.rows.length) {
            tbody.deleteRow(index);
        }
    }
}

function r0() {
    var ziskej = document.getElementById("myInput").value;
    var ziskej2 = '[' + ziskej + ']';
    var val0 = JSON.parse(ziskej2);

    r1(val0);
    r2(val0);
}

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