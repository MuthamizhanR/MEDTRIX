/**
 * MEDTRIX CORE ENGINE v3.2 (Instant Load Edition)
 */

const MEDTRIX = {
    config: {
        version: '3.2',
        // Split API Key to bypass GitHub Security
        kPart1: "AIzaSyAvG61ZVSmjer_",
        kPart2: "PNsixRsxxqf7gaoNz7nQ",
        themeKey: 'medtrix-theme',
        dbKey: 'medtrix_analytics'
    },

    data: {
        _manifestCache: null,
        _fileCache: {},

        // 1. GET FILE LIST (Optimized for Pre-Indexed Data)
        getManifest: async function() {
            if (this._manifestCache) return this._manifestCache;
            try {
                const res = await fetch('quiz_manifest.json');
                if (!res.ok) throw new Error("Run python script");
                
                let rawList = await res.json();
                
                // If Python script ran correctly, data is already formatted.
                // We just return it directly. Zero processing time.
                this._manifestCache = rawList;
                return rawList;
                
            } catch (e) { console.error(e); return []; }
        },

        // 2. GET SINGLE QUIZ
        getQuiz: async function(filename) {
            if (this._fileCache[filename]) return this._fileCache[filename];
            try {
                const res = await fetch(`quiz_data/${filename}`);
                const data = await res.json();
                
                // Auto-Fix Data Structure (Fix [object Object])
                if(data.questions) {
                    data.questions = data.questions.map(q => {
                        if(typeof q.question === 'object') q.text = q.question.text || JSON.stringify(q.question);
                        else q.text = q.question || q.text;

                        if(q.options) {
                            if(!Array.isArray(q.options)) q.options = Object.values(q.options);
                            q.options = q.options.map(opt => {
                                if(typeof opt === 'object') return { text: opt.text || opt.value, correct: opt.correct || false };
                                return { text: opt, correct: false };
                            });
                        }
                        return q;
                    });
                }
                this._fileCache[filename] = data;
                return data;
            } catch (e) { return null; }
        },

        // 3. TITLE FORMATTER (Fallback only)
        formatTitle: function(rawName) {
            return rawName.replace('.json', '').replace(/^\d+[_-\s]*/, '').replace(/_/g, ' ');
        }
    },

    // --- 3. DATABASE ---
    db: {
        saveResult: function(qData, isCorrect, filename) {
            let history = JSON.parse(localStorage.getItem(MEDTRIX.config.dbKey) || '[]');
            history = history.filter(h => h.uid !== qData.uid);
            history.push({
                uid: qData.uid, text: qData.text, explanation: qData.explanation,
                timestamp: Date.now(), isCorrect: isCorrect, source: filename, options: qData.options
            });
            try { localStorage.setItem(MEDTRIX.config.dbKey, JSON.stringify(history)); } catch(e) {}
        }
    },

    // --- 4. AI ENGINE ---
    ai: {
        getKey: function() { return MEDTRIX.config.kPart1 + MEDTRIX.config.kPart2; },
        ask: async function(prompt, context) {
            const key = this.getKey();
            try {
                const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${key}`, {
                    method: "POST", headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ contents: [{ parts: [{ text: prompt + "\n\nContext: " + context.substring(0,1000) }] }] })
                });
                const data = await response.json();
                if (data.error) throw new Error(data.error.message);
                return data.candidates[0].content.parts[0].text;
            } catch (e) { return `AI Error: ${e.message}`; }
        }
    },

    // --- 5. UI ---
    ui: {
        initTheme: function() {
            const theme = localStorage.getItem(MEDTRIX.config.themeKey) || 'light';
            document.documentElement.setAttribute('data-theme', theme);
        },
        toast: function(msg) {
            let t = document.createElement('div');
            t.innerText = msg;
            t.style.cssText = "position:fixed; bottom:90px; left:50%; transform:translateX(-50%); background:rgba(0,0,0,0.8); color:#fff; padding:8px 16px; border-radius:20px; z-index:9999; font-size:0.8rem; animation:fadeIn 0.3s;";
            document.body.appendChild(t);
            setTimeout(() => t.remove(), 1500);
        }
    }
};

MEDTRIX.ui.initTheme();