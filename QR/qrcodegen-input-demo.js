
let lastColValues = []
  // get last column cells values
function getLastColumnValues() {
  const table = document.querySelector('#tableContainer table');
  if (!table) {
    lastColValues = []; // ✅ Update global variable
    return [];
  }

  lastColValues = Array.from(table.rows).map(row => {
    const lastCell = row.cells[row.cells.length - 1];
    return lastCell ? lastCell.textContent.trim() : '';
  });

  console.log('Last column values:', lastColValues);
  return lastColValues;
}

  /// --- matData and matLookup ---
let matData = [
  ["M300015", "Pěna 23/10"],
  ["M300013", "Pěna 23/20"],
  ["M300014", "Pěna 23/30"],
  ["M300010", "Pěna 23/40"],
  ["M300011", "Pěna 23/50"],
  ["M300012", "Pěna 24/60"],
  ["M300057", "Pěna 28/70"],
  ["M300066", "Pěna 28/10"],
  ["M300024", "Pěna 35/20"],
  ["M300025", "Pěna 35/50"],
  ["M300086", "Pěna 65/40"],
  ["M300114", "Pěna 24/25"],
  ["M300022", "Pěna 35/30"],
  ["M102780", "2.31 BE"],
  ["M103226", "2.35 BE"],
  ["M105367", "2.41 BE"],
  ["M107881", "2.41 BE"],
  ["M101447", "2.31 BE"],
  ["M107869", "2.31 BE"],
  ["M104281", "3.90 AAC"],
  ["M103469", "3.91 AAC"],
  ["M104730", "3.92 AAC"],
  ["M107880", "3.92 AAC"],
  ["M102476", "3.95 AAC"],
  ["M101450", "3.95 AAC"],
  ["M104188", "3.96 AAC"],
  ["M200009", "CP 2mm"],
  ["M200043", "CP 2,5mm"],
  ["M200034", "CP 3mm"],
  ["M200001", "CP 3,5mm"],
  ["M200004", "CP 5mm"],
  ["M200014", "CP 5mm"],
  ["M102112", "2.03 BC"],
  ["M107877", "2.03 BC"],
  ["M101446", "2.30 BC"],
  ["M106269", "2.30 BC"],
  ["M107862", "2.30 BC"],
  ["M100197", "2.31 BC"],
  ["M100446", "2.31 BC"],
  ["M102338", "2.31 BC"],
  ["M107860", "2.31 BC"],
  ["M103231", "2.35 BC N2"],
  ["M107883", "2.35 BC N2"],
  ["M101765", "2.40 BC N2"],
  ["M100554", "2.40 BC N2"],
  ["M101538", "2.41 BC"],
  ["M107873", "2.41 BC"],
  ["M101455", "2.50 BC N2"],
  ["M107868", "2.50 BC N2"],
  ["M101539", "2.51 BC"],
  ["M107875", "2.51 BC"],
  ["M103225", "2.60 BC N2"],
  ["M103223", "2.70 BC N2"],
  ["M101448", "2.71 BC"],
  ["M102036", "2.71 BC"],
  ["M107863", "2.71 BC"],
  ["M101989", "2.90 BC"],
  ["M105705", "2.90 BC"],
  ["M107876", "2.90 BC"],
  ["M101990", "2.91 BC"],
  ["M101449", "2.91 BC"],
  ["M107864", "2.91 BC"],
  ["M102035", "2.91 AC"],
  ["M107879", "2.91 AC"],
  ["M103945", "2.92 AC"],
  ["M101588", "1.20 B"],
  ["M101441", "1.20 B"],
  ["M107861", "1.20 B"],
  ["M103229", "1.25 B"],
  ["M107871", "1.25 B"],
  ["M100187", "1.30 B"],
  ["M101454", "1.30 B"],
  ["M107867", "1.30 B"],
  ["M100062", "1,37 B"],
  ["M101442", "1,37 B"],
  ["M107870", "1,37 B"],
  ["M102964", "1.31 B"],
  ["M107874", "1.31 B"],
  ["M102425", "1.41 B"],
  ["M101443", "1.41 B"],
  ["M107665", "1.41 B N1"],
  ["M107859", "1.41 B"],
  ["M107878", "1.41 B N1"],
  ["M103232", "1.20 C"],
  ["M101764", "1.30 C"],
  ["M107872", "1.30 C"],
  ["M101444", "1.31 C"],
  ["M102086", "1.31 C"],
  ["M107866", "1.31 C"],
  ["M100198", "1.41 C"],
  ["M101445", "1.41 C"],
  ["M107865", "1.41 C"],
  ["M100012", "1.21 E"],
  ["M102364", "1.25 E"], 
  ["M100013", "1.25 E"]
];

// Create reverse lookup: code -> list of values
let codeToValues = {};
matData.forEach(([code, value]) => {
  if (!codeToValues[code]) codeToValues[code] = [];
  codeToValues[code].push(value);
});

// Create lookup for substitution: code -> value
let matLookup = {};
matData.forEach(([code, value]) => {
  matLookup[code] = value;
});

let currentTableData = [];
let originalRowCount = 0;
let currentFullData = [];
let rowMetadata = [];

function getColor(index) {
  const palette = [
    "#c9f1fc", "#d4f8c4", "#ffe0ac", "#f9c6c7", "#d6c6f9", "#ffc6e0",
    "#c6ffe0", "#f6f7d7", "#e6e6fa", "#cef6e3", "#ffd6d6", "#d6fffa"
  ];
  if (index < palette.length) return palette[index];
  return `hsl(${(index * 47) % 360}, 70%, 80%)`;
}

function removeContextMenu() {
  const menu = document.querySelector('.custom-context-menu');
  if (menu) menu.remove();
}

function removeDuplicateRows(tableData) {
  const uniqueRows = [];
  const seenRowSignatures = new Set();
  
  tableData.forEach(row => {
    const rowSignature = JSON.stringify(row);
    if (!seenRowSignatures.has(rowSignature)) {
      seenRowSignatures.add(rowSignature);
      uniqueRows.push(row);
    }
  });
  
  return uniqueRows;
}

function processTableData(rawTableData) {
  rawTableData.forEach(rowData => {
    // Replace empty cells with "nothing"
    for (let i = 0; i < rowData.length; i++) {
      if (!rowData[i] || rowData[i].trim() === '') {
        rowData[i] = '';
      }
    }
    
    // Process the date format
    if (rowData.length > 2 && rowData[2]) {
      const dateMatch = rowData[2].match(/^(\d{1,2})\.(\d{1,2})\.(\d{2,4})$/);
      if (dateMatch) {
        const [, day, month] = dateMatch;
        rowData[2] = `${day}.${month}.`;
      }
    }
  });

  return removeDuplicateRows(rawTableData);
  
}

function renderTable(tableData) {
  const valueCounts = {};
  tableData.forEach(row => {
    if (row.length > 1 && row[1]) {
      valueCounts[row[1]] = (valueCounts[row[1]] || 0) + 1;
    }
  });

  const frequentValues = Object.keys(valueCounts).filter(val => valueCounts[val] > 1);
  const valueColorMap = {};
  frequentValues.forEach((val, i) => {
    valueColorMap[val] = getColor(i);
  });

  const table = document.createElement('table');
  table.style.borderCollapse = 'collapse';

  tableData.forEach((rowData, rowIdx) => {
    const tr = document.createElement('tr');
    tr.dataset.rowIndex = rowIdx;
    
    rowData.forEach((cellData, colIdx) => {
      const td = document.createElement('td');
      const plainText = cellData || '';
      const cleanedData = plainText.replace(/\r?\n/g, '<br>');
      td.innerHTML = cleanedData;
      td.style.border = '1px solid #ccc';
      td.style.padding = '4px 8px';
      if (colIdx === 1 && valueColorMap[plainText]) {
        td.style.background = valueColorMap[plainText];
      }
      if (colIdx === 1) {
        td.addEventListener('contextmenu', function(e) {
          e.preventDefault();
          removeContextMenu();
          // Get the material values from the code
          const values = codeToValues[plainText];
          if (!values || values.length === 0) return;
          const menu = document.createElement('div');
          menu.className = 'custom-context-menu';
          const ul = document.createElement('ul');
          values.forEach(value => {
            const li = document.createElement('li');
            li.textContent = value;
            ul.appendChild(li);
          });
          menu.appendChild(ul);
          document.body.appendChild(menu);
          menu.style.left = `${e.pageX}px`;
          menu.style.top = `${e.pageY}px`;
        });
      } else {
        // Right-click on any cell except column 1 to toggle row selection
        td.addEventListener('contextmenu', function(e) {
          e.preventDefault();
          removeContextMenu();
          // Toggle selection for this row
          tr.classList.toggle('selected-row');
        });
      }
      if (colIdx === 0) {
        td.addEventListener('click', function() {
          td.classList.toggle('highlight-first-col');
        });
      }
      tr.appendChild(td);
    });
    
    const scissorsTd = document.createElement('td');
    const metadata = rowMetadata[rowIdx] || {};
    let emojiText = '';
    if (metadata.hasScissors) emojiText += '✂️';
    if (metadata.hasGear) emojiText += '⚙️';
    scissorsTd.textContent = emojiText;
    scissorsTd.style.border = '1px solid #ccc';
    scissorsTd.style.padding = '4px 8px';
    scissorsTd.style.textAlign = 'center';
    tr.appendChild(scissorsTd);
    table.appendChild(tr);
  });

  const container = document.getElementById('tableContainer');
  container.innerHTML = '';
  container.appendChild(table);
}

function parseTabSeparatedData(text) {
  const rows = [];
  let currentRow = [];
  let cellContent = '';
  let inQuotedCell = false;

  for (let i = 0; i < text.length; i++) {
    const char = text[i];

    if (char === '"') {
      if (inQuotedCell && text[i + 1] === '"') {
        cellContent += '"';
        i++;
      } else {
        inQuotedCell = !inQuotedCell;
      }
    } else if (char === '\t' && !inQuotedCell) {
      currentRow.push(cellContent);
      cellContent = '';
    } else if ((char === '\n' || char === '\r') && !inQuotedCell) {
      if (cellContent !== '' || currentRow.length > 0) {
        currentRow.push(cellContent);
        rows.push(currentRow);
      }
      currentRow = [];
      cellContent = '';
      if (char === '\r' && text[i + 1] === '\n') i++;
    } else {
      cellContent += char;
    }
  }

  if (cellContent !== '' || currentRow.length > 0) {
    currentRow.push(cellContent);
    rows.push(currentRow);
  }

  return rows;
}

async function readClipboardAndProcess() {
  try {
    const text = await navigator.clipboard.readText();
    const rows = parseTabSeparatedData(text);

    const fullData = rows;

    const tableData = rows.map(row => {
      const col1 = row[1] !== undefined ? row[1] : '';
      const col2 = row[2] !== undefined ? row[2] : '';
      const col8 = row[8] !== undefined ? row[8] : '';
      return [col1, col2, col8];
    });

    return { fullData, tableData };
  } catch (err) {
    console.error("Failed to read clipboard contents: ", err);
    return null;
  }
}

document.addEventListener('click', removeContextMenu);
document.addEventListener('scroll', removeContextMenu);

// Handle Delete key to remove selected rows
document.addEventListener('keydown', function(e) {
  if (e.key === 'Delete') {
    const selectedRows = document.querySelectorAll('tr.selected-row');
    if (selectedRows.length > 0) {
      // Collect row indices to delete
      const indicesToDelete = [];
      selectedRows.forEach(row => {
        const idx = parseInt(row.dataset.rowIndex);
        if (!isNaN(idx)) {
          indicesToDelete.push(idx);
        }
      });
      
      // Sort in descending order to delete from bottom to top (avoid index shifting)
      indicesToDelete.sort((a, b) => b - a);
      
      // Remove rows from all data arrays
      indicesToDelete.forEach(rowIndex => {
        if (rowIndex >= 0 && rowIndex < currentTableData.length) {
          currentTableData.splice(rowIndex, 1);
          currentFullData.splice(rowIndex, 1);
          rowMetadata.splice(rowIndex, 1);
        }
      });
      
      // Re-render table
      renderTable(currentTableData);
      updateInputField(currentFullData);
    }
  }
});

function updateInputField(fullData) {
  const textarea = document.getElementById('text-input');

  // To track duplicates
  const seen = new Set();

  const text = fullData.map(row => {
    const col1 = row[1] !== undefined ? row[1] : '';
    const col2 = row[2] !== undefined ? row[2] : '';
    let col23 = row[8] !== undefined ? row[8] : '';

    // ✅ convert DD.MM.YY → DD.MM.
    const dateMatch = col23.match(/^(\d{1,2})\.(\d{1,2})\.(\d{2,4})$/);
    if (dateMatch) {
      const [, day, month] = dateMatch;
      col23 = `${day}.${month}.`;
    }

    // Build row: empty col + 2 data cols + 5 empties + date col
    const rowArr = [''];                // 1 empty col
    rowArr.push(col1, col2);            // 2 data cols
    rowArr.push(...Array(5).fill('')); // 5 empty cols
    rowArr.push(col23);                 // last col (date)

    return rowArr.join('\t');
  }).filter(rowStr => {
    if (seen.has(rowStr)) return false; // remove duplicate
    seen.add(rowStr);
    return true;
  }).join('\n');

  textarea.value = text;
}

// --- Replace button ---
document.getElementById('btnSubmit').addEventListener('click', async () => {
  const result = await readClipboardAndProcess();
  if (result) {
    let { fullData, tableData } = result;

    // ✅ apply matData conversions
    tableData = processTableData(tableData);

    currentTableData = tableData; 
    currentFullData = fullData; 
    originalRowCount = currentTableData.length;
    
    rowMetadata = currentTableData.map(() => ({ hasScissors: true, hasGear: false }));

    renderTable(currentTableData);
    updateInputField(currentFullData);
    
    // ✅ Call getLastColumnValues after rendering
    getLastColumnValues();
  }
});

// --- Append button ---
document.getElementById('btnAppend').addEventListener('click', async () => {
  const result = await readClipboardAndProcess();
  if (result) {
    let { fullData, tableData } = result;

    tableData = processTableData(tableData);

    const existingSignatures = new Set(currentTableData.map(row => JSON.stringify(row)));
    const newSignatures = new Set();

    const uniqueNewRows = [];
    tableData.forEach(row => {
      const signature = JSON.stringify(row);
      
      if (existingSignatures.has(signature)) {
        const existingIndex = currentTableData.findIndex(r => JSON.stringify(r) === signature);
        if (existingIndex !== -1) {
          rowMetadata[existingIndex].hasGear = true;
        }
      } else if (!newSignatures.has(signature)) {
        uniqueNewRows.push(row);
        newSignatures.add(signature);
      }
    });

    currentTableData = currentTableData.concat(uniqueNewRows);
    currentFullData = currentFullData.concat(fullData);
    
    uniqueNewRows.forEach(() => {
      rowMetadata.push({ hasScissors: false, hasGear: true });
    });

    renderTable(currentTableData);   
    updateInputField(currentFullData);
    
    // ✅ Call getLastColumnValues after rendering
    getLastColumnValues();
  }
});
 
 
 
 
 
 
 





















"use strict";
var app;
(function (app) {
    function initialize() {
        getElem("loading").style.display = "none";
        getElem("loaded").style.removeProperty("display");
        let elems = document.querySelectorAll("input[type=number], input[type=text], textarea");
        for (let el of elems) {
            if (el.id.indexOf("version-") != 0)
                el.oninput = redrawQrCode;
        }
        elems = document.querySelectorAll("input[type=radio], input[type=checkbox]");
        for (let el of elems)
            el.onchange = redrawQrCode;
        redrawQrCode();
    }























    // Helper: convert Uint8Array to base64 string
    function uint8ToBase64(bytes) {
        let binary = '';
        for (let i = 0; i < bytes.length; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return btoa(binary);
    }

    function redrawQrCode() {
        // Show/hide rows based on bitmap/vector image output
        const bitmapOutput = getInput("output-format-bitmap").checked;
        const scaleRow = getElem("scale-row");
        const svgXmlRow = getElem("svg-xml-row");
        if (bitmapOutput) {
            scaleRow.style.removeProperty("display");
            svgXmlRow.style.display = "none";
        }
        else {
            scaleRow.style.display = "none";
            svgXmlRow.style.removeProperty("display");
        }
        const svgXml = getElem("svg-xml-output");
        svgXml.value = "";
        // Reset output images in case of early termination
        const canvas = getElem("qrcode-canvas");
        const svg = document.getElementById("qrcode-svg");
        canvas.style.display = "none";
        svg.style.display = "none";

        // Returns a QrCode.Ecc object based on the radio buttons in the HTML form.
        function getInputErrorCorrectionLevel() {
            if (getInput("errcorlvl-medium").checked)
                return qrcodegen.QrCode.Ecc.MEDIUM;
            else if (getInput("errcorlvl-quartile").checked)
                return qrcodegen.QrCode.Ecc.QUARTILE;
            else if (getInput("errcorlvl-high").checked)
                return qrcodegen.QrCode.Ecc.HIGH;
            else // In case no radio button is depressed
                return qrcodegen.QrCode.Ecc.LOW;
        }

        // Get form inputs and compute QR Code
        const ecl = getInputErrorCorrectionLevel();
















  function populateMissingDates(text0) {
    // 1. Split the input text into individual lines.
    const lines = text0.split('\n');

    // Regular expression to match the date pattern "DD.MM." at the end of a line.
    // \d{2} matches exactly two digits.
    // \. matches a literal dot (escaped because . is a special regex character).
    // $ asserts the position at the end of the string.
    const datePattern = /\d{2}\.\d{2}\.$/;

    // Array to store the modified lines.
    const modifiedLines = [];

    // 2. Iterate through each line.
    for (const line of lines) {
        // Trim the line to handle potential leading/trailing whitespace
        // that might interfere with the regex match, though not strictly
        // necessary for the given example as the tabs are internal.
        const trimmedLine = line.trimEnd(); // Only trim trailing whitespace

        // 3. Check if the line ends with the date pattern.
        if (datePattern.test(trimmedLine)) {
            // If a date is present, keep the line as is.
            modifiedLines.push(line);
        } else {
            // 4. If a date is missing, append '**' to the original line.
            // We use the original line (not trimmedLine) to preserve leading tabs/spaces.
            modifiedLines.push(line + '**');
        }
    }

    // 5. Join the modified lines back into a single string, separated by newlines.
    return modifiedLines.join('\n');
}









        // Gather text input, compress and encode for QR code
         

// Your input text
const text0 = getElem("text-input").value;

// ✅ Ensure lastColValues is available (get it if not already populated)
if (!lastColValues || lastColValues.length === 0) {
    getLastColumnValues();
}

// Call the function to get the modified text
const text1 = populateMissingDates(text0);
















console.log("\nModified Text:\n", text1);





// Split the list into lines and filter out empty ones
const lines = text1.split('\n').filter(line => line.trim());

// Map each line with its corresponding array element
const mergedLines = lines.map((line, index) => {
    if (index < lastColValues.length) {
        return `${line}    ${lastColValues[index]}`;
    }
    return line;
});

// Join back into a single string
const result = mergedLines.join('\n');

console.log(result);




































        const inputText = result.replace(/\n+/g, ' ').trim();
      
        const encoder = new TextEncoder();
        const inputBytes = Array.from(encoder.encode(inputText)); // Array of bytes

        // Asynchronous: generate QR after compression
        LZMA.compress(inputBytes, 9, function(compressed) {
            const compressedUint8 = Uint8Array.from(compressed);
            const text = uint8ToBase64(compressedUint8); // Base64 string
            // Now make QR code as normal, using the base64 string
            const segs = qrcodegen.QrSegment.makeSegments(text);
            const minVer = parseInt(getInput("version-min-input").value, 10);
            const maxVer = parseInt(getInput("version-max-input").value, 10);
            const mask = parseInt(getInput("mask-input").value, 10);
            const boostEcc = getInput("boost-ecc-input").checked;

            const qr = qrcodegen.QrCode.encodeSegments(segs, ecl, minVer, maxVer, mask, boostEcc);

            // Draw output, as in your original code...
            const border = parseInt(getInput("border-input").value, 10);
            const lightColor = getInput("light-color-input").value;
            const darkColor = getInput("dark-color-input").value;
            if (border < 0 || border > 100)
                return;
            if (bitmapOutput) {
                const scale = parseInt(getInput("scale-input").value, 10);
                if (scale <= 0 || scale > 30)
                    return;
                drawCanvas(qr, scale, border, lightColor, darkColor, canvas);
                canvas.style.removeProperty("display");
            } else {
                const code = toSvgString(qr, border, lightColor, darkColor);
                const viewBox = / viewBox="([^"]*)"/.exec(code)[1];
                const pathD = / d="([^"]*)"/.exec(code)[1];
                svg.setAttribute("viewBox", viewBox);
                svg.querySelector("path").setAttribute("d", pathD);
                svg.querySelector("rect").setAttribute("fill", lightColor);
                svg.querySelector("path").setAttribute("fill", darkColor);
                svg.style.removeProperty("display");
                svgXml.value = code;
            }

            // Returns a string to describe the given list of segments.
            function describeSegments(segs) {
                if (segs.length == 0)
                    return "none";
                else if (segs.length == 1) {
                    const mode = segs[0].mode;
                    const Mode = qrcodegen.QrSegment.Mode;
                    if (mode == Mode.NUMERIC)
                        return "numeric";
                    if (mode == Mode.ALPHANUMERIC)
                        return "alphanumeric";
                    if (mode == Mode.BYTE)
                        return "byte";
                    if (mode == Mode.KANJI)
                        return "kanji";
                    return "unknown";
                }
                else
                    return "multiple";
            }
            // Returns the number of Unicode code points in the given UTF-16 string.
            function countUnicodeChars(str) {
                let result = 0;
                for (let i = 0; i < str.length; i++, result++) {
                    const c = str.charCodeAt(i);
                    if (c < 0xD800 || c >= 0xE000)
                        continue;
                    else if (0xD800 <= c && c < 0xDC00 && i + 1 < str.length) { // High surrogate
                        i++;
                        const d = str.charCodeAt(i);
                        if (0xDC00 <= d && d < 0xE000) // Low surrogate
                            continue;
                    }
                    throw new RangeError("Invalid UTF-16 string");
                }
                return result;
            }
            // Show the QR Code symbol's statistics as a string
            getElem("statistics-output").textContent = `QR Code version = ${qr.version}, ` +
                `mask pattern = ${qr.mask}, ` +
                `character count = ${countUnicodeChars(text)},\n` +
                `encoding mode = ${describeSegments(segs)}, ` +
                `error correction = level ${"LMQH".charAt(qr.errorCorrectionLevel.ordinal)}, ` +
                `data bits = ${qrcodegen.QrSegment.getTotalBits(segs, qr.version)}.`;
        });
    }

    // Draws the given QR Code, with the given module scale and border modules, onto the given HTML
    // canvas element. The canvas's width and height is resized to (qr.size + border * 2) * scale.
    // The drawn image is purely dark and light, and fully opaque.
    // The scale must be a positive integer and the border must be a non-negative integer.
    function drawCanvas(qr, scale, border, lightColor, darkColor, canvas) {
        if (scale <= 0 || border < 0)
            throw new RangeError("Value out of range");
        const width = (qr.size + border * 2) * scale;
        canvas.width = width;
        canvas.height = width;
        let ctx = canvas.getContext("2d");
        for (let y = -border; y < qr.size + border; y++) {
            for (let x = -border; x < qr.size + border; x++) {
                ctx.fillStyle = qr.getModule(x, y) ? darkColor : lightColor;
                ctx.fillRect((x + border) * scale, (y + border) * scale, scale, scale);
            }
        }
    }
    // Returns a string of SVG code for an image depicting the given QR Code, with the given number
    // of border modules. The string always uses Unix newlines (\n), regardless of the platform.
    function toSvgString(qr, border, lightColor, darkColor) {
        if (border < 0)
            throw new RangeError("Border must be non-negative");
        let parts = [];
        for (let y = 0; y < qr.size; y++) {
            for (let x = 0; x < qr.size; x++) {
                if (qr.getModule(x, y))
                    parts.push(`M${x + border},${y + border}h1v1h-1z`);
            }
        }
        return `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 ${qr.size + border * 2} ${qr.size + border * 2}" stroke="none">
	<rect width="100%" height="100%" fill="${lightColor}"/>
	<path d="${parts.join(" ")}" fill="${darkColor}"/>
</svg>
`;
    }
    function handleVersionMinMax(which) {
        const minElem = getInput("version-min-input");
        const maxElem = getInput("version-max-input");
        let minVal = parseInt(minElem.value, 10);
        let maxVal = parseInt(maxElem.value, 10);
        minVal = Math.max(Math.min(minVal, qrcodegen.QrCode.MAX_VERSION), qrcodegen.QrCode.MIN_VERSION);
        maxVal = Math.max(Math.min(maxVal, qrcodegen.QrCode.MAX_VERSION), qrcodegen.QrCode.MIN_VERSION);
        if (which == "min" && minVal > maxVal)
            maxVal = minVal;
        else if (which == "max" && maxVal < minVal)
            minVal = maxVal;
        minElem.value = minVal.toString();
        maxElem.value = maxVal.toString();
        redrawQrCode();
    }
    app.handleVersionMinMax = handleVersionMinMax;
    function getElem(id) {
        const result = document.getElementById(id);
        if (result instanceof HTMLElement)
            return result;
        throw new Error("Assertion error");
    }
    function getInput(id) {
        const result = getElem(id);
        if (result instanceof HTMLInputElement)
            return result;
        throw new Error("Assertion error");
    }
    initialize();
})(app || (app = {}));
