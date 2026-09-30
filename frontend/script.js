// ═══════════════════════════════════
// API URL - Our FastAPI backend address
// ═══════════════════════════════════

// This is where our FastAPI is running
const API_URL = 'http://localhost:8001';

// ═══════════════════════════════════
// CHECK API CONNECTION
// Runs as soon as page loads
// ═══════════════════════════════════

// window.onload = runs this function when page finishes loading
window.onload = async function() {
    await checkAPIConnection();
}

async function checkAPIConnection() {
    // Get the status bar element from HTML
    const statusEl = document.getElementById('api-status');
    
    try {
        // fetch sends a GET request to our API home route
        // await waits for the response before continuing
        const response = await fetch(`${API_URL}/`);
        
        if (response.ok) {
            // response.ok = true means API responded successfully
            statusEl.textContent = '✅ API Connected — System Ready';
            statusEl.className = 'status-connected';
        } else {
            throw new Error('API not responding');
        }
    } catch (error) {
        // If fetch fails (backend not running) show error
        statusEl.textContent = '❌ API Offline — Please start the backend';
        statusEl.className = 'status-error';
    }
}

// ═══════════════════════════════════
// TAB SWITCHING
// ═══════════════════════════════════

function showTab(tabName) {
    // Hide ALL tab contents first
    // querySelectorAll gets all elements with that class
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.add('hidden');
    });

    // Remove active class from ALL tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show only the selected tab
    document.getElementById(`${tabName}-tab`).classList.remove('hidden');

    // Find which button was clicked and make it active
    // event.target gives us the clicked element
    event.target.classList.add('active');
}

// ═══════════════════════════════════
// HELPER FUNCTION - Show Result
// Reused by all 3 features
// ═══════════════════════════════════

function showResult(elementId, type, message) {
    // Get the result box element
    const resultEl = document.getElementById(elementId);
    
    // Remove hidden class to make it visible
    resultEl.classList.remove('hidden');
    
    // Remove all previous result classes
    resultEl.classList.remove(
        'result-real', 
        'result-fake', 
        'result-error', 
        'result-loading'
    );
    
    // Add the correct class based on type
    resultEl.classList.add(`result-${type}`);
    
    // Set the message text
    resultEl.innerHTML = message;
}

// ═══════════════════════════════════
// FEATURE 1 - ANALYZE REVIEW
// ═══════════════════════════════════

async function analyzeReview() {
    // Get the review text from textarea
    const review = document.getElementById('review-input').value;
    
    // Check if user actually typed something
    if (!review.trim()) {
        showResult('review-result', 'error', '⚠️ Please enter a review first!');
        return;
    }
    
    // Show loading state while waiting for API
    showResult('review-result', 'loading', '⏳ Analyzing review...');
    
    // Disable button while loading
    // This prevents user from clicking multiple times
    const btn = event.target;
    btn.disabled = true;
    
    try {
        // Send POST request to our analyze-review route
        const response = await fetch(`${API_URL}/analyze-review`, {
            // method POST = we are sending data
            method: 'POST',
            headers: {
                // Tell API we are sending JSON data
                'Content-Type': 'application/json'
            },
            // body = the actual data we send
            // JSON.stringify converts JS object to JSON string
            body: JSON.stringify({ review: review })
        });
        
        // Parse the JSON response from API
        // response.json() converts JSON string back to JS object
        const data = await response.json();
        
        if (data.status === 'success') {
            // Build result message based on FAKE or REAL
            if (data.result === 'FAKE') {
                showResult('review-result', 'fake',
                    `❌ <strong>FAKE REVIEW DETECTED</strong><br>
                    Confidence: ${data.confidence}<br>
                    <small>This review shows signs of being computer generated</small>`
                );
            } else {
                showResult('review-result', 'real',
                    `✅ <strong>REAL REVIEW</strong><br>
                    Confidence: ${data.confidence}<br>
                    <small>This review appears to be genuine</small>`
                );
            }
        } else {
            showResult('review-result', 'error', `⚠️ Error: ${data.detail}`);
        }
        
    } catch (error) {
        // If fetch fails completely
        showResult('review-result', 'error', 
            '❌ Could not connect to API. Is the backend running?'
        );
    }
    
    // Re-enable button after response
    btn.disabled = false;
}

// ═══════════════════════════════════
// FEATURE 2 - QR CODE PREVIEW
// Shows image preview before verifying
// ═══════════════════════════════════

function previewQR(input) {
    // input.files[0] = the file user selected
    const file = input.files[0];
    
    if (file) {
        // FileReader reads the file content
        const reader = new FileReader();
        
        // onload runs when file is fully read
        reader.onload = function(e) {
            // Show preview image
            document.getElementById('qr-preview').classList.remove('hidden');
            // e.target.result = the image data as a URL
            document.getElementById('qr-preview-img').src = e.target.result;
        }
        
        // readAsDataURL converts image to a URL string
        reader.readAsDataURL(file);
    }
}

// ═══════════════════════════════════
// FEATURE 2 - VERIFY QR CODE
// ═══════════════════════════════════

async function verifyQR() {
    // Get the uploaded file
    const fileInput = document.getElementById('qr-input');
    const file = fileInput.files[0];
    
    if (!file) {
        showResult('verify-result', 'error', '⚠️ Please upload a QR code image first!');
        return;
    }
    
    showResult('verify-result', 'loading', '⏳ Verifying QR code...');
    
    const btn = event.target;
    btn.disabled = true;
    
    try {
        // FormData is used to send FILES to an API
        // JSON.stringify doesn't work for files — FormData does
        const formData = new FormData();
        
        // append adds our file to the form data
        // 'qr_image' must match the parameter name in our FastAPI route
        formData.append('qr_image', file);
        
        const response = await fetch(`${API_URL}/verify-qr`, {
            method: 'POST',
            // Note: NO Content-Type header when sending FormData
            // Browser sets it automatically with correct boundary
            body: formData
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            if (data.result === 'REAL') {
                showResult('verify-result', 'real',
                    `✅ <strong>REAL PRODUCT VERIFIED</strong><br>
                    Product: ${data.product_name}<br>
                    ID: ${data.product_id}`
                );
            } else {
                showResult('verify-result', 'fake',
                    `❌ <strong>FAKE PRODUCT DETECTED</strong><br>
                    This QR code is not in our database<br>
                    <small>Product ID found: ${data.product_id}</small>`
                );
            }
        } else {
            showResult('verify-result', 'error', `⚠️ ${data.detail}`);
        }
        
    } catch (error) {
        showResult('verify-result', 'error',
            '❌ Could not connect to API. Is the backend running?'
        );
    }
    
    btn.disabled = false;
}

// ═══════════════════════════════════
// FEATURE 3 - GENERATE QR CODE
// ═══════════════════════════════════

async function generateQR() {
    // Get product name from input
    const productName = document.getElementById('product-input').value;
    
    if (!productName.trim()) {
        showResult('generate-result', 'error', '⚠️ Please enter a product name!');
        return;
    }
    
    showResult('generate-result', 'loading', '⏳ Generating QR code...');
    
    const btn = event.target;
    btn.disabled = true;
    
    try {
        const response = await fetch(`${API_URL}/generate-qr`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ product_name: productName })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showResult('generate-result', 'real',
                `✅ <strong>QR Code Generated!</strong><br>
                Product: ${data.product_name}<br>
                Product ID: ${data.product_id}<br>
                <small>QR code saved to backend/qr/qr_codes/</small>`
            );
            
            // Clear input after success
            document.getElementById('product-input').value = '';
            
        } else {
            showResult('generate-result', 'error', `⚠️ ${data.detail}`);
        }
        
    } catch (error) {
        showResult('generate-result', 'error',
            '❌ Could not connect to API. Is the backend running?'
        );
    }
    
    btn.disabled = false;
}