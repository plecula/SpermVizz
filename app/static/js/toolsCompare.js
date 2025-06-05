let currentTool = null;
let annotationsMap = {}; // separated annotations for canvases
let selectedCanvas = null;

function getContext() {
  if (!selectedCanvas) return null;
  return selectedCanvas.getContext("2d");
}

// pick canvas by pressing a button
document.querySelectorAll('.which-frame-btn').forEach(button => {
  button.addEventListener('click', () => {
    document.querySelectorAll('.which-frame-btn').forEach(btn => btn.classList.remove('selected'));
    button.classList.add('selected');

    const canvasId = button.getAttribute('data-canvas');
    selectedCanvas = document.getElementById(canvasId);

    // if first add empty map 
    if (!annotationsMap[canvasId]) {
      annotationsMap[canvasId] = [];
    }

    // redraw only for chosen canvas
    const context = getContext();
    if (context) {
      context.clearRect(0, 0, selectedCanvas.width, selectedCanvas.height);
      redrawAnnotations(context);
    }
  });
});

function selectTool(tool) {
  currentTool = tool;

  const context = getContext();
  if (!context) return;

  const canvasId = selectedCanvas.id;

  if (currentTool === 'clear-last') {
    annotationsMap[canvasId].pop();
    context.clearRect(0, 0, selectedCanvas.width, selectedCanvas.height);
    redrawAnnotations(context);
    currentTool = null;
  } 
  else if (currentTool === 'clear-all') {
    annotationsMap[canvasId].length = 0;
    context.clearRect(0, 0, selectedCanvas.width, selectedCanvas.height);
    redrawAnnotations(context);
    currentTool = null;
  }
}

let isDrawing = false;
let startX, startY;

document.querySelectorAll("canvas").forEach(c => {
  c.addEventListener("mousedown", (e) => {
    if (!currentTool || !selectedCanvas || c !== selectedCanvas) return;

    const rect = selectedCanvas.getBoundingClientRect();
    startX = e.clientX - rect.left;
    startY = e.clientY - rect.top;
    isDrawing = true;
  });

  c.addEventListener("mousemove", (e) => {
    if (!currentTool || !selectedCanvas || c !== selectedCanvas) return;

    const context = getContext();
    if (!context) return;

    const rect = selectedCanvas.getBoundingClientRect();
    const currentX = e.clientX - rect.left;
    const currentY = e.clientY - rect.top;

    context.clearRect(0, 0, selectedCanvas.width, selectedCanvas.height);
    redrawAnnotations(context);

    const width = Math.abs(currentX - startX);
    const height = Math.abs(currentY - startY);
    const centerX = (startX + currentX) / 2;
    const centerY = (startY + currentY) / 2;

    if (isDrawing) {
      drawLive(context, centerX, centerY, width / 2, height / 2);
    }
  });

  c.addEventListener("mouseup", (e) => {
    if (!isDrawing || !selectedCanvas || c !== selectedCanvas) return;

    const context = getContext();
    if (!context) return;

    const rect = selectedCanvas.getBoundingClientRect();
    const endX = e.clientX - rect.left;
    const endY = e.clientY - rect.top;

    const width = Math.abs(endX - startX);
    const height = Math.abs(endY - startY);
    const centerX = (startX + endX) / 2;
    const centerY = (startY + endY) / 2;

    const canvasId = selectedCanvas.id;

    annotationsMap[canvasId].push({
      type: currentTool,
      x: centerX,
      y: centerY,
      width: width / 2,
      height: height / 2,
      startX: startX,
      startY: startY,
      endX: endX,
      endY: endY,
      rotation: 0
    });

    context.clearRect(0, 0, selectedCanvas.width, selectedCanvas.height);
    redrawAnnotations(context);
    currentTool = null;
    isDrawing = false;
  });
});

// rotate last object
document.getElementById("rotationSlider").addEventListener("input", (e) => {
  const context = getContext();
  if (!context || !selectedCanvas) return;

  const canvasId = selectedCanvas.id;
  const angle = parseInt(e.target.value);

  if (annotationsMap[canvasId] && annotationsMap[canvasId].length > 0) {
    annotationsMap[canvasId][annotationsMap[canvasId].length - 1].rotation = angle * Math.PI / 180;
    context.clearRect(0, 0, selectedCanvas.width, selectedCanvas.height);
    redrawAnnotations(context);
  }
});

function redrawAnnotations(context) {
  const canvasId = selectedCanvas.id;
  const annotations = annotationsMap[canvasId] || [];

  annotations.forEach((ann) => {
    switch (ann.type) {
      case 'artifact':
        context.save();
        context.translate(ann.x, ann.y);
        context.rotate(ann.rotation);
        context.beginPath();
        context.ellipse(0, 0, ann.width, ann.height, 0, 0, Math.PI * 2);
        context.strokeStyle = "purple";
        context.lineWidth = 2;
        context.stroke();
        context.closePath();
        context.restore();
        break;

      case 'eroded-head':
        drawArrow(context, ann.startX, ann.startY, ann.x, ann.y, "green");
        break;

      case 'missing-cell':
        context.save();
        context.translate(ann.x, ann.y);
        context.rotate(ann.rotation);
        context.beginPath();
        context.rect(-ann.width, -ann.height, ann.width * 2, ann.height * 2);
        context.strokeStyle = "yellow";
        context.lineWidth = 2;
        context.stroke();
        context.closePath();
        context.restore();
        break;

      case 'short-tail':
        context.save();
        context.translate(ann.x, ann.y);
        context.rotate(ann.rotation);
        context.beginPath();
        context.ellipse(0, 0, ann.width, ann.height, 0, 0, Math.PI * 2);
        context.strokeStyle = "blue";
        context.lineWidth = 2;
        context.stroke();
        context.closePath();
        context.restore();
        break;

      case 'broken-tail':
        drawArrow(context, ann.startX, ann.startY, ann.x, ann.y, "red");
        break;
    }
  });
}

function drawLive(context, x, y, width, height) {
  switch (currentTool) {
    case 'artifact':
      context.beginPath();
      context.ellipse(x, y, width, height, 0, 0, Math.PI * 2);
      context.strokeStyle = "purple";
      context.lineWidth = 2;
      context.stroke();
      context.closePath();
      break;

    case 'eroded-head':
      drawArrow(context, startX, startY, x, y, "green");
      break;

    case 'missing-cell':
      context.beginPath();
      context.rect(startX, startY, (x - startX) * 2, (y - startY) * 2);
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
      drawArrow(context, startX, startY, x, y, "red");
      break;
  }
}

function drawArrow(context, fromX, fromY, toX, toY, color = "black") {
  const headlen = 10;
  const dx = toX - fromX;
  const dy = toY - fromY;
  const angle = Math.atan2(dy, dx);

  context.beginPath();
  context.moveTo(fromX, fromY);
  context.lineTo(toX, toY);
  context.strokeStyle = color;
  context.lineWidth = 2;
  context.stroke();

  context.beginPath();
  context.moveTo(toX, toY);
  context.lineTo(
    toX - headlen * Math.cos(angle - Math.PI / 6),
    toY - headlen * Math.sin(angle - Math.PI / 6)
  );
  context.lineTo(
    toX - headlen * Math.cos(angle + Math.PI / 6),
    toY - headlen * Math.sin(angle + Math.PI / 6)
  );
  context.lineTo(toX, toY);
  context.fillStyle = color;
  context.fill();

}

