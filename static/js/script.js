// Global variables
let currentTab = 'text';
let uploadedImage = null;
let extractedEmailText = '';

// Create animated particles
function createParticles() {
    const container = document.getElementById('particles');
    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.width = Math.random() * 60 + 20 + 'px';
        particle.style.height = particle.style.width;
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.background = `rgba(255, 255, 255, ${Math.random() * 0.3})`;
        particle.style.animationDelay = Math.random() * 20 + 's';
        particle.style.animationDuration = (Math.random() * 10 + 15) + 's';
        container.appendChild(particle);
    }
}

// Tab switching
function switchTab(tab, event) {
    currentTab = tab;
    
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    if (tab === 'text') {
        document.getElementById('textTab').classList.add('active');
    } else {
        document.getElementById('imageTab').classList.add('active');
    }
    
    document.getElementById('result').style.display = 'none';
}

// Image Upload Handling
const imageInput = document.getElementById('imageInput');
const uploadArea = document.getElementById('uploadArea');
const imagePreview = document.getElementById('imagePreview');
const previewImg = document.getElementById('previewImg');

imageInput.addEventListener('change', handleImageSelect);

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleImageFile(files[0]);
    }
});

uploadArea.addEventListener('click', (e) => {
    if (e.target === uploadArea || e.target.classList.contains('upload-icon') || 
        e.target.classList.contains('upload-text') || e.target.classList.contains('upload-subtext')) {
        imageInput.click();
    }
});

function handleImageSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleImageFile(file);
    }
}

function handleImageFile(file) {
    if (!file.type.startsWith('image/')) {
        alert('Please upload a valid image file (JPG, PNG, JPEG)');
        return;
    }

    if (file.size > 5 * 1024 * 1024) {
        alert('File size must be less than 5MB');
        return;
    }

    uploadedImage = file;

    const reader = new FileReader();
    reader.onload = (e) => {
        previewImg.src = e.target.result;
        uploadArea.style.display = 'none';
        imagePreview.style.display = 'block';
        
        extractTextFromImage();
    };
    reader.readAsDataURL(file);
}

function extractTextFromImage() {
    const extractedTextDiv = document.getElementById('extractedText');
    extractedTextDiv.innerHTML = `
        <div class="scanner-status">
            <div class="spinner-small"></div> 
            Scanning email with OCR technology...
        </div>
    `;

    Tesseract.recognize(
        previewImg.src,
        'eng',
        {
            logger: (m) => {
                if (m.status === 'recognizing text') {
                    const progress = Math.round(m.progress * 100);
                    extractedTextDiv.innerHTML = `
                        <div class="scanner-status">
                            <div class="spinner-small"></div> 
                            Scanning... ${progress}%
                        </div>
                    `;
                }
            }
        }
    ).then(({ data: { text } }) => {
        if (text.trim()) {
            extractedEmailText = text.trim();
            extractedTextDiv.innerHTML = `
                <h5>✅ Text Extracted Successfully</h5>
                <p>${extractedEmailText}</p>
            `;
        } else {
            extractedTextDiv.innerHTML = `
                <div style="color: #ef4444;">
                    <h5>⚠️ No text detected</h5>
                    <p>Please upload a clearer image with visible text.</p>
                </div>
            `;
        }
    }).catch(err => {
        console.error('OCR Error:', err);
        extractedTextDiv.innerHTML = `
            <div style="color: #ef4444;">
                <h5>❌ Extraction Failed</h5>
                <p>Unable to extract text. Please try another image.</p>
            </div>
        `;
    });
}

function removeImage() {
    uploadedImage = null;
    extractedEmailText = '';
    imageInput.value = '';
    previewImg.src = '';
    uploadArea.style.display = 'block';
    imagePreview.style.display = 'none';
    document.getElementById('result').style.display = 'none';
}

function useSample(text) {
    document.getElementById('messageInput').value = text;
    document.querySelectorAll('.tab-btn')[0].click();
}

function clearInput() {
    document.getElementById('messageInput').value = '';
    document.getElementById('result').style.display = 'none';
}

async function classifyMessage() {
    let message = '';
    
    if (currentTab === 'text') {
        message = document.getElementById('messageInput').value.trim();
        if (!message) {
            alert('Please enter an email to analyze!');
            return;
        }
    } else {
        if (!extractedEmailText) {
            alert('Please upload an email screenshot and wait for text extraction!');
            return;
        }
        message = extractedEmailText;
    }

    document.getElementById('loading').style.display = 'block';
    document.getElementById('result').style.display = 'none';

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();

        if (data.error) {
            alert('Error: ' + data.error);
            document.getElementById('loading').style.display = 'none';
            return;
        }

        document.getElementById('loading').style.display = 'none';

        const isSpam = data.prediction === 'spam';
        const confidence = data.confidence;

        const resultDiv = document.getElementById('result');
        resultDiv.className = 'result ' + (isSpam ? 'spam' : 'ham');
        resultDiv.innerHTML = `
            <div class="result-header">
                <div class="result-icon">${isSpam ? '⚠️' : '✅'}</div>
                <div class="result-text">
                    <h3>${isSpam ? 'SPAM EMAIL DETECTED' : 'SAFE EMAIL'}</h3>
                    <p>${isSpam ? 'This email appears to be spam' : 'This email appears to be legitimate'}</p>
                </div>
            </div>
            <div class="confidence-bar">
                <div class="confidence-fill" style="width: ${confidence}%">
                    ${confidence.toFixed(1)}% Confidence
                </div>
            </div>
        `;
        resultDiv.style.display = 'block';

        loadStats();
        loadHistory();

    } catch (error) {
        console.error('Error:', error);
        alert('Failed to classify message. Please try again.');
        document.getElementById('loading').style.display = 'none';
    }
}

async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();

        document.getElementById('totalCount').textContent = data.total;
        document.getElementById('spamCount').textContent = data.spam;
        document.getElementById('hamCount').textContent = data.ham;

    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        const data = await response.json();

        const tbody = document.getElementById('historyBody');
        
        if (data.history.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="4" style="text-align: center; color: #999; padding: 30px;">
                        No emails analyzed yet. Start by entering an email above!
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = data.history.map(item => `
            <tr>
                <td>${item.message.substring(0, 80)}${item.message.length > 80 ? '...' : ''}</td>
                <td><span class="badge ${item.prediction}">${item.prediction.toUpperCase()}</span></td>
                <td>${item.confidence.toFixed(1)}%</td>
                <td>${item.timestamp}</td>
            </tr>
        `).join('');

    } catch (error) {
        console.error('Error loading history:', error);
    }
}

async function clearHistory() {
    if (!confirm('Are you sure you want to clear all history?')) {
        return;
    }

    try {
        await fetch('/api/clear', { method: 'DELETE' });
        loadStats();
        loadHistory();
    } catch (error) {
        console.error('Error clearing history:', error);
        alert('Failed to clear history');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    createParticles();
    loadStats();
    loadHistory();
});