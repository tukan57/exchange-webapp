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

            const result = await response.json();

            if (response.ok && result.success) {
                // Přihlášení bylo úspěšné, jdeme na hlavní stránku
                errorEl.innerText = "Vítej, " + username + "!";
                window.location.href = '/'; 
            } else {
                errorEl.innerText = result.message || "Nesprávné jméno nebo heslo.";
            }
        } catch (error) {
            console.error("Login error:", error);
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