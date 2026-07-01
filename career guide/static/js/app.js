

document.addEventListener('DOMContentLoaded', () => {
    
    // 1. TAB SWITCHING  
    const navItems = {
        'nav-assessment': document.getElementById('quiz-container'),
        'nav-roadmap': document.getElementById('roadmap-area'),
        'nav-jobs': document.getElementById('jobs-area')
    };
    const navButtons = document.querySelectorAll('.nav-item');
    const resultArea = document.getElementById('result-area');

    function switchTab(clickedId) {
        // Sabhi sections aur result area ko chhupao
        Object.values(navItems).forEach(sec => { if (sec) sec.style.display = 'none'; });
        if (resultArea) resultArea.style.display = 'none';
        
        // Sabhi buttons se active class hatao
        navButtons.forEach(btn => btn.classList.remove('active'));

        // Sirf clicked section ko dikhao
        if (navItems[clickedId]) {
            navItems[clickedId].style.display = 'block';
            const activeBtn = document.getElementById(clickedId);
            if (activeBtn) activeBtn.classList.add('active');
        }
    }

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.id));
    });

    // --- 2. QUIZ OPTION SELECTION ---
    document.querySelectorAll('.option-card').forEach(card => {
        card.addEventListener('click', function() {
            const step = this.closest('.step');
            step.querySelectorAll('.option-card').forEach(c => c.classList.remove('selected'));
            this.classList.add('selected');
            const radio = this.querySelector('input[type="radio"]');
            if (radio) radio.checked = true;
        });
    });

    //  3. NEXT BUTTON & QUIZ NAVIGATION
    const nextBtn = document.getElementById('next-btn');
    const steps = document.querySelectorAll('.step');

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            const activeStep = document.querySelector('.step.active');
            if (!activeStep) return;

            const selected = activeStep.querySelector('input:checked');

            if (!selected) {
                alert("Please select an option to continue!");
                return;
            }

            const stepNum = parseInt(activeStep.dataset.step);
            
            if (stepNum < steps.length) {
                // Move to Next Question
                activeStep.classList.remove('active');
                activeStep.style.display = 'none';
                
                const nextStep = document.querySelector(`[data-step="${stepNum + 1}"]`);
                if (nextStep) {
                    nextStep.classList.add('active');
                    nextStep.style.display = 'block';
                }
            } else {
                // Submit Quiz (Calling the function below)
                submitCareerTest();
            }
        });
    }

    //  4. CAREER TEST SUBMISSION (FIXED) 
async function submitCareerTest() {
    console.log("Submitting Assessment...");

    // Default scores ( baad mein isey dynamic kar )
   const totalScores = { technical: 0, creative: 0, analytical: 0 };

// Sabhi selected radio buttons ko scan karo
document.querySelectorAll('input[type="radio"]:checked').forEach(input => {
    const type = input.dataset.type; // HTML mein data-type="technical" hona chahiye
    if (type) totalScores[type] += 5; // Har sahi answer par 5 points
});

    try {
        const response = await fetch('/api/assessment', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scores: totalScores })
        });

        if (!response.ok) throw new Error("Server Error");

        const data = await response.json();

        //  FIXED IDs HERE 
        const roleEl = document.getElementById('res-role');    // Pehle 'result-role' tha
        const reasonEl = document.getElementById('res-reason'); // Pehle 'result-reason' tha
        const ytLinkEl = document.getElementById('res-yt');     // Pehle 'yt-roadmap' tha

        if(roleEl) roleEl.innerText = data.role;
        if(reasonEl) reasonEl.innerText = data.reason;
        
        if(ytLinkEl) {
            ytLinkEl.href = data.yt_link;
            ytLinkEl.style.display = "block"; // Link ensure karo ki dikhe
            console.log("YT Link updated to:", data.yt_link);
        }

        // UI Switch
        const quizContainer = document.getElementById('quiz-container');
        const resultArea = document.getElementById('result-area');

        if (quizContainer) quizContainer.style.display = 'none';
        if (resultArea) resultArea.style.display = 'block';

    } catch (error) {
        console.error("Test Error:", error);
        alert("Oops! The server connection failed.");
    } finally {
        if(testBtn) {
            testBtn.innerText = "Next Question";
            testBtn.disabled = false;
        }
    }
}
    // 5. ROADMAP GENERATION 
    const genBtn = document.getElementById('gen-btn');
    if (genBtn) {
        genBtn.onclick = async () => {
            const topicInput = document.getElementById('topic-input');
            const topic = topicInput.value.trim();

            if (!topic) {
                alert("At least write a topic first!");
                return;
            }

            genBtn.innerText = "Generating Roadmap...";
            genBtn.disabled = true;

            try {
                const response = await fetch('/api/roadmap', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ topic: topic })
                });

                const data = await response.json();

                document.getElementById('roadmap-box').style.display = 'block';
                document.getElementById('roadmap-content').innerHTML = `
                    <div class="roadmap-step"><strong>Phase 1:</strong> ${data.d1}</div>
                    <div class="roadmap-step"><strong>Phase 2:</strong> ${data.d2}</div>
                    <div class="roadmap-step"><strong>Phase 3:</strong> ${data.d3}</div>
                    <div class="roadmap-step"><strong>Phase 4:</strong> ${data.d4}</div>
                    <div class="roadmap-step"><strong>Phase 5:</strong> ${data.d5}</div>
                `;
                const ytBtn = document.getElementById('roadmap-yt');
if(ytBtn) {
    ytBtn.href = data.yt_link;
    ytBtn.style.display = 'block';
    ytBtn.innerText = "▶ Watch Step-by-Step Video Tutorial";
}
               

            } catch (error) {
                console.error("Roadmap Error:", error);
                alert("The roadmap couldn't be generated.");
            } finally {
                genBtn.innerText = "Generate My Plan";
                genBtn.disabled = false;
            }
        };
    }

    // --- 6. FEEDBACK MODAL & SUBMISSION (FIXED) ---
    const modal = document.getElementById('feedbackModal');
    const openBtn = document.getElementById('openFeedback') || document.getElementById('openFeedbackBtn'); 
    const closeBtn = document.getElementById('closeFeedback');
    const feedbackForm = document.getElementById('feedbackForm');

    if (openBtn && modal) openBtn.onclick = () => modal.style.display = 'flex';
    if (closeBtn && modal) closeBtn.onclick = () => modal.style.display = 'none';

    window.onclick = (event) => {
        if (modal && event.target == modal) modal.style.display = 'none';
    }

    // --- 5. FEEDBACK SUBMISSION LOGIC (JSON VERSION) ---

if (feedbackForm) {
    feedbackForm.onsubmit = async (e) => {
        e.preventDefault(); 
        
        const submitBtn = feedbackForm.querySelector('.submit-btn');
        const feedbackText = document.getElementById('feedbackText').value;
        
        // Agar rating radio buttons nahi mil rahe, toh default '5' bhej do
        const ratingInput = document.querySelector('input[name="rating"]:checked');
        const ratingValue = ratingInput ? ratingInput.value : '5';

        submitBtn.innerText = "Sending... 🚀";
        submitBtn.disabled = true;

        try {
            const response = await fetch('/submit_feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }, // YEH ZAROORI HAI
                body: JSON.stringify({ 
                    feedback_text: feedbackText, 
                    rating: ratingValue 
                })
            });

            // Flask se result check karo
            const result = await response.json(); 

            if (response.ok && result.status === "success") {
                alert("Thank you! Feedback Submitted  ✅");
                const modal = document.getElementById('feedbackModal');
                if (modal) modal.style.display = 'none';
                feedbackForm.reset();
            } else {
                alert("Error: " + (result.error || "Server issue"));
            }
        } catch (error) {
            console.error("Network Error:", error);
            alert("Connection error! Please check the server.");
        } finally {
            submitBtn.innerText = "Submit 🚀";
            submitBtn.disabled = false;
        }
    };
}
});