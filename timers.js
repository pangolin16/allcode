//list of words
var validWords = ["cat", "dog"]; // List of valid words
var score = 0; // Initialize score

function checkWord() {
    const userInput = document.getElementById("userInput").value.toLowerCase(); // Convert input to lowercase
    const resultDiv = document.getElementById("result"); // Get result div

    if (validWords.includes(userInput)) {
        score += 10; // Add 10 points if the word is valid
        document.getElementById("score").textContent = score; // Update score display
        resultDiv.textContent = "The word is valid!"; // Display valid message
    } else {
        resultDiv.textContent = "The word is not valid."; // Display invalid message
    }

    document.getElementById("userInput").value = ''; // Clear input field
}








var alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
var i = 0;
var intervalID;
var usedLetters = new Set(); // Set to track used letters

function startGenerating() {
  // Clear any existing interval
  clearInterval(intervalID);
  usedLetters.clear(); // Clear the set for new session

  // Loop through the alphabet
  intervalID = setInterval(function() {
    document.getElementById("alpha").innerHTML = alphabet[i];
    i++;
    if (i === alphabet.length) {
      i = 0; // Reset to start of the alphabet
    }
  }, 100); // Change letter every 100 ms

  // After a short delay, stop on a random letter
  setTimeout(stopGenerating, 1000); // Adjust how long it loops
}

function stopGenerating() {
  clearInterval(intervalID);
  
  // Generate a random letter that hasn't been used
  let randomAlphabet;
  do {
    var randomIndex = Math.floor(Math.random() * alphabet.length);
    randomAlphabet = alphabet[randomIndex];
  } while (usedLetters.has(randomAlphabet));

  // Add the letter to the Set to prevent future duplicates
  usedLetters.add(randomAlphabet);
  document.getElementById("alpha").innerHTML = randomAlphabet;
}

// Add event listener to the start button
document.querySelector('.start').addEventListener('click', startGenerating);


//timer

const el = document.querySelector(".clock");
const bell = document.querySelector("audio");

const mindiv = document.querySelector(".mins");
const secdiv = document.querySelector(".secs");

const startBtn = document.querySelector(".start");
localStorage.setItem("btn", "focus");

let initial, totalsecs, perc, paused, mins, seconds;

startBtn.addEventListener("click", () => {
  let btn = localStorage.getItem("btn");

  if (btn === "focus") {
    mins = +localStorage.getItem("focusTime") || 1;
  } else {
    mins = +localStorage.getItem("breakTime") || 1;
  }

  seconds = mins * 60;
  totalsecs = mins * 60;
  setTimeout(decremenT(), 60);
  startBtn.style.transform = "scale(0)";
  paused = false;
});

function decremenT() {
  mindiv.textContent = Math.floor(seconds / 60);
  secdiv.textContent = seconds % 60 > 9 ? seconds % 60 : `0${seconds % 60}`;
  if (circle.classList.contains("danger")) {
    circle.classList.remove("danger");
  }

  if (seconds > 0) {
    perc = Math.ceil(((totalsecs - seconds) / totalsecs) * 100);
    setProgress(perc);
    seconds--;
    initial = window.setTimeout("decremenT()", 1000);
    if (seconds < 10) {
      circle.classList.add("danger");
    }
  } else {
    mins = 0;
    seconds = 0;
    bell.play();
    let btn = localStorage.getItem("btn");

    if (btn === "focus") {
      startBtn.textContent = "restart";
      startBtn.classList.add("break");
      localStorage.setItem("btn", "break");
    } else {
      startBtn.classList.remove("break");
      startBtn.textContent = "restart";
      localStorage.setItem("btn", "focus");
    }
    startBtn.style.transform = "scale(1)";
  }
}
//settings
const focusTimeInput = document.querySelector("#focusTime");


focusTimeInput.value = localStorage.getItem("focusTime");

document.querySelector("form").addEventListener("submit", (e) => {
  e.preventDefault();
  localStorage.setItem("focusTime", focusTimeInput.value);

});

document.querySelector(".reset").addEventListener("click", () => {
  startBtn.style.transform = "scale(1)";
  clearTimeout(initial);
  setProgress(0);
  mindiv.textContent = 0;
  secdiv.textContent = 0;
});




