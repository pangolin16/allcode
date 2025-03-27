var validWords = [
  "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", 
  "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan", "Bahamas", 
  "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", 
  "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", 
  "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", 
  "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", 
  "Chile", "China", "Colombia", "Comoros", "Congo", "Costa Rica", 
  "Croatia", "Cuba", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", 
  "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", 
  "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", 
  "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", 
  "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada", 
  "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", 
  "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iran", 
  "Iraq", "Ireland", "Israel", "Italy", "Jamaica", "Japan", 
  "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea, North", 
  "Korea, South", "Kuwait", "Kyrgyzstan", "Laos", "Latvia", 
  "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", 
  "Lithuania", "Luxembourg", "Madagascar", "Malawi", "Malaysia", 
  "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", 
  "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco", 
  "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar", 
  "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", 
  "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", 
  "Oman", "Pakistan", "Palau", "Palestine", "Panama", "Papua New Guinea", 
  "Paraguay", "Peru", "Philippines", "Poland", "Portugal", 
  "Qatar", "Romania", "Russia", "Rwanda", "Saint Kitts and Nevis", 
  "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", 
  "San Marino", "Sao Tome and Principe", "Saudi Arabia", 
  "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", 
  "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", 
  "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", 
  "Sweden", "Switzerland", "Syria", "Tajikistan", "Tanzania", 
  "Thailand", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", 
  "Tunisia", "Turkey", "Turkmenistan", "Tuvalu", "Uganda", 
  "Ukraine", "United Arab Emirates", "United Kingdom", 
  "United States", "Uruguay", "Uzbekistan", "Vanuatu", 
  "Vatican City", "Venezuela", "Vietnam", "Yemen", 
  "Zambia", "Zimbabwe"
];
var commonAnimalNames = [
  "Dog", "Cat", "Fish", "Bird", "Horse", "Rabbit", "Hamster", "Turtle", 
  "Lizard", "Snake", "Frog", "Guinea Pig", "Parrot", "Chicken", "Duck", 
  "Goat", "Sheep", "Pig", "Cow", "Deer", "Fox", "Bear", "Wolf", "Lion", 
  "Tiger", "Elephant", "Giraffe", "Zebra", "Monkey", "Kangaroo", "Panda", 
  "Koala", "Otter", "Seal", "Whale", "Dolphin", "Octopus", "Crab", 
  "Lobster", "Shrimp", "Ant", "Bee", "Butterfly", "Moth", "Spider", 
  "Scorpion", "Dragonfly", "Grasshopper", "Cockroach", "Termite", 
  "Slug", "Snail", "Bat", "Raccoon", "Squirrel", "Chipmunk", "Hedgehog", 
  "Porcupine", "Bison", "Buffalo", "Cheetah", "Leopard", "Hyena", 
  "Jaguar", "Rhino", "Hippo", "Camel", "Gorilla", "Chimpanzee", 
  "Orangutan", "Sloth", "Anteater", "Armadillo", "Ocelot", "Serval", 
  "Tasmanian Devil", "Wallaby", "Wombat", "Meerkat", "Mongoose", 
  "Manatee", "Narwhal", "Penguin", "Flamingo", "Peacock", "Swan", 
  "Canary", "Finch", "Sparrow", "Woodpecker", "Pigeon", "Dove", 
  "Raven", "Crow", "Seagull", "Parakeet", "Macaw", "Cockatoo", 
  "Budgerigar", "Quail", "Ostrich", "Emu", "Kookaburra", "Heron", 
  "Eagle", "Hawk", "Falcon", "Vulture", "Condor", "Albatross", 
  "Pelican", "Seal Lion", "Walrus", "Sea Lion", "Sea Turtle", 
  "Starfish", "Jellyfish", "Sea Urchin", "Coral", "Anemone", 
  "Lobster", "Crayfish", "Eel", "Pike", "Trout", "Salmon", 
  "Catfish", "Tuna", "Mackerel", "Snapper", "Bass", "Grouper", 
  "Swordfish", "Marlin", "Haddock", "Flounder", "Sardine", 
  "Anchovy", "Mullet", "Perch", "Carp", "Goldfish", "Betta", 
  "Guppy", "Molly", "Platies", "Cichlid", "Angelfish", "Koi", 
  "Tetra", "Barb", "Rainbowfish", "Killifish", "Dwarf Pufferfish"
];

// Repeat or expand this list to reach 1000 names as needed.



var score = 0; // Initialize score
var generatedLetter = ''; // Variable to store the randomly generated letter

function checkWord() {
  const userInput = document.getElementById("userInput").value;
  const resultDiv = document.getElementById("result"); // Get result div

  if (validWords.includes(userInput)) {
      score += 10; // Add 10 points if the word is valid
      resultDiv.textContent = "The word is valid!"; // Display valid message
  } else if (userInput.startsWith(generatedLetter)) {
      score += 10; // Add 10 points if the word starts with the generated letter
      resultDiv.textContent = "The word starts with the correct letter!"; // Display message
  } else {
      resultDiv.textContent = "The word is not valid."; // Display invalid message
  }

  document.getElementById("score").textContent = score; // Update score display
  document.getElementById("userInput").value = ''; // Clear input field
}

var alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
var i = 0;
var intervalID;
var usedLetters = new Set(); // Set to track used letters

function startGenerating() {
  clearInterval(intervalID);
  usedLetters.clear(); // Clear the set for new session

  intervalID = setInterval(function() {
      document.getElementById("alpha").innerHTML = alphabet[i];
      i++;
      if (i === alphabet.length) {
          i = 0; // Reset to start of the alphabet
      }
  }, 100); // Change letter every 100 ms

  setTimeout(stopGenerating, 1000); // Adjust how long it loops
}

function stopGenerating() {
  clearInterval(intervalID);
  
  let randomIndex = Math.floor(Math.random() * alphabet.length);
  generatedLetter = alphabet[randomIndex]; // Store the randomly generated letter
  document.getElementById("alpha").innerHTML = generatedLetter; // Display the letter
}

// Timer setup
const mindiv = document.querySelector(".mins");
const secdiv = document.querySelector(".secs");
const bell = document.querySelector("audio");
const startBtn = document.querySelector(".start");
let initial, mins, seconds;

startBtn.addEventListener("click", () => {
  mins = +document.getElementById("focusTime").value || 1;
  seconds = mins * 60;
  startGenerating(); // Start generating letters
  decremenT(); // Start the timer
  startBtn.style.transform = "scale(0)"; // Hide the start button
});

function decremenT() {
  mindiv.textContent = Math.floor(seconds / 60);
  secdiv.textContent = seconds % 60 > 9 ? seconds % 60 : `0${seconds % 60}`;

  if (seconds > 0) {
      seconds--;
      setTimeout(decremenT, 1000);
  } else {
      bell.play();
      checkWord(); // Call checkWord function when timer runs out
      startBtn.style.transform = "scale(1)"; // Show the start button again
  }
}

document.querySelector("form").addEventListener("submit", (e) => {
  e.preventDefault();
  localStorage.setItem("focusTime", document.getElementById("focusTime").value);
});