// client.js

console.log("client.js loaded");

/* Supabase CDN must already be loaded in HTML */
const supabaseUrl = "https://jfsguugvifnxpxanimum.supabase.co";
const supabaseKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impmc2d1dWd2aWZueHB4YW5pbXVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU3MjIwOTQsImV4cCI6MjA4MTI5ODA5NH0.vHq9O4n3EBosogfhNKtvu4JhEJUl4PyQ_X4SWrJr4Mo"; // keep as-is

window.supabase = supabase.createClient(supabaseUrl, supabaseKey);

console.log("Supabase initialized:", window.supabase);
