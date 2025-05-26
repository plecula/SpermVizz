let currentTool = null;
let annotations = [];

function selectTool(tool) {
    currentTool = tool;
}

const canvas = document.getElementById("canvas");
const context = canvas.getContext("2d");

let isDrawing = false;
let startX, startY;

canvas.addEventListener("mousedown", (e) => {
    if (!currentTool) return;
  
    const rect = canvas.getBoundingClientRect();
    startX = e.clientX - rect.left;
    startY = e.clientY - rect.top;
    isDrawing = true;
  
});

canvas.addEventListener("mousemove", (e) => {
    if (!currentTool) return;

    const rect = canvas.getBoundingClientRect();
    currentX = e.clientX - rect.left;
    currentY = e.clientY - rect.top;
    
     // Wyczyszczenie canvasu i odrysowanie wszystkich poprzednich oznaczeń
    context.clearRect(0, 0, canvas.width, canvas.height);
    redrawAnnotations();

    const width = Math.abs(currentX - startX);
    const height = Math.abs(currentY - startY);
    const centerX = (startX + currentX) / 2;
    const centerY = (startY + currentY) / 2;

    // Rysowanie na podglądzie
    if (isDrawing) {
        drawLive(centerX, centerY, width / 2, height / 2);
    }
    
});

canvas.addEventListener("mouseup", (e) => {

    if (!isDrawing) return;
  isDrawing = false;

  const rect = canvas.getBoundingClientRect();
  const endX = e.clientX - rect.left;
  const endY = e.clientY - rect.top;

  const width = Math.abs(endX - startX);
  const height = Math.abs(endY - startY);
  const centerX = (startX + endX) / 2;
  const centerY = (startY + endY) / 2;

  // Zapisanie do tablicy anotacji
  annotations.push({
    type: currentTool,
    x: centerX,
    y: centerY,
    width: width / 2,
    height: height / 2,
    startX: startX,
    startY: startY,
    endX: endX,
    endY: endY

  });

  // Wyczyszczenie canvasu i odrysowanie wszystkich anotacji
  context.clearRect(0, 0, canvas.width, canvas.height);
  redrawAnnotations();
  currentTool = null;
});

function drawArrow(fromX, fromY, toX, toY, color = "black") {
    const headlen = 10; // długość grotka
    const dx = toX - fromX;
    const dy = toY - fromY;
    const angle = Math.atan2(dy, dx);

    // kreska
    context.beginPath();
    context.moveTo(fromX, fromY);
    context.lineTo(toX, toY);
    context.strokeStyle = color;
    context.lineWidth = 2;
    context.stroke();

    // grot
    context.beginPath();
    context.moveTo(toX, toY);
    context.lineTo(toX - headlen * Math.cos(angle - Math.PI / 6),
                   toY - headlen * Math.sin(angle - Math.PI / 6));
    context.lineTo(toX - headlen * Math.cos(angle + Math.PI / 6),
                   toY - headlen * Math.sin(angle + Math.PI / 6));
    context.lineTo(toX, toY);
    context.fillStyle = color;
    context.fill();
}

function redrawAnnotations() {
    annotations.forEach((ann) => {

        switch (ann.type) {
            case 'artifact' :
                context.beginPath();
                context.ellipse(ann.x, ann.y, ann.width, ann.height, 0, 0, Math.PI * 2);
                context.strokeStyle = "purple";
                context.lineWidth = 2;
                context.stroke();
                context.closePath();
                break;

            case 'eroded-head':
                // context.beginPath();
                // context.moveTo(ann.x, ann.y);
                // context.lineTo(ann.x + 20, ann.y - 10);
                // context.moveTo(ann.x, ann.y);
                // context.lineTo(ann.x + 20, ann.y + 10);
                // context.moveTo(ann.x, ann.y);
                // context.lineTo(ann.x + 40, ann.y);
                // context.strokeStyle = "green";
                // context.lineWidth = 2;
                drawArrow(ann.startX, ann.startY, ann.x, ann.y, "green");
                // context.stroke();
                // context.closePath();

                
                break;
            case 'missing-cell':
                context.beginPath();
                context.rect(ann.x, ann.y, ann.width, ann.height)
                context.strokeStyle = "yellow";
                context.lineWidth = 2;
                context.stroke();
                context.closePath();
                break;
            case 'short-tail':
                context.beginPath();
                context.ellipse(ann.x, ann.y, ann.width, ann.height, 0, 0, Math.PI * 2);
                context.strokeStyle = "blue";
                context.lineWidth = 2;
                context.stroke();
                context.closePath();
                break;
            case 'broken-tail':
                context.beginPath();
                context.ellipse(ann.x, ann.y, ann.width, ann.height, 0, 0, Math.PI * 2);
                context.strokeStyle = "red";
                context.lineWidth = 2;
                context.stroke();
                context.closePath();
                break;
        }
      
    });
  }

  function drawLive(x, y, width, height) {

    startX = startX;
    startY = startY;

    switch(currentTool) {

        case 'artifact':
            context.beginPath();
            context.ellipse(x, y, width, height, 0, 0, Math.PI * 2);
            context.strokeStyle = "purple";
            context.lineWidth = 2;
            context.stroke();
            context.closePath();
            break;
        case 'eroded-head':
            // context.beginPath();
            // context.moveTo(x, y);
            // // context.lineTo(x + 20, y - 10);
            // // context.moveTo(x, y);
            // // context.lineTo(x + 20, y + 10);
            // // context.moveTo(x, y);
            // // context.lineTo(x + 40, y);
            
            // context.strokeStyle = "green";
            // context.lineWidth = 2;
            // context.stroke();
            // context.closePath();
            drawArrow(startX, startY, x, y, "green");

            break;
        case 'missing-cell':
            context.beginPath();
            context.rect(x, y, width, height)
            context.strokeStyle = "yellow";
            context.lineWidth = 2;
            context.stroke();
            context.closePath();
            break;
        case 'short-tail':
            context.beginPath();
            context.ellipse(x, y, width, height, 0, 0, Math.PI * 2);
            context.strokeStyle = "blue";
            context.lineWidth = 2;
            context.stroke();
            context.closePath();
            break;
        case 'broken-tail':
            context.beginPath();
            context.ellipse(x, y, width, height, 0, 0, Math.PI * 2);
            context.strokeStyle = "red";
            context.lineWidth = 2;
            context.stroke();
            context.closePath();
            break;
    }

  }

  
