        // Your web app's Firebase configuration
      
        // For Firebase JS SDK v7.20.0 and later, measurementId is optional
      
        const firebaseConfig = {
      
            apiKey: "AIzaSyCkKS79ztaGyEDS29mKAgo_3-fnXTfmyro",
        
            authDomain: "pangolin-f37fa.firebaseapp.com",
        
            projectId: "pangolin-f37fa",
        
            storageBucket: "pangolin-f37fa.firebasestorage.app",
        
            messagingSenderId: "880099895366",
        
            appId: "1:880099895366:web:edcf2fbdbdc2decbb0c247",
        
            measurementId: "G-M31Q6C45FX"
        




 };


        // Initialize Firebase
        const app = firebase.initializeApp(firebaseConfig);
        const db = firebase.firestore();

        const editableText = document.getElementById("editableText");
        const saveButton = document.getElementById("saveButton");

        // Load existing text from Firestore
        db.collection("editableText").doc("content").onSnapshot((doc) => {
            if (doc.exists) {
                editableText.innerText = doc.data().text;
            }
        });

        // Save changes to Firestore
        saveButton.addEventListener("click", () => {
            const text = editableText.innerText;
            db.collection("editableText").doc("content").set({ text: text })
                .then(() => {
                    console.log("Text saved successfully!");
                })
                .catch((error) => {
                    console.error("Error saving text: ", error);
                });
        });























//  var jmeno =document.getElementById("name");

//           var messagesRef=firebase.database().ref("messages");
        
//         function savemessage(name){var newmessageRef=messagesRef.push;newmessageRef.set({name:name})}