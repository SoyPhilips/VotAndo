import os
import shutil
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, send_from_directory
from flask_cors import CORS
from backend.models import db, Proposal, User
from backend.auth import auth_bp, bcrypt
from backend.routes import api_bp

app = Flask(__name__, static_folder='frontend/static')
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../data/vota_ciudadano.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'vota-ciudadano-super-secret-key')

db.init_app(app)
bcrypt.init_app(app)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def serve_index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)

def init_db():
    with app.app_context():
        db.create_all()
        
        # Add default admin if not exists
        if not User.query.filter_by(email='admin@vota.com').first():
            hashed_pw = bcrypt.generate_password_hash('Admin123').decode('utf-8')
            admin = User(email='admin@vota.com', password_hash=hashed_pw, is_admin=True)
            db.session.add(admin)
        
        # Add default proposals if table is empty
        if not Proposal.query.first():
            proposals = [
                Proposal(
                    title="¿Implementar recolección de basura nocturna?",
                    description="Propuesta para cambiar el horario de recolección a horas de la noche para mejorar el flujo vehicular diurno.",
                    category="Servicios Públicos",
                    start_date=datetime.utcnow(),
                    end_date=datetime.utcnow() + timedelta(days=30),
                    status='active'
                ),
                Proposal(
                    title="¿Crear ciclovía en la avenida principal?",
                    description="Instalación de una ciclovía protegida de 5km en la Avenida Central para fomentar el transporte sostenible.",
                    category="Movilidad",
                    start_date=datetime.utcnow(),
                    end_date=datetime.utcnow() + timedelta(days=45),
                    status='active'
                ),
                Proposal(
                    title="¿Instalar cámaras de seguridad en el parque central?",
                    description="Proyecto de videovigilancia 24/7 conectado con la policía local para aumentar la seguridad ciudadana.",
                    category="Seguridad",
                    start_date=datetime.utcnow(),
                    end_date=datetime.utcnow() + timedelta(days=20),
                    status='active'
                ),
                Proposal(
                    title="¿Remodelación de la Plaza de los Artesanos?",
                    description="Proyecto arquitectónico para modernizar los puestos de venta y mejorar la iluminación de la plaza.",
                    category="Cultura",
                    start_date=datetime.utcnow(),
                    end_date=datetime.utcnow() + timedelta(days=60),
                    status='active'
                ),
                Proposal(
                    title="¿Nuevas zonas de Wi-Fi gratuito?",
                    description="Habilitar 10 puntos nuevos de conexión a internet de alta velocidad en bibliotecas y centros comunitarios.",
                    category="Tecnología",
                    start_date=datetime.utcnow(),
                    end_date=datetime.utcnow() + timedelta(days=15),
                    status='active'
                )
            ]
            for p in proposals:
                db.session.add(p)
        
        db.session.commit()
        print("Database initialized with default data.")

# Backup Service
def backup_task():
    while True:
        try:
            source = 'data/vota_ciudadano.db'
            if os.path.exists(source):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = f'data/backups/vota_ciudadano_{timestamp}.db'
                shutil.copy2(source, backup_path)
                print(f"Backup created at {backup_path}")
                
                # Keep only last 7 backups
                backups = sorted([os.path.join('data/backups', f) for f in os.listdir('data/backups') if f.endswith('.db')])
                if len(backups) > 7:
                    for old_backup in backups[:-7]:
                        os.remove(old_backup)
        except Exception as e:
            print(f"Backup failed: {e}")
        
        # Wait 24 hours (86400 seconds)
        time.sleep(86400)

if __name__ == '__main__':
    init_db()
    
    # Start backup thread
    threading.Thread(target=backup_task, daemon=True).start()
    
    app.run(debug=True, port=5000)
