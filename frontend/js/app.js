// ─── API Base URL Detection ───────────────────────────────────────────────────
// • localhost:8000  → same-origin (FastAPI serves frontend)
// • localhost:3000  → cross-origin to localhost:8000 (separate dev server)
// • Render / prod   → same-origin (FastAPI serves everything)
const _host = window.location.hostname;
const _port = window.location.port;
const API_BASE =
    (_host === "localhost" || _host === "127.0.0.1") && _port !== "8000"
        ? "http://localhost:8000"   // local dev with separate frontend server
        : "";                       // same-origin (Render prod or local :8000)

// ─── Global fetch wrapper ─────────────────────────────────────────────────────
async function fetchJSON(url, options = {}) {
  const response = await fetch(url, options);
  return response;
}

// ─── Backend Wake-up Ping (handles Render free-tier cold starts) ──────────────
async function pingBackendUntilReady(maxRetries = 12, intervalMs = 5000) {
    const overlay = document.getElementById("wakeup-overlay");
    const wakeupMsg = document.getElementById("wakeup-message");
    if (overlay) overlay.style.display = "flex";

    for (let i = 1; i <= maxRetries; i++) {
        try {
            const res = await fetch(`${API_BASE}/api/internships/?role=ping`, { method: "GET" });
            if (res.ok || res.status === 404) {
                // Backend is alive
                if (overlay) overlay.style.display = "none";
                return true;
            }
        } catch (_) {
            // Still spinning up — keep waiting
        }
        if (wakeupMsg) {
            wakeupMsg.textContent = `Server is waking up… (${i}/${maxRetries}). This takes ~30 seconds on first visit.`;
        }
        await new Promise(r => setTimeout(r, intervalMs));
    }
    if (overlay) overlay.style.display = "none";
    return false;
}

// State Management variables
let activeTab = "upload";
let selectedFile = null;
let currentResumeId = null;
let currentAnalysisId = null;
let currentSessionId = null;
let interviewStatus = "inactive";

// DOM Elements cache
const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");
const fileDisplay = document.getElementById("file-display");
const selectedFileName = document.getElementById("selected-file-name");
const resumeText = document.getElementById("resume-text");
const targetRoleInput = document.getElementById("target-role");
const analyzeBtn = document.getElementById("analyze-btn");
const btnSpinner = document.getElementById("btn-spinner");
const topActionBar = document.getElementById("top-action-bar");

// Initialize Drag & Drop Bindings
if (dropZone) {
    dropZone.addEventListener("click", () => fileInput.click());
    
    // Highlight drop area when dragging over
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add('drag-active');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('drag-active');
        }, false);
    });

    // Handle dropped files
    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleSelectedFile(files[0]);
        }
    });

    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            handleSelectedFile(e.target.files[0]);
        }
    });
}

function handleSelectedFile(file) {
    if (file.type === "application/pdf" || file.name.endsWith(".pdf") || file.type === "text/plain" || file.name.endsWith(".txt")) {
        selectedFile = file;
        selectedFileName.textContent = file.name;
        fileDisplay.style.display = "flex";
        // Clear text box if file uploaded
        resumeText.value = "";
    } else {
        alert("Invalid file format. Please upload a PDF or TXT file.");
    }
}

function clearSelectedFile(event) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    selectedFile = null;
    fileInput.value = "";
    fileDisplay.style.display = "none";
}

// Tab switcher functionality
function switchTab(tabId) {
    const navItem = document.getElementById(`nav-${tabId}`);
    if (navItem.classList.contains("disabled")) return;

    // Remove active state from all items
    document.querySelectorAll(".nav-item").forEach(item => {
        item.classList.remove("active");
    });
    // Add active state to clicked item
    navItem.classList.add("active");

    // Hide all views
    document.querySelectorAll(".tab-view").forEach(view => {
        view.classList.remove("active");
        view.style.display = "none";
    });

    // Show selected view
    const targetView = document.getElementById(`view-${tabId}`);
    targetView.style.display = "block";
    
    // Micro-delay for transition animations
    setTimeout(() => {
        targetView.classList.add("active");
    }, 10);

    activeTab = tabId;

    // Update main text details
    const titleEl = document.getElementById("main-title");
    const subEl = document.getElementById("main-subtitle");

    switch(tabId) {
        case "upload":
            titleEl.textContent = "Smart Career Assistant";
            subEl.textContent = "Upload details or copy resume text to begin career intelligence analysis";
            break;
        case "dashboard":
            titleEl.textContent = "Candidate Profile Dashboard";
            subEl.textContent = "Structured breakdown of qualifications, education, and extracted skills";
            break;
        case "gaps":
            titleEl.textContent = "Skill Gap Assessment";
            subEl.textContent = "Comparison of qualifications against target job role criteria";
            break;
        case "roadmap":
            titleEl.textContent = "Personalized Learning Roadmap";
            subEl.textContent = "Sequenced syllabus with recommended study timelines";
            break;
        case "interview":
            titleEl.textContent = "Interactive Interview Coach";
            subEl.textContent = "Stateful mock developer interviews and real-time review evaluations";
            break;
        case "opportunities":
            titleEl.textContent = "Career Opportunities & Resources";
            subEl.textContent = "Curated internships and targeted skill-gap learning resources";
            break;
    }
}

// State unlocking
function unlockDashboard() {
    document.querySelectorAll(".nav-item").forEach(item => {
        item.classList.remove("disabled");
    });
    topActionBar.classList.remove("hidden");
}

// Reset App state
function resetApp() {
    clearSelectedFile(null);
    resumeText.value = "";
    targetRoleInput.value = "";
    currentResumeId = null;
    currentAnalysisId = null;
    currentSessionId = null;
    interviewStatus = "inactive";

    // Disable tab navigations
    document.querySelectorAll(".nav-item").forEach(item => {
        if (item.id !== "nav-upload") {
            item.classList.add("disabled");
        }
    });

    // Hide analyses blocks
    document.querySelectorAll(".analysis-panel").forEach(p => {
        p.style.display = "none";
    });

    topActionBar.classList.add("hidden");
    
    // Clear chat blocks
    document.getElementById("chat-messages-container").innerHTML = "";
    document.getElementById("interview-feedback-report").innerHTML = "";
    document.getElementById("interview-feedback-report").style.display = "none";
    document.getElementById("interview-feedback-placeholder").style.display = "flex";

    // Clear opportunities and reset subtabs
    const internshipsList = document.getElementById("internships-list-container");
    if (internshipsList) internshipsList.innerHTML = "";
    const ytList = document.getElementById("resource-category-youtube");
    if (ytList) ytList.innerHTML = "";
    const docList = document.getElementById("resource-category-documentation");
    if (docList) docList.innerHTML = "";
    const pracList = document.getElementById("resource-category-practice");
    if (pracList) pracList.innerHTML = "";

    switchTab("upload");
}

// Asynchronous execution Orchestrator
async function submitProfile() {
    const role = targetRoleInput.value.trim();
    if (!role) {
        alert("Please specify a target career position to run the analysis.");
        return;
    }

    const text = resumeText.value.trim();
    if (!selectedFile && !text) {
        alert("Please upload a resume file or paste raw resume text to analyze.");
        return;
    }

    // Toggle loading UI states
    analyzeBtn.disabled = true;
    btnSpinner.style.display = "block";

    try {
        let resumeData = null;

        // 1. Upload or Submit Text
        if (selectedFile) {
            const formData = new FormData();
            formData.append("file", selectedFile);
            
            const res = await fetchJSON(`${API_BASE}/api/resume/upload`, {
                method: "POST",
                body: formData
            });
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Failed to upload resume file.");
            }
            resumeData = await res.json();
        } else {
            const res = await fetchJSON(`${API_BASE}/api/resume/text`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: text })
            });
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Failed to process resume text.");
            }
            resumeData = await res.json();
        }

        currentResumeId = resumeData.id;
        
        // 2. Perform Career analysis
        const analysisRes = await fetchJSON(`${API_BASE}/api/analysis`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    resume_id: currentResumeId,
                    target_role: role
                })
            });
        if (!analysisRes.ok) {
            const err = await analysisRes.json();
            throw new Error(err.detail || "Failed to run career analysis.");
        }
        const analysisData = await analysisRes.json();
        currentAnalysisId = analysisData.id;

        // 3. Render Parsed details
        renderProfile(resumeData.parsed_profile);
        renderGapReport(analysisData);

        // 4. Load Roadmap
        await loadRoadmap(currentAnalysisId);

        // 4.5. Load Opportunities & Resources
        await loadOpportunities(analysisData.target_role, analysisData.skill_gaps);

        // 5. Start Interview Coach session
        await startInterviewSession(role, currentResumeId);

        // Success Transition
        unlockDashboard();
        switchTab("dashboard");

    } catch (error) {
        console.error(error);
        alert(`Error executing analysis: ${error.message}`);
    } finally {
        analyzeBtn.disabled = false;
        btnSpinner.style.display = "none";
    }
}

// Render DOM profile components
function renderProfile(profile) {
    if (!profile) return;
    
    document.getElementById("profile-name").textContent = profile.name || "Candidate Profile";
    document.getElementById("profile-email-text").textContent = profile.email || "Contact unspecified";
    document.getElementById("profile-summary-text").textContent = profile.summary || "Summary details...";

    // Skills lists
    const skillsContainer = document.getElementById("profile-skills-list");
    skillsContainer.innerHTML = "";
    if (profile.skills && profile.skills.length > 0) {
        profile.skills.forEach(skill => {
            const tag = document.createElement("span");
            tag.className = "skill-tag";
            tag.textContent = skill;
            skillsContainer.appendChild(tag);
        });
    } else {
        skillsContainer.innerHTML = `<span class="text-muted" style="font-size: 0.85rem;">No skills identified</span>`;
    }

    // Experience/Education items
    const listContainer = document.getElementById("history-timeline-list");
    listContainer.innerHTML = "";

    // Append Experience
    if (profile.experience && profile.experience.length > 0) {
        const header = document.createElement("div");
        header.className = "section-subtitle";
        header.textContent = "Employment History";
        listContainer.appendChild(header);

        profile.experience.forEach(exp => {
            const card = document.createElement("div");
            card.className = "history-card";
            card.innerHTML = `
                <div class="history-header">
                    <span class="history-title">${exp.role || 'Job Role'}</span>
                    <span class="history-duration">${exp.duration || ''}</span>
                </div>
                <div class="history-sub">${exp.company || 'Company Name'}</div>
                <p class="history-body">${exp.description || ''}</p>
            `;
            listContainer.appendChild(card);
        });
    }

    // Append Education
    if (profile.education && profile.education.length > 0) {
        const header = document.createElement("div");
        header.className = "section-subtitle";
        header.style.marginTop = "1.5rem";
        header.textContent = "Academic History";
        listContainer.appendChild(header);

        profile.education.forEach(edu => {
            const card = document.createElement("div");
            card.className = "history-card";
            card.style.borderLeftColor = "var(--secondary)";
            card.innerHTML = `
                <div class="history-header">
                    <span class="history-title">${edu.degree || 'Degree Qualification'}</span>
                    <span class="history-year">${edu.year || ''}</span>
                </div>
                <div class="history-sub">${edu.school || 'Academic Institution'}</div>
            `;
            listContainer.appendChild(card);
        });
    }
}

// Render Skill gaps gauge & lists
function renderGapReport(analysis) {
    if (!analysis) return;

    const score = analysis.overall_fit_score;
    document.getElementById("gap-score-text").textContent = `${score}%`;
    document.getElementById("gap-comparison-label").innerHTML = `Match score for <strong>${analysis.target_role}</strong> position.`;

    // Radial Circle progress update
    const progressCircle = document.getElementById("gap-progress-circle");
    const radius = 40;
    const circumference = 2 * Math.PI * radius; // ~251.2
    
    // Set dashoffset based on percentage
    const offset = circumference - (score / 100) * circumference;
    progressCircle.style.strokeDashoffset = offset;

    // Render Have list
    const haveContainer = document.getElementById("gap-skills-have");
    haveContainer.innerHTML = "";
    const current = analysis.current_skills || [];
    const required = analysis.required_skills || [];

    // Matched skills
    const matched = required.filter(skill => 
        current.some(c => c.toLowerCase() === skill.toLowerCase())
    );

    if (matched.length > 0) {
        matched.forEach(skill => {
            const badge = document.createElement("span");
            badge.className = "tag-badge have-badge";
            badge.textContent = skill;
            haveContainer.appendChild(badge);
        });
    } else {
        haveContainer.innerHTML = `<span class="text-muted" style="font-size: 0.75rem;">None matching.</span>`;
    }

    // Missing skills
    const missingContainer = document.getElementById("gap-skills-missing");
    missingContainer.innerHTML = "";
    const gaps = analysis.skill_gaps || [];
    
    if (gaps.length > 0) {
        gaps.forEach(skill => {
            const badge = document.createElement("span");
            badge.className = "tag-badge gap-badge";
            badge.textContent = skill;
            missingContainer.appendChild(badge);
        });
    } else {
        missingContainer.innerHTML = `<span class="text-muted" style="font-size: 0.75rem;">No missing gaps identified. Ready for hiring!</span>`;
    }

    // Recommendations text
    document.getElementById("gap-recommendations-text").textContent = analysis.recommendations || "Tactical feedback complete.";
}

// Fetch and render learning Roadmap
async function loadRoadmap(analysisId) {
    try {
        const res = await fetchJSON(`${API_BASE}/api/roadmap/analysis/${analysisId}`);
        if (!res.ok) throw new Error("Failed to load learning roadmap.");
        
        const data = await res.json();
        
        document.getElementById("roadmap-duration").textContent = data.estimated_duration || "N/A";
        
        const timeline = document.getElementById("roadmap-timeline-steps");
        timeline.innerHTML = "";

        if (data.steps && data.steps.length > 0) {
            data.steps.forEach(step => {
                const stepEl = document.createElement("div");
                stepEl.className = "timeline-step";
                
                // Construct skill tags inside step
                let skillsHtml = "";
                if (step.skills_learned && step.skills_learned.length > 0) {
                    step.skills_learned.forEach(skill => {
                        skillsHtml += `<span class="skill-tag" style="font-size:0.7rem; padding: 0.15rem 0.5rem;">${skill}</span>`;
                    });
                }

                stepEl.innerHTML = `
                    <div class="step-marker">${step.step_number}</div>
                    <div class="step-content">
                        <div class="step-header">
                            <h3 class="step-title">${step.topic}</h3>
                            <span class="step-duration">${step.duration}</span>
                        </div>
                        <p class="step-description">${step.description}</p>
                        <div class="step-skills">
                            <span class="step-skills-label">Skills focus:</span>
                            ${skillsHtml}
                        </div>
                    </div>
                `;
                timeline.appendChild(stepEl);
            });
        } else {
            timeline.innerHTML = `<p class="text-muted">No syllabus steps found.</p>`;
        }
    } catch (e) {
        console.error(e);
        document.getElementById("roadmap-timeline-steps").innerHTML = `<p class="text-muted">Error loading learning roadmap details.</p>`;
    }
}

// Initialize mock Interview session
async function startInterviewSession(role, resumeId) {
    try {
        const res = await fetchJSON(`${API_BASE}/api/interview/session`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    target_role: role,
                    resume_id: resumeId
                })
            });
        if (!res.ok) throw new Error("Failed to initialize mock coach session.");
        
        const sessionData = await res.json();
        currentSessionId = sessionData.id;
        interviewStatus = "active";

        document.getElementById("interview-coach-title").textContent = `Interviewer (${role})`;

        // Render welcoming coach question
        const container = document.getElementById("chat-messages-container");
        container.innerHTML = "";
        
        if (sessionData.messages && sessionData.messages.length > 0) {
            sessionData.messages.forEach(msg => {
                appendChatMessage(msg.sender, msg.message);
            });
        }
    } catch (e) {
        console.error(e);
        alert("Could not start mock interview session. Chat will be unavailable.");
    }
}

// Append bubble to chat viewport
function appendChatMessage(sender, text) {
    const container = document.getElementById("chat-messages-container");
    const msgEl = document.createElement("div");
    msgEl.className = `message ${sender}`; // sender is 'coach' or 'candidate'
    
    // Simple sanitization
    const escapedText = text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    
    // Format paragraph breaks
    const formattedText = escapedText.replace(/\n\n/g, "<br><br>").replace(/\n/g, "<br>");

    msgEl.innerHTML = `
        <div class="msg-bubble">${formattedText}</div>
        <div class="msg-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
    `;
    
    container.appendChild(msgEl);
    
    // Auto scroll container
    container.scrollTop = container.scrollHeight;
}

// Send chat message triggers
async function sendChatMessage() {
    const input = document.getElementById("chat-user-input");
    const text = input.value.trim();
    if (!text || !currentSessionId || interviewStatus !== "active") return;

    // Clear input
    input.value = "";
    
    // Append candidate message instantly
    appendChatMessage("candidate", text);

    try {
        const res = await fetchJSON(`${API_BASE}/api/interview/session/${currentSessionId}/message`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text })
            });
        if (!res.ok) throw new Error("Failed to transmit chat message.");
        
        const reply = await res.json();
        appendChatMessage(reply.sender, reply.message);
    } catch (e) {
        console.error(e);
        appendChatMessage("coach", "Error: My connection timed out. Please try sending that answer again.");
    }
}

function handleChatEnter(event) {
    if (event.key === "Enter") {
        sendChatMessage();
    }
}

// Conclude interview session and evaluate performance
async function endInterviewSession() {
    if (!currentSessionId || interviewStatus !== "active") return;

    if (!confirm("Are you sure you want to end this interview session? This will compile your feedback report.")) {
        return;
    }

    interviewStatus = "completed";
    
    // Show loading text in feedback panel
    const reportContainer = document.getElementById("interview-feedback-report");
    const placeholder = document.getElementById("interview-feedback-placeholder");
    placeholder.style.display = "none";
    reportContainer.style.display = "block";
    reportContainer.innerHTML = `<p class="text-muted">Analyzing your response history and generating report metrics. Please wait...</p>`;

    try {
        const res = await fetchJSON(`${API_BASE}/api/interview/session/${currentSessionId}/complete`, {
                method: "POST"
            });
        if (!res.ok) throw new Error("Failed to compile session evaluation.");
        
        const data = await res.json();
        
        // Helper markdown formatting
        reportContainer.innerHTML = parseFeedbackMarkdown(data.feedback);
        
        // Update coach status in top header bar
        document.querySelector(".coach-status").textContent = "Session Concluded";
        document.querySelector(".coach-status").style.color = "var(--text-muted)";
    } catch (e) {
        console.error(e);
        reportContainer.innerHTML = `<p class="text-danger">Failed to generate feedback assessment report.</p>`;
    }
}

// Minimalistic markdown-to-styled-HTML formatter for feedback summaries
function parseFeedbackMarkdown(markdownText) {
    if (!markdownText) return "";
    
    // Sanitize first
    let html = markdownText.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    
    // Headers e.g. ### Header
    html = html.replace(/^### (.*$)/gim, '<h3 style="font-family:var(--font-heading); margin-top:1.25rem; margin-bottom:0.5rem; color:var(--text-primary); border-bottom:1px solid rgba(255,255,255,0.04); padding-bottom:0.25rem;">$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2 style="font-family:var(--font-heading); margin-top:1.5rem; margin-bottom:0.5rem; color:var(--text-primary);">$1</h2>');
    
    // Bold tags e.g. **bold text**
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong style="color:var(--primary);">$1</strong>');
    
    // Unordered lists e.g. * list item
    html = html.replace(/^\* (.*$)/gim, '<li style="margin-left:1rem; margin-bottom:0.4rem; list-style-type:square; font-size:0.85rem; color:var(--text-secondary);">$1</li>');
    // Wrap lists in ul
    // Simple lookbehind and lookahead to wrap lists (heuristic regex)
    html = html.replace(/((?:<li.*?>.*?<\/li>\n?)+)/g, '<ul style="margin-bottom: 1rem;">$1</ul>');

    // Ordered lists e.g. 1. list item
    html = html.replace(/^\d+\.\s+(.*$)/gim, '<li style="margin-left:1rem; margin-bottom:0.4rem; list-style-type:decimal; font-size:0.85rem; color:var(--text-secondary);">$1</li>');
    // Wrap ordered lists in ol
    html = html.replace(/((?:<li style="[^"]*decimal.*?>.*?<\/li>\n?)+)/g, '<ol style="margin-bottom: 1rem;">$1</ol>');

    // Paragraph blocks
    // Split by double newline, wrap everything that isn't list or header in a paragraph
    const lines = html.split("<br><br>");
    const parsedLines = lines.map(line => {
        const trimmed = line.trim();
        if (!trimmed) return "";
        if (trimmed.startsWith("<h") || trimmed.startsWith("<ul") || trimmed.startsWith("<ol") || trimmed.startsWith("<li")) {
            return trimmed;
        }
        return `<p style="font-size:0.85rem; line-height:1.5; color:var(--text-secondary); margin-bottom:0.85rem;">${trimmed}</p>`;
    });
    
    return parsedLines.join("");
}

// Fetch and render Internships & Learning Resources
async function loadOpportunities(role, skillGaps) {
    try {
        // Fetch internships matching target role
        const internshipsUrl = `${API_BASE}/api/internships/?role=${encodeURIComponent(role)}`;
        const internshipsRes = await fetchJSON(internshipsUrl);
        const internships = await internshipsRes.json();

        // Fetch resources matching skill gaps
        const skillsParam = (skillGaps && skillGaps.length > 0) ? skillGaps.join(",") : "";
        const resourcesUrl = `${API_BASE}/api/resources/?skills=${encodeURIComponent(skillsParam)}`;
        const resourcesRes = await fetchJSON(resourcesUrl);
        if (!resourcesRes.ok) throw new Error("Failed to load learning resources.");
        const resources = await resourcesRes.json();

        // Render data to DOM
        renderOpportunities(role, internships, resources);
    } catch (e) {
        console.error("Error loading opportunities/resources:", e);
        document.getElementById("internships-list-container").innerHTML = `<p class="text-muted">Error loading internships.</p>`;
        document.getElementById("resource-category-youtube").innerHTML = `<p class="text-muted">Error loading resources.</p>`;
    }
}

function renderOpportunities(role, internships, resources) {
    // Render target role label
    document.getElementById("opportunities-target-role").textContent = role;

    // Render Internships
    const internshipsContainer = document.getElementById("internships-list-container");
    internshipsContainer.innerHTML = "";

    if (internships && internships.length > 0) {
        internships.forEach(item => {
            const card = document.createElement("div");
            card.className = "history-card";
            card.style.borderLeftColor = "var(--secondary)";
            card.style.marginBottom = "0.75rem";
            card.innerHTML = `
                <div class="history-header" style="display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem;">
                    <span class="history-title" style="font-size: 0.95rem; font-weight: 600; color: var(--text-primary);">${item.title}</span>
                    <a href="${item.link}" target="_blank" class="btn-primary" style="margin-top: 0; padding: 0.25rem 0.75rem; font-size: 0.75rem; border-radius: 6px; box-shadow: none; text-decoration: none; white-space: nowrap;">Apply Now</a>
                </div>
                <div class="history-sub" style="color: var(--primary); font-weight: 500; font-size: 0.85rem; margin-top: 0.25rem;">${item.company} &bull; <span style="color: var(--text-muted); font-weight: normal;">${item.location || 'Location unspecified'}</span></div>
                <p class="history-body" style="margin-top: 0.5rem; line-height: 1.4; color: var(--text-secondary); font-size: 0.8rem;">${item.description || ''}</p>
            `;
            internshipsContainer.appendChild(card);
        });
    } else {
        internshipsContainer.innerHTML = `<p class="text-muted" style="font-size: 0.85rem; text-align: center; padding: 1.5rem 0;">No matching internships found for "${role}" at the moment.</p>`;
    }

    // Render Resources by category (youtube, documentation, practice)
    const ytContainer = document.getElementById("resource-category-youtube");
    const docContainer = document.getElementById("resource-category-documentation");
    const pracContainer = document.getElementById("resource-category-practice");

    ytContainer.innerHTML = "";
    docContainer.innerHTML = "";
    pracContainer.innerHTML = "";

    let hasYt = false;
    let hasDoc = false;
    let hasPrac = false;

    if (resources && resources.length > 0) {
        resources.forEach(res => {
            const row = document.createElement("div");
            row.style.display = "flex";
            row.style.alignItems = "center";
            row.style.justifyContent = "space-between";
            row.style.background = "rgba(15, 23, 42, 0.25)";
            row.style.border = "1px solid var(--glass-border)";
            row.style.borderRadius = "var(--border-radius-md)";
            row.style.padding = "0.75rem 1rem";
            row.style.marginBottom = "0.75rem";
            row.innerHTML = `
                <div style="flex: 1; min-width: 0; margin-right: 1rem;">
                    <div style="font-size: 0.9rem; font-weight: 600; color: var(--text-primary); text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">${res.title}</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">Skill Focus: <span class="skill-tag" style="font-size: 0.65rem; padding: 0.1rem 0.4rem; vertical-align: middle;">${res.skill}</span></div>
                </div>
                <a href="${res.link}" target="_blank" class="btn-secondary" style="padding: 0.35rem 0.75rem; font-size: 0.75rem; text-decoration: none; border-radius: 6px; white-space: nowrap; cursor: pointer; display: inline-flex; align-items: center; gap: 0.25rem;">
                    View
                </a>
            `;

            if (res.type === "youtube") {
                ytContainer.appendChild(row);
                hasYt = true;
            } else if (res.type === "documentation") {
                docContainer.appendChild(row);
                hasDoc = true;
            } else if (res.type === "practice") {
                pracContainer.appendChild(row);
                hasPrac = true;
            }
        });
    }

    if (!hasYt) {
        ytContainer.innerHTML = `<p class="text-muted" style="font-size: 0.85rem; text-align: center; padding: 1.5rem 0;">No matching YouTube resources for your skill gaps.</p>`;
    }
    if (!hasDoc) {
        docContainer.innerHTML = `<p class="text-muted" style="font-size: 0.85rem; text-align: center; padding: 1.5rem 0;">No matching documentation links for your skill gaps.</p>`;
    }
    if (!hasPrac) {
        pracContainer.innerHTML = `<p class="text-muted" style="font-size: 0.85rem; text-align: center; padding: 1.5rem 0;">No matching practice platforms for your skill gaps.</p>`;
    }
}

// Sub-tab switching logic for resources
function switchResourceCategory(category) {
    // Hide all containers
    document.querySelectorAll(".resource-list-container").forEach(c => {
        c.style.display = "none";
        c.classList.remove("active-category");
    });

    // Remove active styles from all buttons
    document.querySelectorAll(".resource-subtabs button").forEach(b => {
        b.classList.remove("active");
        b.style.color = "var(--text-secondary)";
        b.style.fontWeight = "500";
    });

    // Show selected category container
    const selectedContainer = document.getElementById(`resource-category-${category}`);
    if (selectedContainer) {
        selectedContainer.style.display = "block";
        setTimeout(() => selectedContainer.classList.add("active-category"), 10);
    }

    // Set active style to clicked button
    const buttons = document.querySelectorAll(".resource-subtabs button");
    buttons.forEach(btn => {
        if (btn.getAttribute("onclick").includes(category)) {
            btn.classList.add("active");
            btn.style.color = "var(--primary)";
            btn.style.fontWeight = "600";
        }
    });
}

// ─── Auto wake-up backend on page load ────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
    pingBackendUntilReady();
});

