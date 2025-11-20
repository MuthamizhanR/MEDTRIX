import os

OUTPUT_FILE = "revision.html"

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MEDTRIX | Active Recall</title>
    <style>
        :root { --primary: #6200ea; --bg: #f3e5f5; --card-bg: #ffffff; --text: #333; }
        [data-theme="dark"] { --primary: #b388ff; --bg: #121212; --card-bg: #1e1e1e; --text: #e0e0e0; }

        body { font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; }
        .container { max-width: 700px; margin: 0 auto; padding-bottom: 100px; }

        header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
        h1 { margin: 0; font-size: 1.5rem; color: var(--primary); }
        .back-btn { text-decoration: none; color: var(--text); font-weight: bold; border: 1px solid var(--text); padding: 8px 15px; border-radius: 20px; }

        /* FLASHCARD STYLES */
        .flashcard {
            background: var(--card-bg); border-radius: 15px; padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1); text-align: center;
            min-height: 200px; display: flex; flex-direction: column; justify-content: center; align-items: center;
            transition: transform 0.3s; cursor: pointer; position: relative;
        }
        .flashcard:hover { transform: translateY(-5px); }
        
        .card-content { font-size: 1.2rem; font-weight: 500; line-height: 1.6; }
        .card-label { 
            position: absolute; top: 15px; left: 15px; font-size: 0.8rem; 
            text-transform: uppercase; letter-spacing: 1px; opacity: 0.5; font-weight: bold;
        }
        .tap-hint { margin-top: 20px; font-size: 0.9rem; opacity: 0.5; }

        /* ANSWER REVEAL */
        .answer-area { 
            display: none; margin-top: 20px; padding-top: 20px; 
            border-top: 1px solid rgba(128,128,128,0.2); width: 100%; 
        }
        .answer-text { font-size: 1rem; opacity: 0.9; margin-bottom: 20px; }

        /* CONTROLS */
        .controls { 
            display: none; gap: 10px; justify-content: center; width: 100%; 
        }
        .rate-btn {
            flex: 1; padding: 15px; border: none; border-radius: 12px; 
            font-weight: bold; font-size: 1rem; cursor: pointer; color: white;
            transition: transform 0.1s;
        }
        .rate-btn:active { transform: scale(0.95); }
        
        .btn-again { background: #d50000; } /* < 1 min */
        .btn-hard { background: #ff9100; }  /* 2 days */
        .btn-good { background: #00c853; }  /* 4 days */
        .btn-easy { background: #2962ff; }  /* 7 days */

        /* LIST VIEW (For Overview) */
        .deck-stats { text-align: center; margin-bottom: 20px; opacity: 0.7; }
        #deck-list { margin-top: 40px; }
        .list-item { 
            padding: 15px; border-bottom: 1px solid rgba(128,128,128,0.1); 
            display: flex; justify-content: space-between; font-size: 0.9rem; 
        }
    </style>
</head>
<body>

<div class="container">
    <header>
        <a href="index.html" class="back-btn">← Home</a>
        <h1>🧠 Active Recall</h1>
    </header>

    <div id="review-mode">
        <div class="deck-stats" id="queue-status">Loading deck...</div>
        
        <!-- THE CARD -->
        <div class="flashcard" id="activeCard" onclick="revealAnswer()">
            <div class="card-label" id="cardSource">Source</div>
            <div class="card-content" id="cardQuestion">...</div>
            <div class="tap-hint">Tap to show answer</div>
            
            <div class="answer-area" id="cardAnswerArea">
                <div class="answer-text" id="cardAnswer"></div>
                <div class="controls">
                    <button class="rate-btn btn-again" onclick="rateCard('again', event)">Again<br><span style="font-size:0.7em">1m</span></button>
                    <button class="rate-btn btn-hard" onclick="rateCard('hard', event)">Hard<br><span style="font-size:0.7em">2d</span></button>
                    <button class="rate-btn btn-good" onclick="rateCard('good', event)">Good<br><span style="font-size:0.7em">4d</span></button>
                    <button class="rate-btn btn-easy" onclick="rateCard('easy', event)">Easy<br><span style="font-size:0.7em">7d</span></button>
                </div>
            </div>
        </div>
    </div>

    <div id="empty-mode" style="display:none; text-align:center; padding:50px;">
        <h2>🎉 All caught up!</h2>
        <p>You have reviewed all due cards for today.</p>
        <button onclick="resetDeck()" style="margin-top:20px; padding:10px 20px; background:transparent; border:1px solid var(--text); color:var(--text); border-radius:20px; cursor:pointer;">Reset & Review All</button>
    </div>
</div>

<script>
    // THEME
    if(localStorage.getItem('medtrix-theme') === 'dark') document.documentElement.setAttribute('data-theme', 'dark');

    // STATE
    let dueCards = [];
    let currentCard = null;

    // LOAD CARDS
    function loadDeck() {
        dueCards = [];
        const NOW = new Date().getTime();
        const DAY = 24 * 60 * 60 * 1000;

        for(let i=0; i<localStorage.length; i++) {
            const key = localStorage.key(i);
            if(!key.startsWith('srs_')) continue;
            
            try {
                let data = JSON.parse(localStorage.getItem(key));
                // Default interval if missing
                if(!data.nextReview) data.nextReview = 0;
                
                // Check if due
                if(data.nextReview <= NOW) {
                    dueCards.push({ key, ...data });
                }
            } catch(e) { console.error("Corrupt card", key); }
        }

        // Sort by randomness to mix subjects
        dueCards.sort(() => Math.random() - 0.5);
        
        updateUI();
    }

    function updateUI() {
        if(dueCards.length === 0) {
            document.getElementById('review-mode').style.display = 'none';
            document.getElementById('empty-mode').style.display = 'block';
        } else {
            document.getElementById('review-mode').style.display = 'block';
            document.getElementById('empty-mode').style.display = 'none';
            document.getElementById('queue-status').innerText = `${dueCards.length} cards due today`;
            
            // Load first card
            currentCard = dueCards[0];
            renderCard(currentCard);
        }
    }

    function renderCard(card) {
        // Reset View
        document.getElementById('cardAnswerArea').style.display = 'none';
        document.querySelector('.tap-hint').style.display = 'block';
        document.querySelector('.controls').style.display = 'none'; // Hide buttons initially
        
        // Set Content
        document.getElementById('cardSource').innerText = card.source || 'Notes';
        document.getElementById('cardQuestion').innerText = card.text || 'Error loading text';
        
        // For now, answer is just "Self Evaluation" or notes if you added them
        // In the future, you can add an "Answer" field to the capture tool
        document.getElementById('cardAnswer').innerText = "Did you recall this correctly?";
    }

    function revealAnswer() {
        document.getElementById('cardAnswerArea').style.display = 'block';
        document.querySelector('.tap-hint').style.display = 'none';
        // Show buttons after a tiny delay for effect
        setTimeout(() => {
            document.querySelector('.controls').style.display = 'flex';
        }, 100);
    }

    function rateCard(rating, e) {
        e.stopPropagation(); // Prevent card flip click
        
        const NOW = new Date().getTime();
        const DAY = 24 * 60 * 60 * 1000;
        let interval = 0;

        // Simple SM-2 style Logic
        switch(rating) {
            case 'again': interval = 1 * 60 * 1000; break; // 1 min
            case 'hard':  interval = 2 * DAY; break;
            case 'good':  interval = 4 * DAY; break;
            case 'easy':  interval = 7 * DAY; break;
        }

        // Update Storage
        let data = JSON.parse(localStorage.getItem(currentCard.key));
        data.nextReview = NOW + interval;
        data.reviews = (data.reviews || 0) + 1;
        localStorage.setItem(currentCard.key, JSON.stringify(data));

        // Remove from current queue
        dueCards.shift();
        
        // If 'again', maybe push back to end of queue? 
        // For now, we just hide it until reload to keep it simple.
        
        updateUI();
    }

    function resetDeck() {
        // For testing: Reset all dates to NOW
        for(let i=0; i<localStorage.length; i++) {
            const key = localStorage.key(i);
            if(key.startsWith('srs_')) {
                let data = JSON.parse(localStorage.getItem(key));
                data.nextReview = 0;
                localStorage.setItem(key, JSON.stringify(data));
            }
        }
        loadDeck();
    }

    // Init
    loadDeck();

</script>
</body>
</html>
"""

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(HTML_CONTENT)

print(f"✅ Created {OUTPUT_FILE} (Active Recall Engine)")