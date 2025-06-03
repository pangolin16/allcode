
  // Import the functions you need from the SDKs you need
 import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
  // TODO: Add SDKs for Firebase products that you want to use
  // https://firebase.google.com/docs/web/setup#available-libraries

  // Your web app's Firebase configuration
  // For Firebase JS SDK v7.20.0 and later, measurementId is optional
  const firebaseConfig = {
    apiKey: "AIzaSyCbFr69C6oPGZJaX4CcJcZ8JDp6l5v9kEo",
    authDomain: "pangolin-f37fa.firebaseapp.com",
    projectId: "pangolin-f37fa",
    storageBucket: "pangolin-f37fa.firebasestorage.app",
    messagingSenderId: "880099895366",
    appId: "1:880099895366:web:a062f25c2d0d3ff2b0c247",
    measurementId: "G-2SG3MJBCYF"
  };


// Initialize Firebase
const app = initializeApp(firebaseConfig);


// Initialize Firebase Authentication and get a reference to the service
const auth = getAuth(app);
