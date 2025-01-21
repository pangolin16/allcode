

const inpKey=document.getElementById("inpKey").value;
const btnSubmit=document.getElementById("btnSubmit");
const string0=document.getElementById("out0");
btnSubmit.onclick=function(){const key=inpKey;
  if(key){localStorage.setItem("vstup",key);
    location.reload();};}


 const vystupek=localStorage.getItem("vstup")
 string0.value=vystupek;


const string1=document.getElementById("out0").value;
function replaceLetters(inputString) {
  return inputString
  .replace(/d/gi, '')   // Remove all 'd' letters
     .replace(/l/gi, '')   // Remove all 'l' letters
     .replace(/á/gi, '')   // Remove all 'á' letters
     .replace(/o/gi, '0')  // Replace 'o' with '0'
     .replace(/i/gi, '1') // Replace 'i' with '1'
     .replace(/a/gi, '4'); // Replace 'a' with '4'
}



const string2 = replaceLetters(string1);
let array0 =string2.split(' ');


function removeLettersIfConditionMet(inputString) {
    // Check if the string contains either '6250' or '6240' and does not contain 'm'
    if ((inputString.includes('6250') || inputString.includes('6240')) && !inputString.includes('m')) {
        // Remove all letters from the string
        return inputString.replace(/[a-zA-Z]/g, ''); // This regex matches all letters
    }
    return inputString; // Return the original string if conditions not met
}

// Process the array and remove letters based on the condition
const array1 = array0.map(removeLettersIfConditionMet);

const filteredArray = array1.filter(item => item.trim() !== "");

function removeAdjacentStringsStartingWith(array, letterList1, letterList2) {
  for (let i = 0; i < array.length - 1; i++) {
      // Check if the current element starts with a letter from letterList1
      // and the next element starts with a letter from letterList2
      if (letterList1.includes(array[i][0]) && letterList2.includes(array[i + 1][0])) {
          // Remove the two adjacent strings
          array.splice(i, 2);
          // Move the index back to check for more occurrences
          i--;
      }
  }
  return array;
}

const originalArray =[...filteredArray];
const letterList1 = ["6"]; // Letters that the first string can start with
const letterList2 = ["P","V"]; // Letters that the second string can start with

const result = removeAdjacentStringsStartingWith(originalArray, letterList1, letterList2);





function extractAndCleanSubstrings(array) {
  const result = array
    .filter(str => str.includes("6240")|| str.includes("6250") ) // Step 1: Filter
     .map(str => str.replace(/[,.-]/g, '')); // Step 2: Remove . and - symbols

 return result;
}
 const result1 = [...result];
 const result2 = extractAndCleanSubstrings(result1);







const seznam3=[...result]

const filtered=seznam3.filter(function(value){return typeof value==="string" && value.startsWith("M10");});

const filtered2 = result2.filter(function(value) {
  return typeof value === "string" && (value.includes("6240") || value.includes("6250"));
});


    window.onload = function fc(){

         let html = "<table id='tab2'>";
         for (var i = 0; i < filtered2.length; i++) {
             html += "<tr><td><i class='fa-solid fa-rectangle-xmark'></i></td><td>" + filtered2[i] + "</td></tr>";
         }
         html += "</table>";


             
         html = document.getElementById("outputs").innerHTML = html;





     
         let html2 = "<table id='tab1'>";
         for (var i = 0; i < filtered.length; i++) {
             html2 += "<tr><td>" + filtered[i] + "</td></tr>";
         }
         html2 += "</table>";
         html2 = document.getElementById("outputs2").innerHTML = html2;




         const firstTable = document.getElementById("tab2");
         firstTable.addEventListener('click', function(event) {
             const target = event.target;
     
             // Check if the clicked cell is the first cell of a row
             if (target.tagName === 'TD' && target.cellIndex === 0) {
                 // Get the parent row
                 const row = target.parentNode;
     
                 // Get the current row index
                 const rowIndex = row.rowIndex;
     
                 // Remove the row from the first table (tab2)
                 firstTable.deleteRow(rowIndex);
     
                 // Remove the corresponding row from the second table (tab1)
                 const secondTable = document.getElementById("tab1");
                 if (rowIndex < secondTable.rows.length) {
                     secondTable.deleteRow(rowIndex);
                 } else {
                     console.error(`Row index ${rowIndex} is out of bounds for tab1.`);
                 }
             }
         });

         
         let btns = document.querySelectorAll("tr td:not(:nth-child(1))");
         for (i of btns) {
            i.addEventListener('click', function() {
    
              if(this.style.background=="white"){this.style.background="yellow";}
           else{this.style.background="white";}
                });}


                 const findDuplicates = filtered2 => filtered2.map((item, index) => {
                  if (filtered2.indexOf(item) !== index)
                     return index;
                 }).filter(x => x);
                
               const duplicates = findDuplicates(filtered2);
                
               const duplnew=  duplicates.map(function(element){
                  return element - 1;
               });
               
               const duplnew2=localStorage.setItem("indexy",duplnew);document.getElementById("myInput").value=duplnew;
             
            
            
               
         
      
        }

     
          function r1(indices) {


const table=document.getElementById('tab2');
const table2=document.getElementById('tab1');
           
            const tbody = table.tBodies[0];
            indices.sort((a, b) => a - b);

            
            for (let i = indices.length - 1; i >= 0; i--) {
                const index = indices[i];
                if (index >= 0 && index < tbody.rows.length) {
                    tbody.deleteRow(index);
            }
        }


          }

          function r2(indices) {


            const table=document.getElementById('tab1');
                       
                        const tbody = table.tBodies[0];
                        indices.sort((a, b) => a - b);
            
                        
                        for (let i = indices.length - 1; i >= 0; i--) {
                            const index = indices[i];
                            if (index >= 0 && index < tbody.rows.length) {
                                tbody.deleteRow(index);
                        }
                    }
            
            
                      };
                  

   
                         function r0(){var ziskej=document.getElementById("myInput").value
                    
                          var ziskej2='['+ziskej+']';
                          var val0=JSON.parse(ziskej2);
                          
                           r1(val0),r2(val0);



                           
                         };
                  
                    
                         
                   

function colour()  {const table = document.querySelectorAll('table')[1];
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
  };
  

  // window.onload = function fc9(){
  // const f3= seznam3.filter(num => typeof num === 'number')
  // console.log(f3)}

  

