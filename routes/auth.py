from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for
from config import Config

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == Config.USERNAME and password == Config.PASSWORD:
            session['user_id'] = username
            return jsonify({
                "success": True, 
                "redirect": url_for('views.dashboard')
            }), 200
        
        return jsonify({"success": False, "message": "Neplatné údaje"}), 401
        
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))