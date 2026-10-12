document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadStatus = document.getElementById('upload-status');
    const resultsDashboard = document.getElementById('results-dashboard');
    const ctaButton = document.querySelector('.cta-button');

    if (ctaButton) {
        ctaButton.addEventListener('click', () => {
            document.getElementById('drop-zone').scrollIntoView({ behavior: 'smooth', block: 'center' });
            document.getElementById('drop-zone').click();
        });
    }
    
    // Drag and Drop Logic
    dropZone.addEventListener('click', () => fileInput.click());
    
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });
    
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            handleFile(fileInput.files[0]);
        }
    });
    
    async function handleFile(file) {
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            showStatus('Please upload a valid PDF file.', 'error');
            return;
        }
        
        showStatus('Uploading and analyzing your petition...', 'info');
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || `Analysis failed (${response.status}).`);
            }

            renderResults(data);
        } catch (error) {
            console.warn(error);
            showStatus(
                error instanceof Error
                    ? `Unable to analyze this petition: ${error.message}`
                    : 'Unable to analyze this petition. Please try again.',
                'error'
            );
        }
    }
    
    function showStatus(msg, type) {
        uploadStatus.textContent = msg;
        uploadStatus.className = `status-msg msg-${type}`;
        uploadStatus.style.display = 'block';
    }
    
    function renderResults(data) {
        uploadStatus.style.display = 'none';
        resultsDashboard.classList.remove('hidden');
        
        const exData = data.extracted_data;
        const causal = data.causal_inference;
        
        // Render Tags
        document.getElementById('ex-provisions').innerHTML = exData.provisions.map(p => `<span class="tag">${p}</span>`).join('');
        document.getElementById('ex-evidence').innerHTML = exData.evidence_markers.map(m => `<span class="tag">${m}</span>`).join('');
        
        // Sentiment
        const sentEl = document.getElementById('ex-sentiment');
        sentEl.textContent = exData.judicial_sentiment;
        if (exData.judicial_sentiment === 'Favorable') {
            sentEl.style.color = '#10b981';
            sentEl.style.borderColor = 'rgba(16, 185, 129, 0.3)';
            sentEl.style.background = 'rgba(16, 185, 129, 0.15)';
        } else if (exData.judicial_sentiment === 'Critical') {
            sentEl.style.color = '#ec4899';
            sentEl.style.borderColor = 'rgba(236, 72, 153, 0.3)';
            sentEl.style.background = 'rgba(236, 72, 153, 0.15)';
        }
        
        // Animate Score Circle
        setTimeout(() => {
            const scorePath = document.getElementById('score-circle-path');
            const scoreText = document.getElementById('score-text');
            const targetScore = causal.overall_strength_score;
            
            scorePath.setAttribute('stroke-dasharray', `${targetScore}, 100`);
            
            let currentStr = 0;
            const strInterval = setInterval(() => {
                if(currentStr >= targetScore) {
                    scoreText.textContent = targetScore + '%';
                    clearInterval(strInterval);
                } else {
                    currentStr++;
                    scoreText.textContent = currentStr + '%';
                }
            }, 15);
        }, 300);
        
        // Render Causal Logic Map
        const mapContainer = document.getElementById('logic-map');
        mapContainer.innerHTML = causal.causal_logic_map.map(factor => `
            <div class="logic-map-item slide-up">
                <div class="logic-impact">${factor.causal_effect}</div>
                <div class="logic-text">
                    <h5>${factor.marker}</h5>
                    <p>${factor.logic}</p>
                </div>
            </div>
        `).join('');
        
        // Timeline Matcher
        setTimeout(() => {
            const months = causal.estimated_duration_months;
            const maxMonths = 60; // 5 years baseline
            const percent = Math.min((months / maxMonths) * 100, 100);
            
            document.getElementById('timeline-progress').style.width = `${percent}%`;
            document.getElementById('timeline-text').textContent = `Estimated duration: ${months} months based on historical complexity data.`;
            
            // Re-trigger slide up animations for dynamically added map items
            document.querySelectorAll('.logic-map-item').forEach((item, idx) => {
                item.style.animationDelay = `${idx * 0.15}s`;
            });
        }, 500);
        
        // Scroll to results smoothly
        resultsDashboard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
});
