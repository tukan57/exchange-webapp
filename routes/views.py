from flask import Blueprint, render_template, session, redirect, url_for, request
from services.exchange_service import ExchangeService
from services.analytics_service import AnalyticsService
from services.storage_service import StorageService

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def dashboard():
    if 'user_id' not in session: 
        return redirect(url_for('auth.login'))
    
    setts = StorageService.load_settings()
    exchange_svc = ExchangeService()
    
    data = exchange_svc.get_latest_rates(
        setts.get('baseCurrency', 'EUR'), 
        setts.get('selectedCurrencies', [])
    )
    
    rates = data.get('rates', {}) if data else {}
    stats = AnalyticsService.get_min_max(rates)
    
    return render_template('index.html', rates=rates, stats=stats, settings=setts)

@views_bp.route('/settings')
def settings_page():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    setts = StorageService.load_settings()
    return render_template('settings.html', settings=setts)