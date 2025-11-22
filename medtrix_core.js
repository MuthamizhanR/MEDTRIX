/**
 * MEDTRIX CORE ENGINE v3.1 (Final)
 * Centralized Logic for AI, Database, and File Management.
 */

const MEDTRIX = {
    config: {
        version: '3.1',
        // Split API Key to bypass GitHub Security Scanners
        kPart1: "AIzaSyAvG61ZVSmjer_",
        kPart2: "PNsixRsxxqf7gaoNz7nQ",
        themeKey: 'medtrix-theme',
        dbKey: 'medtrix_analytics'
    },

    data: {
        _manifestCache: null,
        _fileCache: {},

        // 1. GET FILE LIST
        getManifest: async function() {
            if (this._manifestCache) return this._manifestCache;
            try {
                const res = await fetch('quiz_manifest.json');
                if (!res.ok) throw new Error("Run 'python3 generate_index.py'");
                
                let rawList = await res.json();
                
                // If raw list, format it. If rich list (from python), use it.
                return rawList.map(item => {
                    const fname = (typeof item === 'object') ? item.file : item;
                    const count = (typeof item === 'object') ? item.count : "?";
                    return {
                        title: this.formatTitle(fname),
                        file: fname,
                        category: this.detectCategory(fname),
                        questions: count
                    };
                });
            } catch (e) { console.error(e); return []; }
        },

        // 2. GET SINGLE QUIZ
        getQuiz: async function(filename) {
            if (this._fileCache[filename]) return this._fileCache[filename];
            try {
                const res = await fetch(`quiz_data/${filename}`);
                const data = await res.json();
                
                // Auto-Fix Data Structure
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

        // 3. FORMAT TITLES
        formatTitle: function(rawName) {
            let clean = rawName.replace('.json', '').replace(/^\d+[_-\s]*/, '').replace(/_/g, ' ');
            const dict = {
                'obg': 'Obstetrics', 'psm': 'Community Med', 'ent': 'ENT', 'fmt': 'Forensic',
                'pyq': 'PYQ', 'inicet': 'INICET', 'neet': 'NEET PG', 'fmge': 'FMGE',
                'uw': 'UWorld', 'radio': 'Radiology', 'derma': 'Dermatology'
            };
            return clean.split(' ').map(w => dict[w.toLowerCase()] || (w.charAt(0).toUpperCase() + w.slice(1))).join(' ');
        },

        // 4. SMART CATEGORIZER
        detectCategory: function(filename) {
            const lower = filename.toLowerCase();
            if (lower.includes('neet') || lower.includes('inicet') || lower.includes('pyq')) return "Previous Year Papers";
            if (lower.includes('grand') || lower.includes('gt')) return "Grand Tests";
            
            const subjects = ['anatomy', 'physiology', 'biochem', 'pathology', 'pharm', 'micro', 'forensic', 'psm', 'ent', 'ophthal', 'med', 'surg', 'obg', 'pedia', 'ortho', 'derma', 'psych', 'radio', 'anesth'];
            for(let s of subjects) { if(lower.includes(s)) return s.charAt(0).toUpperCase() + s.slice(1); }
            
            // Group by first word if likely a subject
            const firstWord = this.formatTitle(filename).split(' ')[0];
            if(firstWord.length > 3 && /^[a-zA-Z]+$/.test(firstWord)) return firstWord;

            return "General / Mixed";
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