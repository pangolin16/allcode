

const inpKey=document.getElementById("inpKey").value;
const btnSubmit=document.getElementById("btnSubmit");
const out0=document.getElementById("out0");
btnSubmit.onclick=function(){const key=inpKey;
  if(key){localStorage.setItem("vstup",key);
    location.reload();
  };



 ;}
 const vystupek=localStorage.getItem("vstup")
 out0.value=vystupek;



const seznama=document.getElementById("out0").value;

let seznam2 =seznama.split(' ');




const filteredArray = seznam2.filter(item => item.trim() !== "");




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
     .filter(str => str.includes("6240") || str.includes(".") || str.includes("-")|| str.includes(",")) // Step 1: Filter
      .map(str => str.replace(/[,.-]/g, '')); // Step 2: Remove . and - symbols

  return result;
 }


 const originalArray2 = [...result];
 const result2 = extractAndCleanSubstrings(originalArray2);







const seznam3=[...result]

const filtered=seznam3.filter(function(value){return typeof value==="string" && value.startsWith("M10");});

const filtered2=result2.filter(function(value){return typeof value==="string" && value.startsWith("6240");});
const filtered3 = seznam2.filter(function(value) {
  // Check if the value is a string
  const isString = typeof value === "string";
  
  // Regular expression for DD.MM. format
  const datePattern = /^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.$/;

  // Check if the value matches the date format
  const isDate = datePattern.test(value);

  // Return true if both conditions are met
  return isString && isDate;
});

window.onload = function fc() {
  // var html = "<table id='tab2'>";
  // for (var i = 0; i < filtered2.length; i++) {
  //     html += "<tr><td>" + filtered2[i] + "</td><td contenteditable='true' id='cell" + i + "'></td></tr>";
  // }
  // html += "</table>";

  // document.getElementById("outputs").innerHTML = html;


  var html = "<table id='tab2'>";
  for (var i = 0; i < filtered2.length; i++) {
      html += `<tr><td>${filtered2[i]}</td><td contenteditable='true' id='cell${i}'></td></tr>`;
  }
  html += "</table>";

  document.getElementById("outputs").innerHTML = html;

  // Call the setup function to add event listeners
  setupTable();
        
         

     
          var html2 = "<table id=tab1>";
        for (var i = 0; i < filtered.length; i++) {
            html2 += "<tr><td>" + filtered[i] + "</td></tr>";
        }
        html2 += "</table>";
        html2 = document.getElementById("outputs2").innerHTML = html2;





//          function createTable() {
//           let html2 = "<table id='tab1'>";
//           html2 += "<tr><th>Item</th><th>Comment</th></tr>"; // Table headers
  
//           for (let i = 0; i < filtered.length; i++) {
//               html2 += "<tr>";
//               html2 += "<td>" + filtered[i] + "</td>";
//               html2 += "<td onclick='addComment(this)'><span class='comment'>Click to add comment</span></td>";
//               html2 += "</tr>";
//           }
  
//           html2 += "</table>";
//           document.getElementById("outputs2").innerhtml2 = html2;
//       }
//   // Add comment function
//   function addComment(cell) {
//     if (commentMode) {
//         const comment = prompt("Enter your comment:");
//         if (comment) {
//             cell.querySelector('.comment').textContent = comment; // Update the comment
//         }
//         commentMode = false; // Exit comment mode after adding a comment
//     }
// }

// // Button click event to enable comment mode
// document.getElementById("addCommentBtn").onclick = function() {
//     commentMode = true; // Set flag to true
// };

// // Create the table on page load
// window.onload = createTable;










        
       
         var html3 = "<table id=tab1>";
         for (var i = 0; i < filtered3.length; i++) {
             html3 += "<tr><td>" + filtered3[i] + "</td></tr>";
         }
         html3 += "</table>";
         html3 = document.getElementById("outputs3").innerHTML = html3;
    
 



          let btns = document.querySelectorAll('td');
         
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


  