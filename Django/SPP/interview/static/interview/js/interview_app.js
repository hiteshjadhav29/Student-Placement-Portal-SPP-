/**
 * InterviewApp - Main Application Controller
 * Coordinates Setup, Intake Form, Live AI Studio, Body Tracking, Voice Engine, and Report Dashboard.
 */

document.addEventListener("DOMContentLoaded", () => {
    // UI Screen References
    const screens = {
        setup: document.getElementById("screen-setup"),
        studio: document.getElementById("screen-studio"),
        report: document.getElementById("screen-report")
    };

    // Elements
    const elements = {
        candidateNameInput: document.getElementById("candidate-name"),
        fieldOfStudySelect: document.getElementById("field-of-study"),
        targetRoleInput: document.getElementById("target-role"),
        experienceLevelSelect: document.getElementById("experience-level"),
        totalQuestionsSelect: document.getElementById("total-questions"),
        btnStartInterview: document.getElementById("btn-start-interview"),

        // Device Check
        videoPreview: document.getElementById("webcam-preview"),
        canvasOverlay: document.getElementById("hud-canvas"),
        micMeterBar: document.getElementById("mic-meter-bar"),

        // Studio Controls & HUD
        aiAvatar: document.getElementById("ai-avatar"),
        aiWaveform: document.getElementById("ai-waveform"),
        aiStatusBadge: document.getElementById("ai-status-badge"),
        questionBadge: document.getElementById("question-badge"),
        questionText: document.getElementById("question-text"),
        liveTranscriptText: document.getElementById("live-transcript-text"),
        
        btnRecordToggle: document.getElementById("btn-record-toggle"),
        btnSubmitAnswer: document.getElementById("btn-submit-answer"),
        btnSkipQuestion: document.getElementById("btn-skip-question"),
        btnRepeatQuestion: document.getElementById("btn-repeat-question"),

        // Telemetry Meters
        meterEyeContact: document.getElementById("meter-eye-contact"),
        valEyeContact: document.getElementById("val-eye-contact"),
        meterPosture: document.getElementById("meter-posture"),
        valPosture: document.getElementById("val-posture"),
        meterFidget: document.getElementById("meter-fidget"),
        valFidget: document.getElementById("val-fidget"),

        // Report Dashboard
        repName: document.getElementById("rep-candidate-name"),
        repField: document.getElementById("rep-field"),
        repRole: document.getElementById("rep-role"),
        repOverallScore: document.getElementById("rep-overall-score"),
        repBadgeVerdict: document.getElementById("rep-badge-verdict"),
        repDomainScore: document.getElementById("rep-domain-score"),
        repSpeechScore: document.getElementById("rep-speech-score"),
        repBodyScore: document.getElementById("rep-body-score"),
        repStructureScore: document.getElementById("rep-structure-score"),
        repVerdictText: document.getElementById("rep-verdict-text"),
        repStrengthsList: document.getElementById("rep-strengths-list"),
        repImprovementsList: document.getElementById("rep-improvements-list"),
        repQaContainer: document.getElementById("rep-qa-container"),

        btnRetakeInterview: document.getElementById("btn-retake")
    };

    // State Variables
    let currentSessionId = null;
    let currentQuestionNum = 1;
    let totalQuestions = 5;
    let currentQuestionText = "";
    let isSubmitting = false;

    // Tracker & Voice Engine instances
    let tracker = null;
    let voiceEngine = null;
    let waveAnimId = null;

    // Initialize Devices & Setup Screen
    async function initSetupScreen() {
        tracker = new BodyLanguageTracker(elements.videoPreview, elements.canvasOverlay);
        
        try {
            await tracker.initCamera();
            tracker.startTracking();
            startTelemetryUIUpdate();
        } catch (err) {
            alert("Camera access is required for body language tracking during mock interviews. Please allow camera access in your browser settings.");
        }

        voiceEngine = new VoiceEngine({
            onTranscriptUpdate: (text) => {
                elements.liveTranscriptText.textContent = text || "Listening for your response...";
            },
            onSpeechStart: () => {
                setAIState("speaking", "AI Interviewer Speaking...");
                startAvatarWaveform();
            },
            onSpeechEnd: () => {
                setAIState("listening", "AI Listening... Speak Your Answer");
                stopAvatarWaveform();
            },
            onError: (err) => {
                console.warn("Voice engine error:", err);
            }
        });
    }

    // Telemetry UI Updates (Eye Contact, Posture, Fidget)
    function startTelemetryUIUpdate() {
        setInterval(() => {
            if (tracker && tracker.isTracking) {
                const m = tracker.metrics;
                if (elements.meterEyeContact) elements.meterEyeContact.style.width = `${m.eyeContactPct}%`;
                if (elements.valEyeContact) elements.valEyeContact.textContent = `${m.eyeContactPct}%`;

                if (elements.meterPosture) elements.meterPosture.style.width = `${m.postureScore}%`;
                if (elements.valPosture) elements.valPosture.textContent = `${m.postureScore}%`;

                if (elements.meterFidget) elements.meterFidget.style.width = `${m.fidgetLevel}%`;
                if (elements.valFidget) elements.valFidget.textContent = `${m.fidgetLevel}%`;
            }
        }, 300);
    }

    // AI Avatar Waveform animation
    function startAvatarWaveform() {
        elements.aiAvatar.classList.add("speaking-pulse");
        const canvas = elements.aiWaveform;
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        canvas.width = canvas.parentElement.clientWidth || 300;
        canvas.height = 40;

        let phase = 0;
        function drawWave() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.strokeStyle = "#06b6d4";
            ctx.lineWidth = 2.5;
            ctx.beginPath();

            const cy = canvas.height / 2;
            for (let x = 0; x < canvas.width; x += 3) {
                const amp = Math.sin(x * 0.05 + phase) * 12 * Math.sin(phase * 0.5);
                const y = cy + amp;
                if (x === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.stroke();
            phase += 0.15;

            waveAnimId = requestAnimationFrame(drawWave);
        }
        drawWave();
    }

    function stopAvatarWaveform() {
        elements.aiAvatar.classList.remove("speaking-pulse");
        if (waveAnimId) {
            cancelAnimationFrame(waveAnimId);
            waveAnimId = null;
        }
        const canvas = elements.aiWaveform;
        if (canvas) {
            const ctx = canvas.getContext("2d");
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
    }

    function setAIState(state, text) {
        if (elements.aiStatusBadge) {
            elements.aiStatusBadge.className = `status-badge ${state}`;
            elements.aiStatusBadge.textContent = text;
        }
    }

    // Switch Screens
    function showScreen(screenKey) {
        Object.keys(screens).forEach(key => {
            if (screens[key]) {
                screens[key].classList.toggle("hidden", key !== screenKey);
            }
        });
    }

    // Event Listeners
    elements.btnStartInterview.addEventListener("click", async () => {
        const candidateName = elements.candidateNameInput.value.trim() || "Candidate";
        const fieldOfStudy = elements.fieldOfStudySelect.value;
        const targetRole = elements.targetRoleInput.value.trim() || "Software Engineer";
        const experienceLevel = elements.experienceLevelSelect.value;
        totalQuestions = parseInt(elements.totalQuestionsSelect.value, 10);

        elements.btnStartInterview.disabled = true;
        elements.btnStartInterview.innerHTML = `<span class="spinner"></span> Starting Session...`;

        try {
            const resp = await fetch("api/start-session/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    candidate_name: candidateName,
                    field_of_study: fieldOfStudy,
                    target_role: targetRole,
                    experience_level: experienceLevel,
                    total_questions: totalQuestions
                })
            });

            const data = await resp.json();
            if (data.success) {
                currentSessionId = data.session_id;
                currentQuestionNum = data.question.number;
                currentQuestionText = data.question.text;

                showScreen("studio");
                renderQuestion(data.question);
            } else {
                alert("Failed to start session: " + (data.error || "Unknown error"));
            }
        } catch (err) {
            console.error("API error:", err);
            alert("Failed to communicate with server.");
        } finally {
            elements.btnStartInterview.disabled = false;
            elements.btnStartInterview.innerHTML = `🚀 Start AI Interview`;
        }
    });

    function renderQuestion(questionObj) {
        currentQuestionNum = questionObj.number;
        currentQuestionText = questionObj.text;

        elements.questionBadge.textContent = `Question ${currentQuestionNum} of ${totalQuestions} • ${questionObj.type.toUpperCase()}`;
        elements.questionText.textContent = questionObj.text;
        elements.liveTranscriptText.textContent = "Click 'Start Speaking' or speak your answer...";

        // AI speaks question aloud
        voiceEngine.speak(questionObj.text, () => {
            // Auto start recording after AI finishes question
            startRecordingAnswer();
        });
    }

    function startRecordingAnswer() {
        voiceEngine.startListening();
        elements.btnRecordToggle.innerHTML = `🎙️ Stop Recording`;
        elements.btnRecordToggle.classList.add("recording");
    }

    function stopRecordingAnswer() {
        const transcript = voiceEngine.stopListening();
        elements.btnRecordToggle.innerHTML = `🎙️ Start Speaking`;
        elements.btnRecordToggle.classList.remove("recording");
        setAIState("idle", "Ready for Submission");
        return transcript;
    }

    elements.btnRecordToggle.addEventListener("click", () => {
        if (voiceEngine.isListening) {
            stopRecordingAnswer();
        } else {
            startRecordingAnswer();
        }
    });

    elements.btnRepeatQuestion.addEventListener("click", () => {
        voiceEngine.stopListening();
        voiceEngine.speak(currentQuestionText);
    });

    elements.btnSubmitAnswer.addEventListener("click", async () => {
        await submitCurrentAnswer();
    });

    elements.btnSkipQuestion.addEventListener("click", async () => {
        elements.liveTranscriptText.textContent = "(Candidate skipped this question)";
        await submitCurrentAnswer();
    });

    async function submitCurrentAnswer() {
        if (isSubmitting) return;
        isSubmitting = true;

        const transcript = stopRecordingAnswer() || elements.liveTranscriptText.textContent;
        voiceEngine.stopSpeaking();

        elements.btnSubmitAnswer.disabled = true;
        elements.btnSubmitAnswer.innerHTML = `<span class="spinner"></span> Processing...`;
        setAIState("thinking", "AI Evaluating Response...");

        const bodyMetrics = tracker ? tracker.metrics : { eyeContactPct: 80, postureScore: 85, fidgetLevel: 10, smileLevel: 40 };

        try {
            const resp = await fetch("api/next-question/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    session_id: currentSessionId,
                    question_number: currentQuestionNum,
                    response_text: transcript,
                    body_language: {
                        eye_contact_pct: bodyMetrics.eyeContactPct,
                        posture_score: bodyMetrics.postureScore,
                        fidget_level: bodyMetrics.fidgetLevel,
                        smile_level: bodyMetrics.smileLevel
                    }
                })
            });

            const data = await resp.json();

            if (data.is_completed) {
                // Interview finishes! Fetch full evaluation report
                await loadEvaluationReport();
            } else if (data.success) {
                renderQuestion(data.question);
            } else {
                alert("Error: " + data.error);
            }
        } catch (err) {
            console.error("Submission failed:", err);
            alert("Error sending answer to server.");
        } finally {
            isSubmitting = false;
            elements.btnSubmitAnswer.disabled = false;
            elements.btnSubmitAnswer.innerHTML = `Next Question ➔`;
        }
    }

    async function loadEvaluationReport() {
        setAIState("thinking", "Generating Final Report...");

        const aggregatedBody = tracker ? tracker.getAggregatedMetrics() : {};

        try {
            const resp = await fetch("api/evaluate-session/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    session_id: currentSessionId,
                    aggregated_body_language: aggregatedBody
                })
            });

            const data = await resp.json();
            if (data.success && data.report) {
                renderReport(data.report);
                showScreen("report");
            } else {
                alert("Failed to load report: " + (data.error || "Unknown"));
            }
        } catch (err) {
            console.error("Report load error:", err);
            alert("Error generating final evaluation report.");
        }
    }

    function renderReport(report) {
        elements.repName.textContent = report.candidate_name;
        elements.repField.textContent = report.field_of_study;
        elements.repRole.textContent = `${report.target_role} (${report.experience_level})`;

        elements.repOverallScore.textContent = `${report.overall_score}%`;
        
        let verdictClass = "verdict-good";
        let verdictBadge = "READY FOR INTERVIEWS";
        if (report.overall_score < 70) {
            verdictClass = "verdict-warn";
            verdictBadge = "NEEDS PRACTICE";
        } else if (report.overall_score >= 88) {
            verdictClass = "verdict-excellent";
            verdictBadge = "OUTSTANDING PERFORMANCE";
        }
        elements.repBadgeVerdict.className = `badge-verdict ${verdictClass}`;
        elements.repBadgeVerdict.textContent = verdictBadge;

        elements.repDomainScore.textContent = `${report.domain_score}%`;
        elements.repSpeechScore.textContent = `${report.speech_score}%`;
        elements.repBodyScore.textContent = `${report.body_language_score}%`;
        elements.repStructureScore.textContent = `${report.structure_score}%`;

        elements.repVerdictText.textContent = report.summary_verdict;

        // Render Strengths
        elements.repStrengthsList.innerHTML = report.strengths.map(s => `<li><span class="icon">✅</span> ${s}</li>`).join("");

        // Render Improvements
        elements.repImprovementsList.innerHTML = report.improvements.map(i => `<li><span class="icon">💡</span> ${i}</li>`).join("");

        // Render Question Breakdown
        elements.repQaContainer.innerHTML = report.qa_list.map(qa => `
            <div class="qa-card">
                <div class="qa-card-header">
                    <span class="qa-num">Q${qa.number} (${qa.type.toUpperCase()})</span>
                    <span class="qa-score-badge">Score: ${qa.rating}/100</span>
                </div>
                <div class="qa-question-text"><strong>Question:</strong> ${qa.question}</div>
                <div class="qa-response-text"><strong>Your Answer:</strong> "${qa.response}"</div>
                
                <div class="qa-metrics-grid">
                    <span>Eye Contact: ${qa.metrics.eye_contact}%</span>
                    <span>Posture: ${qa.metrics.posture}%</span>
                    <span>Fidget: ${qa.metrics.fidget}%</span>
                </div>

                <div class="qa-feedback-box">
                    <strong>AI Feedback:</strong> ${qa.feedback}
                </div>
                <div class="qa-model-box">
                    <strong>Model Answer Strategy:</strong> ${qa.suggested_answer}
                </div>
            </div>
        `).join("");

        // Announce final overall score via voice
        if (voiceEngine) {
            voiceEngine.speak(`Congratulations ${report.candidate_name}! Your interview evaluation is complete. Your overall score is ${report.overall_score} percent. Check out your detailed report below.`);
        }
    }

    elements.btnRetakeInterview.addEventListener("click", () => {
        showScreen("setup");
    });

    // Start setup screen on load
    initSetupScreen();
});
