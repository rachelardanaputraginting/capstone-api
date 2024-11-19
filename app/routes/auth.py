# app/routes/auth.py
from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET'])
def home():
    return 'Login endpoint'

@auth_bp.route('/login', methods=['POST'])
def login():
    return 'Login endpoint'

@auth_bp.route('/register', methods=['POST'])
def register():
    return 'Register endpoint'
