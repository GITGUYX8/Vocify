function sendCommand(endpoint) {
  fetch(endpoint, { method: 'POST' })
    .then(res => res.text())
    .then(msg => {
      document.getElementById('cam-status').innerText = msg;

      if (endpoint === '/capture') {
        document.getElementById('photo').src = `/uploads/captured_photo.jpg?${Date.now()}`;
      }

      if (endpoint === '/record') {
        const video = document.getElementById('video');
        const source = document.getElementById('videoSource');
        source.src = `/uploads/captured_video.mp4v?${Date.now()}`;
        video.load();
      }
    })
    .catch(err => alert("Error: " + err));
}
