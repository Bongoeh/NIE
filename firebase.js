import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getFirestore } from "firebase/firestore"; // For Firestore
import { getDatabase } from "firebase/database"; // For Realtime Database

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDfH01-uY7EnLZLYISxNekmaakTbaFKiSg",
  authDomain: "studywithus-8b4d0.firebaseapp.com",
  projectId: "studywithus-8b4d0",
  storageBucket: "studywithus-8b4d0.firebasestorage.app",
  messagingSenderId: "388858335353",
  appId: "1:388858335353:web:c8b869fa8f2e43b2b7c4a8",
  measurementId: "G-951JPWQH3J",
  databaseURL: "https://studywithus-8b4d0-default-rtdb.firebaseio.com" // Add this for Realtime Database
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

// Initialize Firestore (if using Firestore)
const db = getFirestore(app);

// Initialize Realtime Database (if using Realtime Database)
const realtimeDb = getDatabase(app);

// Export the database instances for use in other files
export { db, realtimeDb };