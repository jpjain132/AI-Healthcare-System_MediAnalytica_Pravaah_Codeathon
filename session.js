// session.js

console.log("session.js loaded");

const FIVE_DAYS = 5 * 24 * 60 * 60 * 1000;
const STORAGE_KEY = "auth_session";

/* =========================
   SAVE SESSION
========================= */
function saveSession(user){
  const sessionData = {
    user: {
      id: user.id || null,
      email: user.email
    },
    expiresAt: Date.now() + FIVE_DAYS
  };

  localStorage.setItem(STORAGE_KEY, JSON.stringify(sessionData));
  console.log("Session saved:", sessionData);
}

/* =========================
   GET SESSION
========================= */
function getSession(){
  const data = localStorage.getItem(STORAGE_KEY);
  if(!data) return null;

  const session = JSON.parse(data);

  if(Date.now() > session.expiresAt){
    clearSession();
    return null;
  }

  return session;
}

/* =========================
   AUTO REDIRECT IF LOGGED IN
========================= */
function redirectIfLoggedIn(){
  const session = getSession();
  if(session){
    window.location.href = "index.html";
  }
}

/* =========================
   REQUIRE AUTH (GUARD)
========================= */
function requireAuth(redirectUrl = "login.html"){
  const session = getSession();
  if(!session){
    window.location.href = redirectUrl;
  }
}

/* =========================
   SIGN OUT (LOCAL + SUPABASE)
========================= */
async function signOut(){
  try{
    if(window.supabase){
      await window.supabase.auth.signOut();
    }
  }catch(err){
    console.warn("Supabase signOut failed:", err);
  }

  clearSession();
  window.location.href = "login.html";
}

/* =========================
   CLEAR SESSION
========================= */
function clearSession(){
  localStorage.removeItem(STORAGE_KEY);
  console.log("Session cleared");
}

/* =========================
   EXPOSE TO WINDOW
========================= */
window.saveSession = saveSession;
window.getSession = getSession;
window.requireAuth = requireAuth;
window.redirectIfLoggedIn = redirectIfLoggedIn;
window.signOut = signOut;
window.clearSession = clearSession;
