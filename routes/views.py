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
    
    all_currencies = exchange_svc.get_all_currencies()
    
    return render_template('index.html', 
                           rates={},
                           stats={}, 
                           settings=setts, 
                           all_currencies=all_currencies)