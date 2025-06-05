let currentFolder = '';
let framesList = [];
let currentFrameIndex = 0;
let selectedModel = null;
let selectedModels = [];
let selectedPoints = [];
let trackMasks = [];

const pageType = document.body.getAttribute('data-page-type');

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

  // choose model

  document.querySelectorAll('.model-btn').forEach(button => {
    button.addEventListener('click', () => {
      

      if (pageType === 'single' || pageType === 'track'){

        document.querySelectorAll('.model-btn').forEach(btn => btn.classList.remove('selected'));

        button.classList.add('selected');

        selectedModel = button.getAttribute('data-model');
      }

      else if (pageType === 'compare') {
        const modelName = button.getAttribute('data-model');

        if (button.classList.contains('selected')) {
          button.classList.remove('selected');
          selectedModels = selectedModels.filter(m => m !== modelName);
        } 
        else {
          if (selectedModels.length >= 2) {
            alert('Only 2 models!');
            return;
          }
          button.classList.add('selected');
          selectedModels.push(modelName);
        }
      }

    })
  })

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
   
    const frameNumber = currentFrameIndex;
    const frameName = `frame_${frameNumber + 1}.jpg`;

    console.log(`Segmenting: /segment_frame/${currentFolder}/${frameName}`);
  
    if (pageType === 'compare') {
      if (selectedModels.length !== 2) {
        alert('Wybierz dokładnie 2 modele!');
        return;
      }
 

      const maskCanvases = document.querySelectorAll('.mask-canvas');
      const captions = document.querySelectorAll('.video-caption');


      // segmentacja dla modelu 1
      fetch(`/segment_frame/${currentFolder}/${frameName}?model=${selectedModels[0]}`)
        .then(response => response.json())
        .then(result1 => {
          if (result1.success) {
            const maskUrl1 = result1.mask_url;

             // canvas z maską
             const canvas1 = maskCanvases[0];
             //const canvas1 = document.getElementsByClassName('mask-canvas')[0];
             const ctx1 = canvas1.getContext('2d');
             const image1 = new Image();
             image1.onload = function() {
               ctx1.clearRect(0, 0, canvas1.width, canvas1.height);
               ctx1.drawImage(image1, 0, 0, canvas1.width, canvas1.height);
             };
             image1.src = maskUrl1;
    

            captions[0].innerText = `Model 1: ${selectedModels[0]}`;
          } else {
            alert('First model error: ' + result1.error);
          }

    
          // segmentacja dla modelu 2 po zakończeniu pierwszego
          return fetch(`/segment_frame/${currentFolder}/${frameName}?model=${selectedModels[1]}`)
        })
        .then(response => response.json())
        .then(result2 => {
          if (result2.success) {
            const maskUrl2 = result2.mask_url;
    
            // canvas z maską
            const canvas2 = maskCanvases[1];
            //const canvas2 = document.getElementsByClassName('mask-canvas')[1];
            const ctx2 = canvas2.getContext('2d');
            const image2 = new Image();
            image2.onload = function() {
              ctx2.clearRect(0, 0, canvas2.width, canvas2.height);
              ctx2.drawImage(image2, 0, 0, canvas2.width, canvas2.height);
            };
            image2.src = maskUrl2;

          captions[1].innerText = `Model 2: ${selectedModels[1]}`;
          } else {
            alert('Second model error: ' + result2.error);
          }
        })
        .catch(error => {
          console.error('Błąd w segmentacji:', error);
        });
    }

    else if (pageType === 'single') {
      if(!selectedModel) {
        alert("At first choose segmentation model!");
        return;
      }

      fetch(`/segment_frame/${currentFolder}/${frameName}?model=${encodeURIComponent(selectedModel)}`)
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
            tile1.innerHTML = `<img src="${maskUrl} "style="max-width: 100%; max-height: 100%;">`;  //"style="max-width: 100%; max-height: 100%;"
  
            // maska w canvas
            const canvas = document.getElementById('mask-canvas');
            const ctx = canvas.getContext('2d');
            const image = new Image();
            image.onload = function() {
              ctx.clearRect(0, 0, canvas.width, canvas.height);
              ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
            };
            image.src = maskUrl;
          
           // podpis         
           document.querySelector('.video-right .video-wrapper:nth-child(1) .video-caption').innerText = `Frame: ${frameName}`;
           document.querySelector('.video-right .video-wrapper:nth-child(2) .video-caption').innerText = `Editing frame: ${frameName}`;

          } else {
            alert('Error jol: ' + result.error);
          }
        });
    }
  
    else if (pageType === 'track') {
      if(!selectedModel) {
        alert("At first choose segmentation model!");
        return;
      }
      segmentWithPoints();

      
    }

  }


  
  function nextFrame() {
    if (currentFrameIndex < framesList.length - 1) {
      currentFrameIndex++;
      const slider = document.getElementById('frame-slider');
      slider.value = currentFrameIndex;
      slider.oninput();  // uobsluga suwaka
    }
  }
 

//skrypt do klatkowania

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

      images.forEach(img => img.style.display = 'none'); // ukrywa wszystkie
      images[this.value].style.display = 'block';        // pokazuje tylko wybraną

      currentFrameIndex = parseInt(this.value);

      // update nazwy
      document.getElementById('current-frame-name').innerText = `frame_${currentFrameIndex + 1}.jpg`;
      document.getElementById('current-folder-name').innerText =currentFolder;
    };

    
  }

  });
});

// tracking

document.getElementById("frame-container").addEventListener("click", function(e) {
  const rect = this.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;

  if (selectedPoints.length < 2) {
    selectedPoints.push([x, y]);

    if (selectedPoints.length === 1) {
      document.querySelector('p:nth-of-type(3)').innerText = `Head: (${x.toFixed(1)}, ${y.toFixed(1)})`;
    } else {
      document.querySelector('p:nth-of-type(4)').innerText = `Flagellum: (${x.toFixed(1)}, ${y.toFixed(1)})`;
    }
  }
});

function resetPoints() {
  selectedPoints = [];
  document.querySelector('p:nth-of-type(3)').innerText = "Head: ";
  document.querySelector('p:nth-of-type(4)').innerText = "Flagellum: ";
}


function segmentWithPoints() {
  if (selectedPoints.length < 2) {
    alert("Click on head and flagellum first!");
    return;
  }

  const frameNumber = currentFrameIndex;
  const frameName = `frame_${frameNumber + 1}.jpg`;

  fetch('/track_and_segment_sperm', {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      folder: currentFolder,
      model: selectedModel,
      points: selectedPoints
    })
  })
  .then(response => response.json())
  .then(result => {
    if (result.success) {
      trackMasks = result.results;
  
      // maska w canvas
      const canvas3 = document.getElementById('mask-canvas');
      const ctx = canvas3.getContext('2d');
      const image = new Image();
      image.onload = function() {
        ctx.clearRect(0, 0, canvas3.width, canvas3.height);
        ctx.drawImage(image, 0, 0, canvas3.width, canvas3.height);
      };
      image.src = trackMasks[0];
  
      // suwak pod maską
      const trackSlider = document.createElement('input');
      trackSlider.type = 'range';
      trackSlider.id = 'track-slider';
      trackSlider.min = 0;
      trackSlider.max = trackMasks.length - 1;
      trackSlider.value = 0;
      trackSlider.style.width = '100%';
  
      // event do zmiany maski
      trackSlider.oninput = function() {
        const idx = parseInt(this.value);
        const img = new Image();
        img.onload = function() {
          ctx.clearRect(0, 0, canvas3.width, canvas3.height);
          ctx.drawImage(img, 0, 0, canvas3.width, canvas3.height);
        };
        img.src = trackMasks[idx];

      };
  
      // suwak
      const sliderDiv = document.getElementById('track-slider-container');
      sliderDiv.innerHTML = ''; // czyści stare
      sliderDiv.appendChild(trackSlider);

    } else {
      alert("Błąd segmentacji: " + result.error);
    }
  });
  

}

