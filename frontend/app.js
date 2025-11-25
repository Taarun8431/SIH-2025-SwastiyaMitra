// API Configuration
const API_BASE_URL = 'http://localhost:8000';
let authToken = null;
let currentMigrants = [];

// Utility Functions
function showStatus(elementId, message, isSuccess = true) {
    const statusElement = document.getElementById(elementId);
    statusElement.textContent = message;
    statusElement.className = `status ${isSuccess ? 'success' : 'error'}`;
    statusElement.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        statusElement.style.display = 'none';
    }, 5000);
}

function showLoading(buttonElement) {
    buttonElement.disabled = true;
    buttonElement.innerHTML = '<span class="loading"></span> Processing...';
}

function hideLoading(buttonElement, originalText) {
    buttonElement.disabled = false;
    buttonElement.innerHTML = originalText;
}

// Authentication Functions
async function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const loginBtn = document.querySelector('#loginSection .btn');
    
    if (!username || !password) {
        showStatus('loginStatus', 'Please enter both username and password', false);
        return;
    }
    
    showLoading(loginBtn);
    
    try {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            authToken = data.access_token;
            
            showStatus('loginStatus', '✅ Login successful!');
            
            // Show other sections
            document.getElementById('migrantSection').style.display = 'block';
            document.getElementById('encounterSection').style.display = 'block';
            document.getElementById('dataDisplay').style.display = 'block';
            
            // Load existing migrants
            await loadMigrants();
            await refreshData();
            
        } else {
            const errorData = await response.json();
            showStatus('loginStatus', `❌ Login failed: ${errorData.detail || 'Invalid credentials'}`, false);
        }
    } catch (error) {
        showStatus('loginStatus', `❌ Connection error: ${error.message}`, false);
    }
    
    hideLoading(loginBtn, 'Login');
}

// Migrant Functions
async function registerMigrant() {
    const migrantBtn = document.querySelector('#migrantSection .btn');
    showLoading(migrantBtn);
    
    try {
        const migrantData = {
            name: document.getElementById('migrantName').value,
            gender: document.getElementById('migrantGender').value,
            contact: document.getElementById('migrantContact').value,
            district_in_kerala: document.getElementById('migrantDistrict').value,
            occupation: document.getElementById('migrantOccupation').value,
            age: parseInt(document.getElementById('migrantAge').value) || null,
            location_lat: parseFloat(document.getElementById('migrantLat').value) || null,
            location_lng: parseFloat(document.getElementById('migrantLng').value) || null
        };
        
        // Validate required fields
        if (!migrantData.name || !migrantData.gender) {
            showStatus('migrantStatus', '❌ Please fill in required fields (Name and Gender)', false);
            hideLoading(migrantBtn, 'Register Migrant');
            return;
        }
        
        const response = await fetch(`${API_BASE_URL}/migrant/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(migrantData)
        });
        
        if (response.ok) {
            const result = await response.json();
            showStatus('migrantStatus', `✅ Migrant registered successfully! ID: ${result.id}`);
            
            // Display QR Code immediately
            if (result.qr_code) {
                displayQRCode(result.id, result.name, result.qr_code);
            }
            
            // Clear form
            document.getElementById('migrantName').value = '';
            document.getElementById('migrantGender').value = '';
            document.getElementById('migrantContact').value = '';
            document.getElementById('migrantDistrict').value = '';
            document.getElementById('migrantOccupation').value = '';
            document.getElementById('migrantAge').value = '';
            document.getElementById('migrantLat').value = '';
            document.getElementById('migrantLng').value = '';
            
            // Refresh data
            await loadMigrants();
            await refreshData();
            
        } else {
            const errorData = await response.json();
            showStatus('migrantStatus', `❌ Registration failed: ${errorData.detail || 'Unknown error'}`, false);
        }
    } catch (error) {
        showStatus('migrantStatus', `❌ Connection error: ${error.message}`, false);
    }
    
    hideLoading(migrantBtn, 'Register Migrant');
}

async function loadMigrants() {
    try {
        const response = await fetch(`${API_BASE_URL}/migrant/`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            currentMigrants = await response.json();
            
            // Update migrant dropdown
            const migrantSelect = document.getElementById('encounterMigrant');
            migrantSelect.innerHTML = '<option value="">Select a migrant</option>';
            
            currentMigrants.forEach(migrant => {
                const option = document.createElement('option');
                option.value = migrant.id;
                option.textContent = `${migrant.name} (ID: ${migrant.id}) - ${migrant.district_in_kerala || 'Unknown District'}`;
                migrantSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading migrants:', error);
    }
}

// Encounter Functions
async function addEncounter() {
    const encounterBtn = document.querySelector('#encounterSection .btn');
    showLoading(encounterBtn);
    
    try {
        const encounterData = {
            migrant_id: parseInt(document.getElementById('encounterMigrant').value),
            symptoms: document.getElementById('encounterSymptoms').value,
            diagnosis: document.getElementById('encounterDiagnosis').value,
            treatment: document.getElementById('encounterTreatment').value,
            encounter_type: document.getElementById('encounterType').value,
            notes: document.getElementById('encounterNotes').value
        };
        
        // Validate required fields
        if (!encounterData.migrant_id || !encounterData.symptoms || !encounterData.diagnosis) {
            showStatus('encounterStatus', '❌ Please fill in required fields (Migrant, Symptoms, Diagnosis)', false);
            hideLoading(encounterBtn, 'Add Encounter');
            return;
        }
        
        const response = await fetch(`${API_BASE_URL}/encounter/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(encounterData)
        });
        
        if (response.ok) {
            const result = await response.json();
            showStatus('encounterStatus', `✅ Encounter added successfully! ID: ${result.id}`);
            
            // Clear form
            document.getElementById('encounterMigrant').value = '';
            document.getElementById('encounterSymptoms').value = '';
            document.getElementById('encounterDiagnosis').value = '';
            document.getElementById('encounterTreatment').value = '';
            document.getElementById('encounterNotes').value = '';
            
            // Refresh data
            await refreshData();
            
        } else {
            const errorData = await response.json();
            showStatus('encounterStatus', `❌ Failed to add encounter: ${errorData.detail || 'Unknown error'}`, false);
        }
    } catch (error) {
        showStatus('encounterStatus', `❌ Connection error: ${error.message}`, false);
    }
    
    hideLoading(encounterBtn, 'Add Encounter');
}

// Data Display Functions
async function refreshData() {
    const dataContainer = document.getElementById('recentData');
    dataContainer.innerHTML = '<div class="loading"></div> Loading recent data...';
    
    try {
        // Fetch recent migrants
        const migrantsResponse = await fetch(`${API_BASE_URL}/migrant/`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        let html = '';
        
        if (migrantsResponse.ok) {
            const migrants = await migrantsResponse.json();
            const recentMigrants = migrants.slice(-5); // Last 5 migrants
            
            html += '<h4>📋 Recent Migrants</h4>';
            recentMigrants.forEach(migrant => {
                html += `
                    <div class="data-item">
                        <strong>ID ${migrant.id}:</strong> ${migrant.name} 
                        <br><small>Gender: ${migrant.gender} | District: ${migrant.district_in_kerala || 'Unknown District'} | Contact: ${migrant.contact || 'N/A'}</small>
                        <br><small>Occupation: ${migrant.occupation || 'N/A'} | Location: ${migrant.location_lat ? `${migrant.location_lat}, ${migrant.location_lng}` : 'N/A'}</small>
                    </div>
                `;
            });
        }
        
        // Fetch recent encounters for each migrant
        html += '<h4 style="margin-top: 20px;">🏥 Recent Encounters</h4>';
        let encounterCount = 0;
        
        for (const migrant of currentMigrants.slice(-3)) { // Last 3 migrants
            try {
                const encountersResponse = await fetch(`${API_BASE_URL}/encounter/migrant/${migrant.id}`, {
                    headers: {
                        'Authorization': `Bearer ${authToken}`
                    }
                });
                
                if (encountersResponse.ok) {
                    const encounters = await encountersResponse.json();
                    encounters.forEach(encounter => {
                        encounterCount++;
                        html += `
                            <div class="data-item">
                                <strong>Encounter ID ${encounter.id}</strong> - ${migrant.name}
                                <br><small>Type: ${encounter.encounter_type} | Diagnosis: ${encounter.diagnosis}</small>
                                <br><small>Symptoms: ${encounter.symptoms}</small>
                                <br><small>Treatment: ${encounter.treatment}</small>
                            </div>
                        `;
                    });
                }
            } catch (error) {
                console.error(`Error fetching encounters for migrant ${migrant.id}:`, error);
            }
        }
        
        if (encounterCount === 0) {
            html += '<div class="data-item">No encounters found</div>';
        }
        
        // Add database info
        html += `
            <h4 style="margin-top: 20px;">💾 Database Information</h4>
            <div class="data-item">
                <strong>Total Migrants:</strong> ${currentMigrants.length}<br>
                <strong>Database:</strong> PostgreSQL (SIH-DB)<br>
                <strong>Server:</strong> ${API_BASE_URL}<br>
                <strong>Last Updated:</strong> ${new Date().toLocaleString()}
            </div>
        `;
        
        dataContainer.innerHTML = html;
        
    } catch (error) {
        dataContainer.innerHTML = `<div class="data-item" style="color: red;">❌ Error loading data: ${error.message}</div>`;
    }
}

// QR Code Display Functions
async function displayQRCode(migrantId, migrantName, qrCodeData) {
    const qrDisplay = document.getElementById('qrDisplay');
    const qrImage = document.getElementById('qrImage');
    const qrMigrantId = document.getElementById('qrMigrantId');
    const qrMigrantName = document.getElementById('qrMigrantName');
    const qrData = document.getElementById('qrData');
    const medicalRecords = document.getElementById('medicalRecords');
    
    // Set QR code image
    qrImage.src = qrCodeData;
    
    // Set migrant information
    qrMigrantId.textContent = migrantId;
    qrMigrantName.textContent = migrantName;
    qrData.textContent = `API URL: ${API_BASE_URL}/migrant/${migrantId}/complete`;
    
    // Fetch complete medical records
    try {
        const response = await fetch(`${API_BASE_URL}/migrant/${migrantId}/complete`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const completeData = await response.json();
            displayMedicalRecords(completeData.encounters);
        } else {
            medicalRecords.innerHTML = '<div class="no-records">Failed to load medical records</div>';
        }
    } catch (error) {
        medicalRecords.innerHTML = '<div class="no-records">Error loading medical records</div>';
    }
    
    // Show the QR display section
    qrDisplay.style.display = 'block';
    
    // Scroll to QR code section
    qrDisplay.scrollIntoView({ behavior: 'smooth' });
    
    // Store QR data globally for download/print functions
    window.currentQRData = {
        id: migrantId,
        name: migrantName,
        qrCode: qrCodeData
    };
}

function displayMedicalRecords(encounters) {
    const medicalRecords = document.getElementById('medicalRecords');
    
    if (!encounters || encounters.length === 0) {
        medicalRecords.innerHTML = '<div class="no-records">No medical records found</div>';
        return;
    }
    
    let html = '';
    encounters.forEach((encounter, index) => {
        const date = encounter.occurred_at ? new Date(encounter.occurred_at).toLocaleDateString() : 
                    new Date(encounter.created_at).toLocaleDateString();
        
        html += `
            <div class="encounter-card">
                <div class="encounter-header">
                    <span class="encounter-type">${encounter.encounter_type}</span>
                    <span class="encounter-date">${date}</span>
                </div>
                <div class="encounter-details">
                    <div class="detail-group">
                        <div class="detail-label">Symptoms</div>
                        <div class="detail-value">${encounter.symptoms || 'N/A'}</div>
                    </div>
                    <div class="detail-group">
                        <div class="detail-label">Diagnosis</div>
                        <div class="detail-value">${encounter.diagnosis || 'N/A'}</div>
                    </div>
                    <div class="detail-group">
                        <div class="detail-label">Treatment</div>
                        <div class="detail-value">${encounter.treatment || 'N/A'}</div>
                    </div>
                    <div class="detail-group">
                        <div class="detail-label">Doctor</div>
                        <div class="detail-value">${encounter.doctor || 'N/A'}</div>
                    </div>
                </div>
                ${encounter.notes ? `<div style="margin-top: 10px; padding: 8px; background: #fff3cd; border-radius: 4px; font-size: 0.9em;"><strong>Notes:</strong> ${encounter.notes}</div>` : ''}
            </div>
        `;
    });
    
    medicalRecords.innerHTML = html;
}

function downloadQR() {
    if (!window.currentQRData) {
        alert('No QR code available to download');
        return;
    }
    
    // Create download link
    const link = document.createElement('a');
    link.href = window.currentQRData.qrCode;
    link.download = `migrant_${window.currentQRData.id}_${window.currentQRData.name.replace(/\s+/g, '_')}_qr.png`;
    
    // Trigger download
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showStatus('migrantStatus', '✅ QR code downloaded successfully!');
}

function printQR() {
    if (!window.currentQRData) {
        alert('No QR code available to print');
        return;
    }
    
    // Create print window with medical records
    const printWindow = window.open('', '_blank');
    
    // Get medical records HTML
    const medicalRecordsElement = document.getElementById('medicalRecords');
    const medicalRecordsHTML = medicalRecordsElement ? medicalRecordsElement.innerHTML : '<div class="no-records">No medical records available</div>';
    
    printWindow.document.write(`
        <html>
        <head>
            <title>Migrant Medical Records - ${window.currentQRData.name}</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    padding: 20px; 
                    color: #333;
                }
                .header {
                    text-align: center;
                    border-bottom: 2px solid #4facfe;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }
                .header h1 {
                    color: #4facfe;
                    margin-bottom: 10px;
                }
                .qr-section {
                    display: flex;
                    align-items: center;
                    margin-bottom: 30px;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                }
                .qr-section img {
                    width: 150px;
                    height: 150px;
                    margin-right: 30px;
                    border: 1px solid #ccc;
                }
                .qr-info h3 {
                    margin-bottom: 15px;
                    color: #4facfe;
                }
                .qr-info p {
                    margin: 5px 0;
                }
                .medical-records h2 {
                    color: #28a745;
                    border-bottom: 2px solid #28a745;
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                }
                .encounter-card {
                    border: 1px solid #ddd;
                    padding: 15px;
                    margin-bottom: 15px;
                    border-radius: 5px;
                    page-break-inside: avoid;
                }
                .encounter-header {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 10px;
                    font-weight: bold;
                }
                .encounter-type {
                    background: #28a745;
                    color: white;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 0.8em;
                }
                .encounter-details {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 15px;
                    margin-top: 10px;
                }
                .detail-group {
                    border: 1px solid #eee;
                    padding: 8px;
                    border-radius: 4px;
                }
                .detail-label {
                    font-weight: bold;
                    font-size: 0.9em;
                    margin-bottom: 5px;
                    color: #666;
                }
                .detail-value {
                    font-size: 0.9em;
                }
                .no-records {
                    text-align: center;
                    color: #666;
                    font-style: italic;
                    padding: 20px;
                }
                .footer {
                    margin-top: 30px;
                    text-align: center;
                    font-size: 0.8em;
                    color: #666;
                    border-top: 1px solid #ddd;
                    padding-top: 15px;
                }
                @media print {
                    body { margin: 0; }
                    .header { page-break-after: avoid; }
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏥 SIH Migrant Health System</h1>
                <p>Complete Medical Records</p>
            </div>
            
            <div class="qr-section">
                <img src="${window.currentQRData.qrCode}" alt="Migrant QR Code">
                <div class="qr-info">
                    <h3>Patient Information</h3>
                    <p><strong>Migrant ID:</strong> ${window.currentQRData.id}</p>
                    <p><strong>Name:</strong> ${window.currentQRData.name}</p>
                    <p><strong>Generated:</strong> ${new Date().toLocaleString()}</p>
                    <p><strong>QR Contains:</strong> Complete medical history accessible via API</p>
                </div>
            </div>
            
            <div class="medical-records">
                <h2>📋 Medical Records</h2>
                ${medicalRecordsHTML}
            </div>
            
            <div class="footer">
                <p>This document contains confidential medical information. Handle with care.</p>
                <p>Generated on ${new Date().toLocaleString()} | SIH Migrant Health System</p>
            </div>
        </body>
        </html>
    `);
    
    printWindow.document.close();
    printWindow.focus();
    
    // Wait for content to load then print
    setTimeout(() => {
        printWindow.print();
        printWindow.close();
    }, 1500);
    
    showStatus('migrantStatus', '✅ Complete medical records sent to printer!');
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    console.log('SIH Frontend loaded');
    console.log('API Base URL:', API_BASE_URL);
    
    // Add enter key support for login
    document.getElementById('password').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            login();
        }
    });
});
