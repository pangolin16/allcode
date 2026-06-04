import { initializeApp } from "https://www.gstatic.com/firebasejs/11.8.1/firebase-app.js";
import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  signOut,
  onAuthStateChanged,
} from "https://www.gstatic.com/firebasejs/11.8.1/firebase-auth.js";

const firebaseConfig = {
  apiKey: "AIzaSyCkKS79ztaGyEDS29mKAgo_3-fnXTfmyro",
  authDomain: "pangolin-f37fa.firebaseapp.com",
  projectId: "pangolin-f37fa",
  storageBucket: "pangolin-f37fa.firebasestorage.app",
  messagingSenderId: "880099895366",
  appId: "1:880099895366:web:edcf2fbdbdc2decbb0c247",
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

function updateAuthUI(user) {
  document.querySelectorAll(".auth-btn").forEach((btn) => {
    if (user) {
      btn.innerHTML = `<img src="${user.photoURL}" class="auth-avatar" alt="${user.displayName}"> <span class="auth-name">${user.displayName.split(" ")[0]}</span>`;
      btn.title = "Sign out";
      btn.onclick = () => signOut(auth);
    } else {
      btn.innerHTML = '<i class="fa-solid fa-user"></i>';
      btn.title = "Sign in with Google";
      btn.onclick = () =>
        signInWithPopup(auth, provider).catch((err) => console.error(err));
    }
  });
}

onAuthStateChanged(auth, updateAuthUI);
