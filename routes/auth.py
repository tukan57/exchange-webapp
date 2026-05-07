from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from config import Config  # Importujeme vaši konfiguraci

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Porovnání s údaji v Configu
        if username == Config.USERNAME and password == Config.PASSWORD:
            session['user_id'] = username  # Přihlášení úspěšné
            return redirect(url_for('views.dashboard'))
    
        return "Neplatné údaje", 401
        
    return render_template('login.html')