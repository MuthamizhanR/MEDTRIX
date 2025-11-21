# THIS SCRIPT BUILDS THE "CINEMA MODE" PDF VIEWER
# FEATURES: Full Width, Floating Zoom, Reliable Mobile Sidebar

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>MEDTRIX Reader</title>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">

    <style>
        /* --- VARIABLES --- */
        :root {
            --bg-dark: #1a1a1a;
            --bg-panel: #252525;
            --primary: #3b82f6;
            --text-light: #e5e5e5;
            --text-dim: #a3a3a3;
            --border: #404040;
        }

        * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; margin: 0; padding: 0; }
        
        body { 
            background-color: var(--bg-dark); 
            font-family: 'Inter', sans-serif; 
            height: 100vh; width: 100vw; 
            overflow: hidden; /* Prevent body scroll, handle in container */
            display: flex; flex-direction: column;
        }

        /* --- TOP BAR (Slim & Dark) --- */
        #toolbar {
            height: 50px; 
            background: var(--bg-panel); 
            border-bottom: 1px solid var(--border);
            display: flex; align-items: center; justify-content: space-between; 
            padding: 0 15px;
            flex-shrink: 0; z-index: 50;
        }

        .title-group { display: flex; align-items: center; gap: 15px; overflow: hidden; }
        
        #doc-title { 
            color: var(--text-light); font-size: 0.9rem; font-weight: 600; 
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 200px;
        }

        .btn {
            background: none; border: none; color: var(--text-light); 
            font-size: 1.1rem; padding: 8px; cursor: pointer;
            border-radius: 8px; transition: background 0.2s;
        }
        .btn:hover { background: rgba(255,255,255,0.1); }

        .exit-btn {
            background: #ef4444; color: white; font-size: 0.8rem; 
            padding: 6px 12px; text-decoration: none; border-radius: 4px; font-weight: 600;
        }

        /* --- SIDEBAR OVERLAY --- */
        #sidebar {
            position: absolute; top: 50px; left: 0; bottom: 0;
            width: 280px; background: var(--bg-panel);
            border-right: 1px solid var(--border);
            transform: translateX(-100%);
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            z-index: 1000; /* Always on top */
            display: flex; flex-direction: column;
            box-shadow: 5px 0 15px rgba(0,0,0,0.5);
        }
        
        #sidebar.open { transform: translateX(0); }

        /* Overlay backdrop for mobile */
        #sidebar-overlay {
            position: absolute; top: 50px; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.5); z-index: 900;
            display: none; backdrop-filter: blur(2px);
        }
        #sidebar-overlay.active { display: block; }

        .sidebar-header { padding: 15px; font-weight: bold; color: var(--text-dim); border-bottom: 1px solid var(--border); }
        #toc-list { flex-grow: 1; overflow-y: auto; }
        
        .toc-item {
            padding: 12px 15px; color: var(--text-light); border-bottom: 1px solid rgba(255,255,255,0.05);
            font-size: 0.9rem; cursor: pointer; display: flex; justify-content: space-between;
        }
        .toc-item:hover { background: rgba(255,255,255,0.05); }
        .toc-item.active { border-left: 4px solid var(--primary); background: rgba(59, 130, 246, 0.1); }
        .page-num { opacity: 0.5; font-size: 0.8rem; }

        /* --- PDF CONTAINER --- */
        #viewer-container {
            flex-grow: 1;
            overflow: auto; /* This allows scrolling */
            background: #121212; /* Dark background for contrast */
            display: flex; 
            justify-content: center; /* Center Horizontally */
            padding: 0; /* REMOVED PADDING to fix useless space */
            position: relative;
        }

        canvas {
            display: block;
            margin: 0 auto; /* Center */
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            /* CRITICAL: Allow canvas to scale naturally */
            max-width: none; 
        }

        /* --- FLOATING CONTROLS (Bottom Right) --- */
        .floating-controls {
            position: absolute; bottom: 20px; right: 20px;
            display: flex; flex-direction: column; gap: 10px;
            z-index: 800;
        }
        
        .fab {
            width: 50px; height: 50px; border-radius: 50%;
            background: var(--primary); color: white;
            border: none; font-size: 1.2rem;
            box-shadow: 0 4px 10px rgba(0,0,0,0.4);
            cursor: pointer; display: flex; align-items: center; justify-content: center;
        }
        .fab:active { transform: scale(0.95); }
        
        .page-indicator {
            position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%);
            background: rgba(0,0,0,0.7); color: white;
            padding: 6px 16px; border-radius: 20px; font-size: 0.85rem;
            z-index: 800; pointer-events: none;
        }

        /* --- CUTE CAT LOADER --- */
        #loader { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; color: white; }
        .cat-icon { font-size: 3rem; color: var(--primary); animation: bounce 0.6s infinite alternate; }
        @keyframes bounce { from { transform: translateY(0); } to { transform: translateY(-20px); } }

    </style>
</head>
<body>

<div id="toolbar">
    <div class="title-group">
        <button class="btn" onclick="toggleSidebar()"><i class="fas fa-bars"></i></button>
        <span id="doc-title">Loading...</span>
    </div>
    <a href="resources.html" class="exit-btn">Exit</a>
</div>

<div id="sidebar-overlay" onclick="toggleSidebar()"></div>
<div id="sidebar">
    <div class="sidebar-header">Table of Contents</div>
    <div id="toc-list"></div>
</div>

<div id="viewer-container">
    <div id="loader">
        <div class="cat-icon"><i class="fas fa-cat"></i></div>
        <div style="margin-top:10px; font-size:0.8rem; opacity:0.7">Fetching...</div>
    </div>
    <canvas id="the-canvas"></canvas>
</div>

<div class="page-indicator" id="page-pill">Loading</div>

<div class="floating-controls">
    <button class="fab" onclick="changeZoom(0.2)"><i class="fas fa-plus"></i></button>
    <button class="fab" onclick="changeZoom(-0.2)"><i class="fas fa-minus"></i></button>
    <button class="fab" style="background:#444" onclick="changePage(-1)"><i class="fas fa-arrow-up"></i></button>
    <button class="fab" style="background:#444" onclick="changePage(1)"><i class="fas fa-arrow-down"></i></button>
</div>

<script>
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

    let pdfDoc = null;
    let pageNum = 1;
    let pageRendering = false;
    let pageNumPending = null;
    let scale = 1.0; 
    let canvas = document.getElementById('the-canvas');
    let ctx = canvas.getContext('2d');
    
    // URL Params
    const params = new URLSearchParams(window.location.search);
    const filename = decodeURIComponent(params.get('file'));
    document.getElementById('doc-title').innerText = filename.replace('.pdf', '').replace(/_/g, ' ');

    // Load PDF
    const url = `materials/${filename}`;
    
    pdfjsLib.getDocument(url).promise.then(doc => {
        pdfDoc = doc;
        document.getElementById('loader').style.display = 'none';
        
        // RESTORE LAST PAGE
        const savedPage = localStorage.getItem('pos_' + filename);
        if(savedPage) pageNum = parseInt(savedPage);

        // INITIAL "FIT WIDTH" CALCULATION
        pdfDoc.getPage(pageNum).then(page => {
            const viewportRaw = page.getViewport({scale: 1.0});
            const containerWidth = document.getElementById('viewer-container').clientWidth;
            
            // Calculate scale to fit width perfectly (subtracting tiny buffer)
            scale = containerWidth / viewportRaw.width;
            
            renderPage(pageNum);
        });
        
        loadTOC();
        updateUI();
    });

    function renderPage(num) {
        pageRendering = true;
        
        pdfDoc.getPage(num).then(page => {
            const viewport = page.getViewport({scale: scale});
            canvas.height = viewport.height;
            canvas.width = viewport.width;

            const renderContext = { canvasContext: ctx, viewport: viewport };
            const renderTask = page.render(renderContext);

            renderTask.promise.then(() => {
                pageRendering = false;
                if (pageNumPending !== null) {
                    renderPage(pageNumPending);
                    pageNumPending = null;
                }
            });
        });

        // Save Position
        localStorage.setItem('pos_' + filename, num);
        updateUI();
    }

    function queueRenderPage(num) {
        if (pageRendering) pageNumPending = num;
        else renderPage(num);
    }

    function changePage(offset) {
        if (pageNum + offset >= 1 && pageNum + offset <= pdfDoc.numPages) {
            pageNum += offset;
            queueRenderPage(pageNum);
        }
    }

    function changeZoom(delta) {
        scale += delta;
        if (scale < 0.2) scale = 0.2; // Prevent disappearing
        renderPage(pageNum);
    }

    function updateUI() {
        if(pdfDoc) {
            document.getElementById('page-pill').innerText = `${pageNum} / ${pdfDoc.numPages}`;
            // Highlight TOC
            document.querySelectorAll('.toc-item').forEach(item => {
                item.classList.remove('active');
                if(parseInt(item.dataset.page) === pageNum) item.classList.add('active');
            });
        }
    }

    // SIDEBAR LOGIC
    function toggleSidebar() {
        document.getElementById('sidebar').classList.toggle('open');
        document.getElementById('sidebar-overlay').classList.toggle('active');
    }

    function loadTOC() {
        fetch('pdf_data.json').then(r => r.json()).then(data => {
            const list = document.getElementById('toc-list');
            const items = data[filename] || [];
            if(items.length === 0) { list.innerHTML = "<div style='padding:20px; opacity:0.5'>No Index</div>"; return; }
            
            items.forEach(item => {
                const div = document.createElement('div');
                div.className = 'toc-item';
                div.dataset.page = item.page;
                div.innerHTML = `<span>${item.title}</span> <span class="page-num">${item.page}</span>`;
                div.onclick = () => { 
                    pageNum = item.page; 
                    queueRenderPage(pageNum); 
                    toggleSidebar(); // Close on click
                };
                list.appendChild(div);
            });
        });
    }
</script>
</body>
</html>
"""

with open("viewer.html", "w", encoding="utf-8") as f:
    f.write(HTML_CONTENT)

print("✅ CINEMA MODE VIEWER BUILT")