

function cutCage() {
    const filename = document.getElementById('video-selector').value;
    const start = document.getElementById('start-time').value;
    const end = document.getElementById('end-time').value;
  
    fetch('/cut_cage', {
      method: 'POST',
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: `filename=${encodeURIComponent(filename)}&start=${start}&end=${end}`
    })
    .then(res => res.json())
    .then(data => {
      const resDiv = document.getElementById('cut-result');
      if (data.success) {
        resDiv.innerHTML = `<p>Fragment zapisany: <a href="${data.output}" target="_blank">Zobacz</a></p>`;
      } else {
        resDiv.innerHTML = `<p>Błąd: ${data.error}</p>`;
      }
    });
  }

//skrypt do segmentacji
document.querySelectorAll('.video-file').forEach(link => {
  link.addEventListener('click', async function(e) {
    e.preventDefault();
    const filename = this.getAttribute('data-filename');

    const formData = new FormData();
    formData.append('filename', filename);

    // Wysyłamy żądanie do backendu
    const response = await fetch('/extract_frames_existing', {  // endpoint do obsługi istniejącego pliku
      method: 'POST',
      body: formData
    });
    const result = await response.json();

   if (result.success) {
  const frameContainer = document.getElementById('frame-container');
  frameContainer.innerHTML = '';

  result.frames.forEach((frameUrl, idx) => {
    const img = document.createElement('img');
    img.src = frameUrl;

    // Ukrywamy wszystkie, oprócz pierwszej klatki
    img.style.display = idx === 0 ? 'block' : 'none';
    frameContainer.appendChild(img);
  });

  const slider = document.getElementById('frame-slider');
  slider.max = result.frames.length - 1;
  slider.value = 0; // Ustaw suwak na start
   slider.style.display = 'block'; 

  // Obsługa suwaka
  slider.oninput = function() {
    const images = frameContainer.querySelectorAll('img');
    images.forEach(img => img.style.display = 'none'); // Ukryj wszystkie
    images[this.value].style.display = 'block';        // Pokaż tylko wybraną
  };
}

  });
});

//seg
function segmentFrame(folder, frameName) {
    fetch(`/segment_frame/${folder}/${frameName}`)
      .then(response => response.json())
      .then(result => {
        if (result.success) {
          const resDiv = document.getElementById('segment-result');
          resDiv.innerHTML = `<img src="${result.mask_url}" alt="Segmentation mask">`;
        } else {
          alert('Error: ' + result.error);
        }
      });
  }
  