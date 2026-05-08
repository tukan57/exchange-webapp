from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for
from config import Config
from services.storage_service import StorageService
from services.logging_service import LoggingService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username')
    password = request.form.get('password')

    if username == Config.USERNAME and password == Config.PASSWORD:
        session['user_id'] = username
        from services.logging_service import LoggingService
        LoggingService.log_event("info", f"Uživatel {username} se přihlásil.")
        
        return jsonify({"success": True, "redirect": url_for('views.dashboard')}), 200
    
    from services.logging_service import LoggingService
    LoggingService.log_event("warning", f"Neúspěšný pokus o přihlášení: {username}")
    return jsonify({"success": False, "message": "Neplatné údaje"}), 401

@auth_bp.route('/logout')
def logout():
    session.clear()
    LoggingService.log_event("info", "Uživatel se odhlásil")
    return redirect(url_for('auth.login'))