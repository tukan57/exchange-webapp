from flask import Blueprint, render_template, session, redirect, url_for, request
from services.exchange_service import ExchangeService
from services.analytics_service import AnalyticsService
from services.storage_service import StorageService

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def dashboard():
    if 'user' not in session: return redirect(url_for('auth.login'))
    
    setts = StorageService.load_settings()
    data = ExchangeService().get_latest_rates(setts['baseCurrency'], setts['selectedCurrencies'])
    
    rates = data.get('rates', {}) if data else {}
    stats = AnalyticsService.get_min_max(rates)
    
    return render_template('dashboard.html', rates=rates, stats=stats, settings=setts)