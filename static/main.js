// --- Globální stav ---
let myChart = null;
let currentLang = localStorage.getItem('lang') || 'cs';
let currentBase = '---'; // Pomocná proměnná pro uchování aktuální základní měny

const translations = {
    cs: {
        dashboard: "📊 Dashboard",
        settings: "⚙️ Nastavení",
        logout: "Odhlásit se",
        base_curr: "Základní měna",
        watched_curr: "Sledované měny",
        save: "Uložit preference",
        config_title: "Konfigurace systému",
        overview: "Přehled kurzů",
        strongest: "Nejsilnější měna",
        weakest: "Nejslabší měna",
        avg: "Průměrný kurz",
        chart_title: "Vizualizace kurzů (vůči ",
        chart_label: "Kurz vůči ",
        table_curr: "Měna",
        table_rate: "Hodnota"
    },
    en: {
        dashboard: "📊 Dashboard",
        settings: "⚙️ Settings",
        logout: "Logout",
        base_curr: "Base Currency",
        watched_curr: "Watched Currencies",
        save: "Save Preferences",
        config_title: "System Configuration",
        overview: "Rates Overview",
        strongest: "Strongest Currency",
        weakest: "Weakest Currency",
        avg: "Average Rate",
        chart_title: "Rates Visualization (vs ",
        chart_label: "Rate vs ",
        table_curr: "Currency",
        table_rate: "Value"
    }
};

// --- Inicializace ---
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('loginForm')) {
        initLogin();
    } else {
        loadDashboardData();
        setupSettingsForm();
        initCurrencySearch();
        applyTranslations();
    }
});

// --- Jazyková logika ---
function switchLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('lang', lang);
    applyTranslations();
    // Pokud máme data, překreslíme graf s novým popiskem (label v legendě)
    if (myChart) {
        loadDashboardData(); 
    }
}

function applyTranslations() {
    const t = translations[currentLang];
    if (!t) return;

    // Nadpis sekce v top-baru
    const sectionTitle = document.getElementById('section-title');
    if (sectionTitle) {
        const isDash = document.getElementById('dashboard-section').style.display !== 'none';
        sectionTitle.innerText = isDash ? t.overview : t.config_title;
    }

    // Sidebar
    document.getElementById('nav-dashboard').innerHTML = `<i>📊</i> ${t.dashboard}`;
    document.getElementById('nav-settings').innerHTML = `<i>⚙️</i> ${t.settings}`;
    document.querySelector('.btn-logout').innerText = t.logout;

    // Statistiky a Tabulka
    document.getElementById('lbl-strongest').innerText = t.strongest;
    document.getElementById('lbl-weakest').innerText = t.weakest;
    document.getElementById('lbl-avg').innerText = t.avg;
    document.getElementById('th-curr').innerText = t.table_curr;
    document.getElementById('th-rate').innerText = t.table_rate;
    
    // Nadpis grafu (oprava zobrazení base currency)
    const chartTitleH3 = document.querySelector('.chart-card h3');
    if (chartTitleH3) {
        chartTitleH3.innerHTML = `${t.chart_title}<span class="base-currency-tag">${currentBase}</span>)`;
    }

    // Nastavení
    document.getElementById('lbl-base-curr').innerText = t.base_curr;
    document.getElementById('lbl-watched-curr').innerText = t.watched_curr;
    document.getElementById('btn-save-text').innerText = t.save;

    // Aktivní tlačítko jazyka
    document.querySelectorAll('.btn-lang').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`lang-${currentLang}`).classList.add('active');
}

// --- Data a Dashboard ---
async function loadDashboardData() {
    try {
        const response = await fetch('/api/rates');
        const data = await response.json();

        if (data && data.rates) {
            currentBase = data.base; // Uložíme si pro překlady
            updateStats(data.rates);
            updateTable(data.rates);
            renderChart(data.rates, data.base);
            
            // Okamžitá aktualizace tagů v HTML
            document.querySelectorAll('.base-currency-tag').forEach(el => el.innerText = data.base);
        }
    } catch (err) {
        console.error("Chyba při načítání dat:", err);
    }
}

function updateStats(rates) {
    const values = Object.values(rates);
    const keys = Object.keys(rates);
    if (values.length === 0) return;
    
    const maxVal = Math.max(...values);
    const minVal = Math.min(...values);
    const avg = values.reduce((a, b) => a + b, 0) / values.length;

    // Nejsilnější měna = nejnižší číslo (stojí nejméně jednotek základní měny)
    document.getElementById('strongestCurrency').innerText = keys[values.indexOf(minVal)];
    document.getElementById('weakestCurrency').innerText = keys[values.indexOf(maxVal)];
    document.getElementById('avgRate').innerText = avg.toFixed(4);
}

function updateTable(rates) {
    const tbody = document.querySelector('#currencyTable tbody');
    if (!tbody) return;
    
    tbody.innerHTML = Object.entries(rates).map(([code, rate]) => `
        <tr>
            <td><strong>${code}</strong></td>
            <td>${rate.toFixed(4)}</td>
        </tr>
    `).join('');
}

function renderChart(rates, baseCurrency) {
    const canvas = document.getElementById('rateChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    if (myChart) myChart.destroy();

    const t = translations[currentLang];

    myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(rates),
            datasets: [{
                label: `${t.chart_label} ${baseCurrency}`,
                data: Object.values(rates),
                backgroundColor: '#4361ee',
                borderRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: false, grid: { color: '#f0f0f0' } }
            }
        }
    });
}

// --- Navigace a hledání ---
function showSection(sectionId) {
    document.querySelectorAll('.app-section').forEach(s => s.style.display = 'none');
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    
    const target = document.getElementById(`${sectionId}-section`);
    if (target) target.style.display = 'block';
    
    const navLink = document.getElementById(`nav-${sectionId}`);
    if (navLink) navLink.classList.add('active');

    applyTranslations();
}

function initCurrencySearch() {
    const searchInput = document.getElementById('currencySearch');
    if (!searchInput) return;

    searchInput.addEventListener('input', (e) => {
        const term = e.target.value.toLowerCase();
        document.querySelectorAll('#symbolsGroup .chip').forEach(chip => {
            const name = chip.getAttribute('data-name') || "";
            const code = chip.getAttribute('data-code') || "";
            chip.style.display = (name.includes(term) || code.includes(term)) ? 'flex' : 'none';
        });
    });
}

// --- Nastavení a Auth ---
function setupSettingsForm() {
    const form = document.getElementById('settingsForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const base = document.getElementById('baseCurrencySelect').value;
        const selected = Array.from(document.querySelectorAll('#symbolsGroup input:checked')).map(cb => cb.value);

        try {
            const response = await fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ baseCurrency: base, selectedCurrencies: selected })
            });

            if (response.ok) {
                await loadDashboardData();
                showSection('dashboard');
            }
        } catch (error) {
            console.error("Save failed:", error);
        }
    });
}

function logout() { window.location.href = '/logout'; }

function initLogin() {
    const loginForm = document.getElementById('loginForm');
    if (!loginForm) return;

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // Zabrání klasickému refresh stránky

        const formData = new FormData(loginForm);
        
        try {
            const response = await fetch('/login', {
                method: 'POST',
                body: formData // Flask request.form.get() tohle přečte automaticky
            });

            if (response.redirected) {
                // Pokud jsi v auth.py použil Možnost A (return redirect)
                window.location.href = response.url;
            } else {
                const data = await response.json();
                if (data.success) {
                    window.location.href = data.redirect;
                } else {
                    alert(data.message || "Neplatné údaje");
                }
            }
        } catch (error) {
            console.error("Login Error:", error);
            alert("Chyba při komunikaci se serverem.");
        }
    });
}