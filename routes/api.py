from flask import Blueprint, jsonify, request, session
from services.exchange_service import ExchangeService
from services.storage_service import StorageService

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/check-auth')
def check_auth():
    if 'user_id' not in session:
        return jsonify({"auth": False}), 401
    return jsonify({"auth": True}), 200

@api_bp.route('/api/rates')
def get_rates():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    settings = StorageService.load_settings()
    exchange_svc = ExchangeService()
    data = exchange_svc.get_latest_rates(settings['baseCurrency'], settings['selectedCurrencies'])
    
    return jsonify(data)

@api_bp.route('/api/settings', methods=['POST'])
def update_settings():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    new_data = request.get_json() 
    
    if not new_data:
        return jsonify({"error": "Žádná data"}), 400

    # Uložení přes tvou StorageService
    current_settings = StorageService.load_settings()
    current_settings.update(new_data)
    StorageService.save_settings(current_settings)
    
    return jsonify({"success": True})