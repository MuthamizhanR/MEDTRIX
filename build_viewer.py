# THIS SCRIPT BUILDS THE "MEDTRIX GLASS" PDF VIEWER WITH CUTE CAT LOADER
HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>MEDTRIX Reader</title>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">

    <style>
        /* --- THEME VARIABLES --- */
        :root {
            --primary: #0056b3; 
            --primary-light: #e3f2fd;
            --bg-app: #f0f4f8; 
            --bg-sidebar: #ffffff;
            --text-main: #1e293b;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        [data-theme="dark"] {
            --primary: #a78bfa;     /* Softer Purple for dark mode */
            --primary-light: rgba(139, 92, 246, 0.1);
            --bg-app: #0f172a;
            --bg-sidebar: #1e293b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border: #334155;
        }

        /* --- RESET & LAYOUT --- */
        * { box-sizing: border-box; outline: none; -webkit-tap-highlight-color: transparent; }
        body { 
            margin: 0; height: 100vh; background: var(--bg-app); color: var(--text-main); 
            font-family: 'Inter', sans-serif; display: flex; overflow: hidden;
        }

        /* --- SIDEBAR --- */
        #sidebar {
            width: 280px; background: var(--bg-sidebar); border-right: 1px solid var(--border);
            display: flex; flex-direction: column; z-index: 50;
            transition: margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1); flex-shrink: 0;
        }
        #sidebar.collapsed { margin-left: -280px; }
        
        .sidebar-header { padding: 20px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; }
        .brand-title { font-weight: 700; color: var(--primary); letter-spacing: -0.5px; }
        .exit-btn { 
            background: #ef4444; color: white; text-decoration: none; padding: 6px 14px; 
            border-radius: 50px; font-size: 0.85rem; font-weight: 600; 
        }
        #toc-list { flex-grow: 1; overflow-y: auto; padding: 10px; }
        
        .toc-item { 
            padding: 12px; margin-bottom: 4px; border-radius: 12px; cursor: pointer; 
            font-size: 0.9rem; color: var(--text-muted); display: flex; justify-content: space-between; 
            transition: all 0.2s;
        }
        .toc-item:hover { background: var(--bg-app); color: var(--primary); }
        .toc-item.active { background: var(--primary-light); color: var(--primary); font-weight: 600; }
        .page-tag { font-size: 0.7rem; opacity: 0.6; background: var(--border); padding: 2px 6px; border-radius: 6px; }

        /* --- MAIN AREA --- */
        #main { flex-grow: 1; display: flex; flex-direction: column; position: relative; min-width: 0; }
        
        #toolbar {
            height: 60px; background: var(--bg-sidebar); border-bottom: 1px solid var(--border);
            display: flex; align-items: center; justify-content: space-between; padding: 0 20px;
            box-shadow: var(--shadow); z-index: 40;
        }
        .icon-btn { 
            background: transparent; border: none; color: var(--text-muted); font-size: 1.1rem; 
            width: 40px; height: 40px; border-radius: 50%; cursor: pointer; 
            display: flex; align-items: center; justify-content: center; transition: 0.2s;
        }
        .icon-btn:hover { background: var(--bg-app); color: var(--primary); transform: scale(1.1); }

        #page-display { background: var(--bg-app); padding: 6px 12px; border-radius: 20px; font-weight: 600; font-size: 0.9rem; }
        #doc-title { font-weight: 600; font-size: 0.95rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 200px;}

        /* --- VIEWER & CUTE LOADER --- */
        #viewer-container { 
            flex-grow: 1; overflow: auto; background: var(--bg-app);
            display: flex; justify-content: center; padding: 20px; position: relative;
        }
        canvas { 
            box-shadow: var(--shadow); border-radius: 12px; background-color: white;
            max-width: 100%; height: auto !important; object-fit: contain;
        }

        /* --- THE CUTE CAT ANIMATION --- */
        #loader { 
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            text-align: center; display: none;
        }
        
        .cat-wrapper { position: relative; display: inline-block; }
        
        .cat-icon { 
            font-size: 3.5rem; color: var(--primary); 
            /* The Bounce */
            animation: cat-bounce 0.6s infinite alternate cubic-bezier(0.5, 0.05, 1, 0.5);
        }
        
        .paw-shadow {
            width: 40px; height: 10px; background: rgba(0,0,0,0.1);
            border-radius: 50%; margin: 0 auto;
            /* The Shadow Shrink */
            animation: shadow-scale 0.6s infinite alternate cubic-bezier(0.5, 0.05, 1, 0.5);
        }

        .loading-text { 
            margin-top: 15px; font-weight: 600; color: var(--text-muted); 
            font-size: 0.85rem; letter-spacing: 1px; text-transform: uppercase;
            animation: pulse 1.5s infinite;
        }

        @keyframes cat-bounce {
            0% { transform: translateY(0) rotate(0deg); }
            100% { transform: translateY(-25px) rotate(5deg); } /* Jump high! */
        }
        @keyframes shadow-scale {
            0% { transform: scale(1.2); opacity: 0.3; }
            100% { transform: scale(0.6); opacity: 0.1; } /* Shadow shrinks as cat goes up */
        }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }

        /* --- MOBILE --- */
        @media (max-width: 768px) {
            #sidebar { position: absolute; height: 100%; margin-left: 0; transform: translateX(-100%); box-shadow: 10px 0 20px rgba(0,0,0,0.2); }
            #sidebar.mobile-open { transform: translateX(0); }
            #sidebar.collapsed { margin-left: 0; } 
            #mobile-close-btn { display: block !important; }
            .zoom-controls { display: none; }
            #viewer-container { padding: 10px; }
            #doc-title { max-width: 100px; }
        }
    </style>
</head>
<body>

<div id="sidebar">
    <div class="sidebar-header">
        <a href="resources.html" class="exit-btn"><i class="fas fa-arrow-left"></i> Exit</a>
        <span class="brand-title">Index</span>
        <button class="icon-btn" onclick="toggleSidebar()" style="display:none; margin-left:auto" id="mobile-close-btn">✕</button>
    </div>
    <div id="toc-list"></div>
</div>

<div id="main">
    <div id="toolbar">
        <div class="tool-group">
            <button class="icon-btn" onclick="toggleSidebar()"><i class="fas fa-bars"></i></button>
            <span id="doc-title">Loading...</span>
        </div>
        <div class="tool-group">
            <button class="icon-btn" onclick="changePage(-1)"><i class="fas fa-chevron-left"></i></button>
            <span id="page-display">-- / --</span>
            <button class="icon-btn" onclick="changePage(1)"><i class="fas fa-chevron-right"></i></button>
        </div>
        <div class="tool-group zoom-controls">
             <button class="icon-btn" onclick="adjustZoom(0.2)"><i class="fas fa-search-plus"></i></button>
             <button class="icon-btn" onclick="adjustZoom(-0.2)"><i class="fas fa-search-minus"></i></button>
        </div>
    </div>
    
    <div id="viewer-container">
        <div id="loader">
            <div class="cat-wrapper">
                <div class="cat-icon"><i class="fas fa-cat"></i></div>
                <div class="paw-shadow"></div>
            </div>
            <div class="loading-text">Fetching Data...</div>
        </div>
        <canvas id="the-canvas"></canvas>
    </div>
</div>

<script>
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
    
    let pdfDoc = null;
    let pageNum = 1;
    let pageRendering = false;
    let pageNumPending = null;
    let scale = 1.2;
    
    const canvas = document.getElementById('the-canvas');
    const ctx = canvas.getContext('2d');
    const params = new URLSearchParams(window.location.search);
    const filename = decodeURIComponent(params.get('file'));
    const url = `materials/${filename}`;

    document.getElementById('doc-title').innerText = filename.replace('.pdf','').replace(/_/g, ' ');
    if(localStorage.getItem('medtrix-theme') === 'dark') document.documentElement.setAttribute('data-theme', 'dark');

    // SHOW CAT LOADER
    document.getElementById('loader').style.display = 'block';

    pdfjsLib.getDocument(url).promise.then(doc => {
        pdfDoc = doc;
        document.getElementById('loader').style.display = 'none'; // HIDE CAT
        
        const containerWidth = document.getElementById('viewer-container').clientWidth;
        if(containerWidth < 600) scale = (containerWidth - 40) / 600; 
        else scale = 1.3;

        const savedPage = localStorage.getItem('pos_' + filename);
        if(savedPage) pageNum = parseInt(savedPage);
        
        renderPage(pageNum);
        loadTOC();
        updatePageDisplay();
    }).catch(err => {
        document.querySelector('.loading-text').innerHTML = '<span style="color:#ef4444">Error: File Not Found</span>';
        document.querySelector('.cat-icon').style.color = '#ef4444';
        console.error(err);
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
                if (pageNumPending !== null) { renderPage(pageNumPending); pageNumPending = null; }
            });
        });
        localStorage.setItem('pos_' + filename, num);
        updatePageDisplay();
        updateTOCHighlight(num);
    }
    function queueRenderPage(num) { if (pageRendering) pageNumPending = num; else renderPage(num); }
    function changePage(offset) { if (pageNum + offset >= 1 && pageNum + offset <= pdfDoc.numPages) { pageNum += offset; queueRenderPage(pageNum); } }
    function adjustZoom(delta) { scale += delta; if(scale < 0.5) scale = 0.5; renderPage(pageNum); }
    function updatePageDisplay() { if(pdfDoc) document.getElementById('page-display').innerText = `${pageNum} / ${pdfDoc.numPages}`; }
    
    function toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        if (window.innerWidth < 768) sidebar.classList.toggle('mobile-open');
        else sidebar.classList.toggle('collapsed');
    }
    
    document.getElementById('main').addEventListener('click', () => {
        if (window.innerWidth < 768 && document.getElementById('sidebar').classList.contains('mobile-open')) toggleSidebar();
    });

    function loadTOC() {
        fetch('pdf_data.json').then(r => r.json()).then(data => {
            const list = document.getElementById('toc-list');
            const items = data[filename] || [];
            if(items.length === 0) { list.innerHTML = "<div style='padding:20px; opacity:0.5; text-align:center; font-size:0.9rem'>No Chapters Found</div>"; return; }
            items.forEach(item => {
                const div = document.createElement('div');
                div.className = 'toc-item';
                div.dataset.page = item.page;
                div.innerHTML = `<span>${item.title}</span> <span class="page-tag">${item.page}</span>`;
                div.onclick = () => { pageNum = item.page; queueRenderPage(pageNum); if(window.innerWidth < 768) toggleSidebar(); };
                list.appendChild(div);
            });
            updateTOCHighlight(pageNum);
        });
    }
    function updateTOCHighlight(current) {
        document.querySelectorAll('.toc-item').forEach(item => {
            item.classList.remove('active');
            if(parseInt(item.dataset.page) === current) item.classList.add('active');
        });
    }
</script>
</body>
</html>
"""

with open("viewer.html", "w", encoding="utf-8") as f:
    f.write(HTML_CONTENT)

print("✅ PDF.js Viewer Updated with CUTE CAT Loader!")