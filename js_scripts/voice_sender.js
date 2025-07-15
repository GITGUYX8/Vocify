let mediaRecorder;
let chunks = [];

const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const status = document.getElementById("audio-status");
const audioPlayer = document.getElementById("audioPlayer");

startBtn.onclick = async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  mediaRecorder.ondataavailable = e => chunks.push(e.data);

  mediaRecorder.onstop = () => {
    const blob = new Blob(chunks, { type: 'audio/webm' });
    const formData = new FormData();
    formData.append('file', blob, 'voice.webm');

    fetch('/upload', { method: 'POST', body: formData })
      .then(() => {
        status.innerText = "Uploaded!";
        audioPlayer.src = '/uploads/received_audio.webm?' + Date.now();
        audioPlayer.style.display = "block";
      })
      .catch(() => status.innerText = "❌ Upload failed");
  };

  mediaRecorder.start();
  chunks = [];
  startBtn.disabled = true;
  stopBtn.disabled = false;
  status.innerText = "🎙️ Recording...";
};

stopBtn.onclick = () => {
  mediaRecorder.stop();
  startBtn.disabled = false;
  stopBtn.disabled = true;
  status.innerText = "Uploading...";
};
