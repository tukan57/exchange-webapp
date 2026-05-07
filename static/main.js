// Konfigurace a stav
let state = {
    user: null,
    settings: {
        base: 'EUR',
        symbols: ['USD', 'CZK', 'GBP']
    }
};

// Inicializace
document.addEventListener('DOMContentLoaded', () => {
    // Pokud jsme na stránce s loginem
    if (document.getElementById('loginForm')) {
        initLogin();
    } else {
        // Na hlavní stránce načteme data a ověříme session
        checkAuthAndInit();
    }
    
    // Připojení eventu pro ukládání nastavení
    const sForm = document.getElementById('settingsForm');
    if (sForm) {
        sForm.addEventListener('submit', saveSettings);
    }
});

// Ověření, zda je uživatel přihlášen (volá backend)
async function checkAuthAndInit() {
    try {
        const response = await fetch('/api/check-auth'); // Endpoint, který musíme přidat do Flasku
        if (response.status === 401) {
            window.location.href = 'login.html';
            return;
        }
        renderDashboard();
    } catch (e) {
        console.error("Auth check failed", e);
    }
}

// volání na Flask auth.py
function initLogin() {
    const loginForm = document.getElementById('loginForm');
    if (!loginForm) return;

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const errorEl = document.getElementById('loginError');

        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
            });

            const result = await response.json(); // Přečteme JSON z Flasku

            if (result.success && result.redirect) {
                // Pokud je vše OK, JS nás přesměruje na dashboard
                window.location.href = result.redirect;
            } else {
                errorEl.innerText = result.message || "Nesprávné jméno nebo heslo.";
            }
        } catch (error) {
            errorEl.innerText = "Chyba při komunikaci se serverem.";
        }
    });
}

// Získání reálných dat z vašeho ExchangeService (přes Flask)
async function fetchRates() {
    try {
        const response = await fetch('/api/rates'); // Backend endpoint
        const data = await response.json();
        
        if (!data || !data.rates) {
            throw new Error("Data nebyla vrácena");
        }
        return data;
    } catch (error) {
        console.error("API Fail:", error);
        return null;
    }
}

// Renderování Dashboardu
async function renderDashboard() {
    const data = await fetchRates();
    if (!data) return;

    // Aktualizace UI statistik
    // Předpokládáme, že backend vrací i vypočtené stats nebo je spočítáme zde
    const entries = Object.entries(data.rates);
    const strongest = entries.reduce((prev, curr) => curr[1] > prev[1] ? curr : prev);
    const weakest = entries.reduce((prev, curr) => curr[1] < prev[1] ? curr : prev);
    const avg = entries.reduce((sum, curr) => sum + curr[1], 0) / entries.length;

    document.getElementById('strongestCurrency').innerText = `${strongest[0]}: ${strongest[1]}`;
    document.getElementById('weakestCurrency').innerText = `${weakest[0]}: ${weakest[1]}`;
    document.getElementById('avgRate').innerText = avg.toFixed(4);

    // Plnění tabulky
    const tbody = document.querySelector('#currencyTable tbody');
    if (tbody) {
        tbody.innerHTML = entries.map(([code, rate]) => `
            <tr>
                <td><strong>${code}</strong></td>
                <td>${rate}</td>
                <td><span class="trend">Stable</span></td>
            </tr>
        `).join('');
    }
}

// Uložení nastavení na server (Persistentní soubor)
async function saveSettings(e) {
    e.preventDefault();
    const base = document.getElementById('baseCurrencySelect').value;
    const symbols = Array.from(document.querySelectorAll('#symbolsGroup input:checked')).map(cb => cb.value);
    
    try {
        const response = await fetch('/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `base=${base}&${symbols.map(s => `symbols=${s}`).join('&')}`
        });

        if (response.ok) {
            alert('Nastavení uloženo na server.');
            renderDashboard();
            showSection('dashboard');
        }
    } catch (error) {
        alert('Chyba při ukládání.');
    }
}

function logout() {
    window.location.href = '/logout';
}

let myChart = null; // Globální proměnná pro instanci grafu

document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();
    setupSettingsForm();
});

// Přepínání sekcí
function showSection(sectionId) {
    document.querySelectorAll('.app-section').forEach(s => s.style.display = 'none');
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    
    document.getElementById(`${sectionId}-section`).style.display = 'block';
    document.getElementById(`nav-${sectionId}`).classList.add('active');
    document.getElementById('section-title').innerText = sectionId.charAt(0).toUpperCase() + sectionId.slice(1);
}

// Načtení dat z backendu
async function loadDashboardData() {
    try {
        const response = await fetch('/api/rates'); // Předpokládám tuto routu v Flasku
        const data = await response.json();

        if (data) {
            updateStats(data.rates);
            updateTable(data.rates);
            renderChart(data.rates, data.base);
            
            // Aktualizace textu u grafu
            document.querySelectorAll('.base-currency-tag').forEach(el => el.innerText = data.base);
        }
    } catch (err) {
        console.error("Chyba při načítání dat:", err);
    }
}

// Vykreslení grafu pomocí Chart.js
function renderChart(rates, baseCurrency) {
    const ctx = document.getElementById('rateChart').getContext('2d');
    
    // Pokud graf už existuje, zničíme ho, aby se mohl vytvořit nový s novými daty
    if (myChart) {
        myChart.destroy();
    }

    const labels = Object.keys(rates);
    const values = Object.values(rates);

    myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: `Kurz vůči ${baseCurrency}`,
                data: values,
                backgroundColor: '#3498db',
                borderRadius: 5
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: false,
                    grid: { color: '#f0f0f0' }
                }
            }
        }
    });
}

function setupSettingsForm() {
    const form = document.getElementById('settingsForm'); // Musí odpovídat ID v HTML
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // 1. Sesbíráme data z formuláře
        const base = document.getElementById('baseCurrencySelect').value;
        const selected = Array.from(document.querySelectorAll('#symbolsGroup input:checked'))
                              .map(cb => cb.value);

        // 2. Pošleme je jako JSON
        try {
            const response = await fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    baseCurrency: base,
                    selectedCurrencies: selected
                })
            });

            if (response.ok) {
                alert('Nastavení úspěšně uloženo!');
                await loadDashboardData();
                showSection('dashboard');  
            } else {
                alert('Chyba při ukládání nastavení.');
            }
        } catch (error) {
            console.error("Save failed:", error);
        }
    });
}

// Pomocné funkce pro statistiky a tabulku
function updateStats(rates) {
    const values = Object.values(rates);
    const keys = Object.keys(rates);
    
    const maxVal = Math.max(...values);
    const minVal = Math.min(...values);
    const avg = values.reduce((a, b) => a + b, 0) / values.length;

    document.getElementById('strongestCurrency').innerText = keys[values.indexOf(minVal)]; // Nejsilnější měna má nejnižší kurz k Base
    document.getElementById('weakestCurrency').innerText = keys[values.indexOf(maxVal)];
    document.getElementById('avgRate').innerText = avg.toFixed(2);
}

function updateTable(rates) {
    const tbody = document.querySelector('#currencyTable tbody');
    tbody.innerHTML = '';
    
    for (const [currency, value] of Object.entries(rates)) {
        const row = `<tr>
            <td><strong>${currency}</strong></td>
            <td>${value.toFixed(4)}</td>
            <td><span class="trend-up">▲</span></td>
        </tr>`;
        tbody.innerHTML += row;
    }
}