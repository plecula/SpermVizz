let currentFolder = '';
let framesList = [];
let currentFrameIndex = 0;

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

  function segmentCurrentFrame() {
    const frameNumber = currentFrameIndex + 1;
    const frameName = `frame_${frameNumber}.jpg`;

    fetch(`/segment_frame/${currentFolder}/${frameName}`)
      .then(response => response.json())
      .then(result => {
        if (result.success) {
          const maskUrl = result.mask_url;

          const resDiv = document.getElementById('segment-result');
          if (resDiv) {
            resDiv.innerHTML = `<img src="${maskUrl}" alt="Segmentation mask">`;
          }

            // maska w video-tile
          const tile1 = document.querySelector('.video-right .video-wrapper:nth-child(1) .video-tile');
          tile1.innerHTML = `<img src="${maskUrl}" style="max-width: 100%; max-height: 100%;">`;

          // maska w canvas
          const canvas = document.getElementById('mask-canvas');
          const ctx = canvas.getContext('2d');
          const image = new Image();
          image.onload = function() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
          };
          image.src = maskUrl;
        
        
        
        } else {
          alert('Error: ' + result.error);
        }
      });
  }

  function nextFrame() {
    if (currentFrameIndex < framesList.length - 1) {
      currentFrameIndex++;
      const slider = document.getElementById('frame-slider');
      slider.value = currentFrameIndex;
      slider.oninput();  // uobsluga suwaka
    }
  }
 

//skrypt do segmentacji
document.querySelectorAll('.video-file').forEach(link => {
  link.addEventListener('click', async function(e) {
    e.preventDefault();
    const filename = this.getAttribute('data-filename');

    const formData = new FormData();
    formData.append('filename', filename);

    // POST do backendu
    const response = await fetch('/extract_frames_existing', {  // endpoint do obsługi istniejącego pliku
      method: 'POST',
      body: formData
    });
    const result = await response.json();
    currentFolder = result.folder;

   if (result.success) {
    const frameContainer = document.getElementById('frame-container');
    frameContainer.innerHTML = '';

    framesList = result.frames;
    currentFolder = result.folder;  // backend folder
    currentFrameIndex = 0;

    result.frames.forEach((frameUrl, idx) => {
      const img = document.createElement('img');
      img.src = frameUrl;

      // Ukrywamy wszystkie, oprócz pierwszej klatki
      img.style.display = idx === 0 ? 'block' : 'none';
      frameContainer.appendChild(img);
    });

    const slider = document.getElementById('frame-slider');
    slider.max = result.frames.length - 1;
    slider.value = 0; //  suwak na start
    slider.style.display = 'block'; 

    // wyswietla nazwy 1 klatki i folderu
    document.getElementById('current-frame-name').innerText = framesList[0].split('/').pop();
    document.getElementById('current-folder-name').innerText = currentFolder;

    // suwak
    slider.oninput = function() {
      const images = frameContainer.querySelectorAll('img');
      images.forEach(img => img.style.display = 'none'); // Ukryj wszystkie
      images[this.value].style.display = 'block';        // Pokaż tylko wybraną
      currentFrameIndex = parseInt(this.value);

      // update nazwy
      document.getElementById('current-frame-name').innerText = `frame_${currentFrameIndex + 1}.jpg`;
      document.getElementById('current-folder-name').innerText =currentFolder;
    };

    
  }

  });
});
  