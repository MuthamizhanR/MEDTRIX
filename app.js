document.addEventListener("DOMContentLoaded", async () => {
  const SUBJECT_ID = "psychiatry"; // Default for demonstration

  let subjectData = null;
  let mcqData = null;

  async function loadData() {
    try {
      const subjectRes = await fetch(`data/subjects/${SUBJECT_ID}.json`);
      subjectData = await subjectRes.json();

      const mcqRes = await fetch(`data/mcqs/${SUBJECT_ID}.json`);
      mcqData = await mcqRes.json();

      initApp();
    } catch (err) {
      console.error("Failed to load data", err);
      document.getElementById('hero-title').textContent = "Error loading subject data.";
    }
  }

  function initApp() {
    renderHero();
    renderPillars();
    renderCrossPillarTable();
    renderCases();
    renderInterventions();
    renderSpeedReference();
    renderNetworkSVG();
  }

  function renderHero() {
    document.getElementById("hero-badge").textContent = `SUBJECT: ${subjectData.subject_id.toUpperCase()}`;
    document.getElementById("hero-title").textContent = subjectData.title;

    let totalPillars = subjectData.pillars.length;
    let totalSubModules = subjectData.pillars.reduce((acc, p) => acc + p.sub_modules.length, 0);
    let totalMCQs = mcqData.questions ? mcqData.questions.length : 0;
    let totalCases = subjectData.cases ? subjectData.cases.length : 0;

    // Collect unique CBME codes
    let cbmeSet = new Set();
    subjectData.pillars.forEach(p => p.cbme_codes.forEach(c => cbmeSet.add(c)));
    if (subjectData.cross_pillar) {
        subjectData.cross_pillar.forEach(cp => {
            if(cp.cbme) cbmeSet.add(cp.cbme);
        });
    }

    const stats = [
      { label: "Pillars", val: totalPillars },
      { label: "Sub-modules", val: totalSubModules },
      { label: "Questions", val: totalMCQs },
      { label: "Clinical Cases", val: totalCases },
      { label: "CBME", val: cbmeSet.size }
    ];

    const statsContainer = document.getElementById("telemetry");
    statsContainer.innerHTML = stats.map(s => `
      <div class="stat-item">
        <span class="stat-value">${s.val}</span>
        <span class="stat-label">${s.label}</span>
      </div>
    `).join("");
  }

  function renderPillars() {
    const grid = document.getElementById("pillars-grid");
    grid.innerHTML = subjectData.pillars.map(p => {
      const smChips = p.sub_modules.map(sm => `<span class="sm-chip" data-sm="${sm.id}" data-pillar="${p.id}">${sm.id}: ${sm.name}</span>`).join("");

      return `
        <div class="pillar-card" style="border-top: 4px solid ${p.color};" data-pillar="${p.id}">
          <h3 class="pillar-title" style="color: ${p.color};">${p.title}</h3>
          <div class="pillar-quote">"${p.quote}"</div>
          <div class="sub-modules">${smChips}</div>
          <div class="pillar-meta">
            <span>${p.mcq_count} MCQs</span>
            <span>${p.chapters} Ch</span>
            <span>Mastery: <span id="mastery-${p.id}">${p.mastery}%</span></span>
          </div>
        </div>
      `;
    }).join("");

    // Add click listeners to cards and chips
    document.querySelectorAll('.pillar-card').forEach(card => {
        card.addEventListener('click', (e) => {
            if(!e.target.classList.contains('sm-chip')) {
                openQuizOverlay(card.dataset.pillar);
            }
        });
    });

    document.querySelectorAll('.sm-chip').forEach(chip => {
        chip.addEventListener('click', (e) => {
            e.stopPropagation();
            openQuizOverlay(chip.dataset.pillar, chip.dataset.sm);
        });
    });
  }

  function renderCrossPillarTable() {
    if (!subjectData.cross_pillar) return;

    const tbody = document.getElementById("cross-pillar-body");
    tbody.innerHTML = subjectData.cross_pillar.map(cp => {
      const isCertifiable = cp.certifiable;
      const rowClass = isCertifiable ? 'certifiable' : '';
      const certBadge = isCertifiable ? '<mark>CERTIFIABLE</mark>' : '';
      const pillars = cp.pillars.map(pid => {
          const p = subjectData.pillars.find(x => x.id === pid);
          return p ? `<span class="pill" style="background:${p.color}">${p.id}</span>` : pid;
      }).join(" ");

      const checked = localStorage.getItem(`cert_${cp.id}`) === 'true' ? 'checked' : '';

      return `
        <tr class="${rowClass}">
          <td>${cp.competency} ${certBadge}</td>
          <td><code>${cp.cbme || 'N/A'}</code></td>
          <td>${pillars}</td>
          <td>
            ${isCertifiable ? `<input type="checkbox" class="cert-toggle" data-cpid="${cp.id}" ${checked}> Verify` : '-'}
          </td>
        </tr>
      `;
    }).join("");

    document.querySelectorAll('.cert-toggle').forEach(chk => {
        chk.addEventListener('change', (e) => {
            localStorage.setItem(`cert_${e.target.dataset.cpid}`, e.target.checked);
        });
    });
  }

  function renderCases() {
    if (!subjectData.cases) return;
    const grid = document.getElementById("cases-grid");

    // Group cases arbitrarily into chains of 2 for demo purposes
    let chains = [];
    for(let i=0; i<subjectData.cases.length; i+=2) {
        chains.push(subjectData.cases.slice(i, i+2));
    }

    grid.innerHTML = chains.map(chain => {
      const p = subjectData.pillars.find(x => x.id === chain[0].pillar_id);
      const color = p ? p.color : 'var(--line)';

      const stepsHtml = chain.map((step, idx) => `
        <div class="step">
          <div class="step-meta">${step.pillar_id.toUpperCase()} · ${step.sub_module_id.toUpperCase()}</div>
          <div class="step-text">${step.step}</div>
        </div>
      `).join("");

      return `
        <div class="chain" style="border-left: 4px solid ${color};">
          <div class="steps-container">
            ${stepsHtml}
          </div>
        </div>
      `;
    }).join("");
  }

  function renderInterventions() {
    if (!subjectData.interventions) return;
    const grid = document.getElementById("rx-grid");

    grid.innerHTML = subjectData.interventions.map(rx => {
      const pills = rx.pillars.map(pid => {
          const p = subjectData.pillars.find(x => x.id === pid);
          return p ? `<span class="pill" style="background:${p.color}">${p.id}</span>` : pid;
      }).join("");

      return `
        <div class="rx-card">
          <div class="rx-name">${rx.name}</div>
          <div class="rx-mech">${rx.mechanism}</div>
          <div class="rx-pillars">${pills}</div>
        </div>
      `;
    }).join("");
  }

  function renderSpeedReference() {
    const grid = document.getElementById("speed-grid");
    grid.innerHTML = subjectData.pillars.map(p => {
      if(!p.speed_reference) return "";

      const listItems = p.speed_reference.map(item => `<li>${item}</li>`).join("");
      return `
        <div class="speed-card" style="border-top: 3px solid ${p.color};">
          <h3>${p.title} Speed Ref</h3>
          <ol>${listItems}</ol>
          <div class="op-rules"><strong>Operating Rule:</strong> ${p.operating_rules}</div>
        </div>
      `;
    }).join("");
  }

  // === SVG Hub-and-Spoke Network Logic ===
  function renderNetworkSVG() {
    const container = document.getElementById("network-container");
    const numPillars = subjectData.pillars.length;

    if(numPillars === 0) {
        container.innerHTML = "<p>No pillars to display in network.</p>";
        return;
    }

    const cx = 470;
    const cy = 300;
    const radius = 200; // Distance of nodes from center

    let svgHtml = `
      <svg class="network" viewBox="0 0 940 620" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <radialGradient id="hubGrad" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#3a3a5c" />
            <stop offset="100%" stop-color="#16162a" />
          </radialGradient>
        </defs>
    `;

    const nodes = [];
    const angleStep = (2 * Math.PI) / numPillars;

    // Calculate node positions
    for (let i = 0; i < numPillars; i++) {
        const p = subjectData.pillars[i];
        // Start at top (-PI/2)
        const angle = (i * angleStep) - (Math.PI / 2);
        const x = cx + radius * Math.cos(angle);
        const y = cy + radius * Math.sin(angle);
        nodes.push({ ...p, x, y });
    }

    // Draw lines from hub to nodes
    nodes.forEach(node => {
        svgHtml += `<line x1="${cx}" y1="${cy}" x2="${node.x}" y2="${node.y}" stroke="#2b2b42" stroke-width="1.3" />`;
    });

    // Optionally draw cross-pillar lines based on cross_pillar data
    if(subjectData.cross_pillar) {
        subjectData.cross_pillar.forEach(cp => {
            if(cp.pillars.length >= 2) {
                const n1 = nodes.find(n => n.id === cp.pillars[0]);
                const n2 = nodes.find(n => n.id === cp.pillars[1]);
                if(n1 && n2) {
                    svgHtml += `<line x1="${n1.x}" y1="${n1.y}" x2="${n2.x}" y2="${n2.y}" stroke="#4a4a70" stroke-width="1.5" stroke-dasharray="5,5" class="cp-line" data-cpid="${cp.id}" style="cursor:pointer;" />`;
                }
            }
        });
    }

    // Draw Hub
    svgHtml += `<circle cx="${cx}" cy="${cy}" r="74" fill="url(#hubGrad)" stroke="#4a4a70" stroke-width="2" />`;
    svgHtml += `<text x="${cx}" y="${cy}" fill="#fff" text-anchor="middle" dominant-baseline="middle" font-family="var(--serif)" font-size="20">${subjectData.subject_id.toUpperCase()}</text>`;

    // Draw Pillar Nodes
    nodes.forEach(node => {
        svgHtml += `
          <g class="network-node" data-pillar="${node.id}" style="cursor: pointer;" transform="translate(${node.x}, ${node.y})">
            <circle cx="0" cy="0" r="46" fill="#14141f" stroke="${node.color}" stroke-width="2.5" />
            <text x="0" y="0" fill="${node.color}" text-anchor="middle" dominant-baseline="middle" font-family="var(--mono)" font-size="14" font-weight="bold">${node.id}</text>
          </g>
        `;
    });

    svgHtml += `</svg>`;
    container.innerHTML = svgHtml;

    // Add interactions
    document.querySelectorAll('.network-node').forEach(node => {
        node.addEventListener('click', () => {
            openQuizOverlay(node.dataset.pillar);
        });
    });

    document.querySelectorAll('.cp-line').forEach(line => {
        line.addEventListener('click', (e) => {
            // Highlight cross-pillar table row (simple scroll for now)
            const cpid = e.target.dataset.cpid;
            const cb = document.querySelector(`.cert-toggle[data-cpid="${cpid}"]`);
            if(cb) {
                cb.scrollIntoView({behavior: 'smooth', block: 'center'});
                cb.closest('tr').style.backgroundColor = 'var(--table-hover)';
                setTimeout(() => cb.closest('tr').style.backgroundColor = '', 2000);
            }
        });
        line.addEventListener('mouseenter', (e) => e.target.setAttribute('stroke', '#fff'));
        line.addEventListener('mouseleave', (e) => e.target.setAttribute('stroke', '#4a4a70'));
    });
  }

  // === Quiz Overlay & Engine ===
  const overlay = document.getElementById("overlay");
  const overlayBody = document.getElementById("overlay-body");
  const closeBtn = document.getElementById("close-overlay");

  closeBtn.addEventListener("click", () => {
      overlay.classList.remove("active");
  });

  function openQuizOverlay(pillarId, subModuleId = null) {
      if(!mcqData || !mcqData.questions) {
          overlayBody.innerHTML = "<h3>No questions available.</h3>";
          overlay.classList.add("active");
          return;
      }

      let qs = mcqData.questions.filter(q => q.pillar_id === pillarId);
      if(subModuleId) {
          qs = qs.filter(q => q.sub_module_id === subModuleId);
      }

      if(qs.length === 0) {
          overlayBody.innerHTML = `<h3>No questions available for ${subModuleId ? subModuleId : pillarId}.</h3>`;
          overlay.classList.add("active");
          return;
      }

      // Render the first question for demo
      renderQuestion(qs[0]);
      overlay.classList.add("active");
  }

  function renderQuestion(q) {
      const attemptsKey = `q_${q.id}_attempts`;
      let attempts = parseInt(localStorage.getItem(attemptsKey) || '0');

      let html = `
          <h2>MEDTRIX Filtered Session</h2>
          <div class="pill" style="background:var(--p1)">${q.pillar_id}</div>
          <span class="sm-chip">${q.sub_module_id}</span>
          <span class="sm-chip">CBME: ${q.cbme}</span>

          <div class="quiz-container" data-qid="${q.id}">
              <div class="quiz-question">${q.question}</div>
              <div class="quiz-options">
                  ${q.options.map((opt, idx) => `<div class="quiz-option" data-idx="${idx}">${opt}</div>`).join("")}
              </div>
              <div class="quiz-explanation" id="expl-${q.id}">${q.explanation}</div>
          </div>
      `;
      overlayBody.innerHTML = html;

      const opts = overlayBody.querySelectorAll('.quiz-option');
      opts.forEach(opt => {
          opt.addEventListener('click', (e) => {
              if(overlayBody.querySelector('.correct')) return; // already answered

              const selectedIdx = parseInt(e.target.dataset.idx);
              const isCorrect = selectedIdx === q.answer;

              attempts++;
              localStorage.setItem(attemptsKey, attempts);

              if(isCorrect) {
                  e.target.classList.add('correct');
                  updateMastery(q.pillar_id, true);
              } else {
                  e.target.classList.add('incorrect');
                  opts[q.answer].classList.add('correct');
                  updateMastery(q.pillar_id, false);
              }
              document.getElementById(`expl-${q.id}`).style.display = 'block';
          });
      });
  }

  function updateMastery(pillarId, isCorrect) {
      const masteryKey = `mastery_${pillarId}`;
      let m = parseFloat(localStorage.getItem(masteryKey) || '0');
      // Simple logic: +5% for correct, -2% for wrong, clamp 0-100
      if(isCorrect) m = Math.min(100, m + 5);
      else m = Math.max(0, m - 2);

      localStorage.setItem(masteryKey, m);

      const display = document.getElementById(`mastery-${pillarId}`);
      if(display) {
          display.textContent = `${Math.round(m)}%`;
      }

      // Update in memory so it persists if re-rendered
      const p = subjectData.pillars.find(x => x.id === pillarId);
      if(p) p.mastery = Math.round(m);
  }

  // Boot
  loadData();
});