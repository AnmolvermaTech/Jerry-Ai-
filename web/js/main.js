// -------------------- INPUT HANDLING --------------------
document.getElementById("userInputButton").addEventListener("click", sendMessage);
document.getElementById("userInput").addEventListener("keyup", e => { 
    if (e.key === "Enter") sendMessage(); 
});

let micBusy = false; // ✅ Prevent double voice triggers


// -------------------- DISPLAY MESSAGE --------------------
function displayMessage(msg, sender){
    let box = document.getElementById("messages");
    let div = document.createElement("div");
    div.className = `message ${sender} fade-in`;

    let avatar = document.createElement("img");
    avatar.className = "avatar";
    avatar.src = sender === "user" ? "images/user.png" : "images/bot.png";

    let bubble = document.createElement("div");
    bubble.className = "bubble";

    // ✅ Detect <code> blocks and apply copy button
    if(msg.includes("<code>") && msg.includes("</code>")){
        let code = msg.match(/<code>([\s\S]*?)<\/code>/)[1];

        bubble.innerHTML = `
        <div class="code-block">
            <button class="copy-btn" onclick="copyCode(this)">Copy</button>
            <pre><code>${code}</code></pre>
        </div>`;
    } 
    else {
        bubble.innerHTML = msg.replace(/\n/g, "<br>");
    }

    div.appendChild(avatar);
    div.appendChild(bubble);
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
}


// -------------------- COPY CODE --------------------
function copyCode(btn){
    let code = btn.parentElement.querySelector("code").innerText;
    navigator.clipboard.writeText(code);
    btn.innerText = "Copied!";
    setTimeout(() => btn.innerText = "Copy", 1200);
}


// -------------------- RECEIVE MESSAGES FROM PYTHON --------------------
eel.expose(addUserMsg);
function addUserMsg(msg) {
    displayMessage(msg, "user");
}

eel.expose(addAppMsg);
function addAppMsg(msg) {
    displayMessage(msg, "bot");
}


// -------------------- SEND MESSAGE TO PYTHON --------------------
function sendMessage(){
    let input = document.getElementById("userInput");
    if(input.value.trim()){
        eel.getUserInput(input.value.trim());
        input.value = "";
    }
}


// -------------------- MIC BUTTON (FIXED + ANIMATION) --------------------
document.getElementById("micButton").addEventListener("click", async () => {
    if (micBusy) return;
    micBusy = true;

    let btn = document.getElementById("micButton");
    btn.classList.add("mic-active");   // ✅ Start animation

    let text = await eel.voiceInput()(); // ✅ Correct voice call

    btn.classList.remove("mic-active"); // ✅ Stop animation
    micBusy = false;

    if (text && text.trim()){
        eel.getUserInput(text.trim());
    }
});


// -------------------- UPDATE GESTURE STATUS --------------------
eel.expose(updateGestureStatus);
function updateGestureStatus(status){
    let el = document.getElementById("gestureStatus");
    el.innerText = status === "on" ? "🟢 Gesture ON" : "🔴 Gesture OFF";
}


// -------------------- LOAD CHAT HISTORY --------------------
eel.loadHistory()(function(history){
    history.forEach(msg => displayMessage(msg.text, msg.sender));
});


// -------------------- CLEAR CHAT --------------------
document.getElementById("clearChatButton").addEventListener("click", () => {
    document.getElementById("messages").innerHTML = "";
    eel.clearHistory();
});
