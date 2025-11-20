# THIS SCRIPT BUILDS A PROFESSIONAL PDF.JS VIEWER
HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>MEDTRIX Reader</title>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">

    <style>
        :root { --primary: #0056b3; --bg: #f4f7f6; --text: #333; --sidebar: #fff; }
        [data-theme="dark"] { --primary: #bb86fc; --bg: #121212; --text: #e0e0e0; --sidebar: #1e1e1e; }
        
        * { box-sizing: border-box; }
        body { margin: 0; display: flex; height: 100vh; background: var(--bg); color: var(--text); font-family: sans-serif; overflow: hidden; }

        /* SIDEBAR (TOC) */
        #sidebar {
            width: 300px; background: var(--sidebar); border-right: 1px solid #ccc;
            display: flex; flex-direction: column; transition: transform 0.3s; z-index: 100;
        }
        .sidebar-header { padding: 15px; border-bottom: 1px solid #ccc; display: flex; align-items: center; gap: 10px; }
        .exit-btn { 
            background: #d32f2f; color: white; text-decoration: none; padding: 8px 12px; 
            border-radius: 5px; font-weight: bold; font-size: 0.9rem; display: block; text-align: center;
        }
        #toc-list { flex-grow: 1; overflow-y: auto; }
        .toc-item { padding: 12px 15px; border-bottom: 1px solid rgba(128,128,128,0.1); cursor: pointer; font-size: 0.9rem; display: flex; justify-content: space-between; }
        .toc-item:hover { background: rgba(128,128,128,0.1); }
        .toc-item.active { background: var(--primary); color: white; }
        .page-tag { font-size: 0.75rem; opacity: 0.7; background: rgba(0,0,0,0.1); padding: 2px 6px; border-radius: 4px; }

        /* MAIN AREA */
        #main { flex-grow: 1; display: flex; flex-direction: column; position: relative; }
        
        /* TOOLBAR */
        #toolbar {
            height: 50px; background: var(--sidebar); border-bottom: 1px solid #ccc;
            display: flex; align-items: center; justify-content: space-between; padding: 0 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .tool-group { display: flex; align-items: center; gap: 10px; }
        .icon-btn { 
            background: none; border: none; color: var(--text); font-size: 1.2rem; cursor: pointer; padding: 5px;
        }
        #page-display { font-weight: bold; font-variant-numeric: tabular-nums; }

        /* PDF CANVAS */
        #viewer-container { 
            flex-grow: 1; overflow: auto; background: #525659; 
            display: flex; justify-content: center; padding: 20px; position: relative;
        }
        canvas { box-shadow: 0 0 10px rgba(0,0,0,0.5); max-width: 100%; height: auto; }

        /* MOBILE TWEAKS */
        @media (max-width: 768px) {
            #sidebar { position: absolute; height: 100%; transform: translateX(-100%); box-shadow: 5px 0 15px rgba(0,0,0,0.5); }
            #sidebar.open { transform: translateX(0); }
            #menu-btn { display: block; }
        }
        @media (min-width: 769px) {
            #menu-btn { display: none; }
        }
        
        /* LOADING SPINNER */
        #loader { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white; font-size: 1.5rem; display: none; }
    </style>
</head>
<body>

<div id="sidebar">
    <div class="sidebar-header">
        <a href="resources.html" class="exit-btn">❌ Exit</a>
        <div style="font-weight:bold; font-size:0.9rem; flex-grow:1; text-align:center">Chapters</div>
        <button class="icon-btn" onclick="toggleSidebar()">✕</button>
    </div>
    <div id="toc-list"></div>
</div>

<div id="main">
    <div id="toolbar">
        <div class="tool-group">
            <button id="menu-btn" class="icon-btn" onclick="toggleSidebar()"><i class="fas fa-bars"></i></button>
            <span id="doc-title" style="font-weight:bold; overflow:hidden; white-space:nowrap; max-width:150px; text-overflow:ellipsis;">Loading...</span>
        </div>
        <div class="tool-group">
            <button class="icon-btn" onclick="changePage(-1)"><i class="fas fa-chevron-left"></i></button>
            <span id="page-display">0 / 0</span>
            <button class="icon-btn" onclick="changePage(1)"><i class="fas fa-chevron-right"></i></button>
        </div>
        <div class="tool-group">
             <button class="icon-btn" onclick="adjustZoom(0.2)"><i class="fas fa-search-plus"></i></button>
             <button class="icon-btn" onclick="adjustZoom(-0.2)"><i class="fas fa-search-minus"></i></button>
        </div>
    </div>
    
    <div id="viewer-container">
        <div id="loader"><i class="fas fa-spinner fa-spin"></i></div>
        <canvas id="the-canvas"></canvas>
    </div>
</div>

<script>
    // SETUP PDF.JS
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

    // STATE
    let pdfDoc = null;
    let pageNum = 1;
    let pageRendering = false;
    let pageNumPending = null;
    let scale = 1.5;
    const canvas = document.getElementById('the-canvas');
    const ctx = canvas.getContext('2d');

    // INITIALIZE
    const params = new URLSearchParams(window.location.search);
    const filename = decodeURIComponent(params.get('file'));
    const url = `materials/${filename}`;
    
    document.getElementById('doc-title').innerText = filename.replace('.pdf','');
    if(localStorage.getItem('medtrix-theme') === 'dark') document.documentElement.setAttribute('data-theme', 'dark');

    // LOAD PDF
    document.getElementById('loader').style.display = 'block';
    pdfjsLib.getDocument(url).promise.then(doc => {
        pdfDoc = doc;
        document.getElementById('page-display').innerText = `${pageNum} / ${pdfDoc.numPages}`;
        document.getElementById('loader').style.display = 'none';
        
        // Restore last read position
        const savedPage = localStorage.getItem('pos_' + filename);
        if(savedPage) pageNum = parseInt(savedPage);
        
        renderPage(pageNum);
        loadTOC();
    });

    // RENDER PAGE
    function renderPage(num) {
        pageRendering = true;
        pdfDoc.getPage(num).then(page => {
            const viewport = page.getViewport({scale: scale});
            canvas.height = viewport.height;
            canvas.width = viewport.width;

            const renderContext = {
                canvasContext: ctx,
                viewport: viewport
            };
            const renderTask = page.render(renderContext);

            renderTask.promise.then(() => {
                pageRendering = false;
                if (pageNumPending !== null) {
                    renderPage(pageNumPending);
                    pageNumPending = null;
                }
            });
        });

        // Update UI
        document.getElementById('page-display').innerText = `${num} / ${pdfDoc.numPages}`;
        localStorage.setItem('pos_' + filename, num);
        
        // Highlight TOC
        document.querySelectorAll('.toc-item').forEach(item => {
            item.classList.remove('active');
            if(parseInt(item.dataset.page) === num) item.classList.add('active');
        });
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

    function adjustZoom(delta) {
        scale += delta;
        if(scale < 0.5) scale = 0.5;
        renderPage(pageNum);
    }

    function toggleSidebar() {
        document.getElementById('sidebar').classList.toggle('open');
    }

    // LOAD TOC FROM JSON
    function loadTOC() {
        fetch('pdf_data.json')
            .then(r => r.json())
            .then(data => {
                const list = document.getElementById('toc-list');
                const items = data[filename] || [];
                
                if(items.length === 0) {
                    list.innerHTML = "<div style='padding:20px; opacity:0.6; text-align:center'>No Index Available</div>";
                    return;
                }

                items.forEach(item => {
                    const div = document.createElement('div');
                    div.className = 'toc-item';
                    div.dataset.page = item.page;
                    div.innerHTML = `<span>${item.title}</span> <span class="page-tag">${item.page}</span>`;
                    div.onclick = () => {
                        pageNum = item.page;
                        queueRenderPage(pageNum);
                        if(window.innerWidth < 768) toggleSidebar(); // Auto-close on mobile
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

print("✅ PDF.js Viewer Built Successfully!")