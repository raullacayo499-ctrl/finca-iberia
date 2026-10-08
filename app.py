from flask import Flask, render_template_string, request, redirect, url_for, session, g
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "finca_iberia_clave_segura_2026"

# ================== USUARIOS ==================
usuarios = {
    "Administrador": {"clave": "guayacan", "rol": "jefe"},  # 👑 TÚ
    "Adrian": {"clave": "1990", "rol": "miembro"},
    "Mincho": {"clave": "1984", "rol": "miembro"},
    "Erick": {"clave": "1994", "rol": "miembro"},
    # Agrega más así: "Nombre": {"clave": "pass", "rol": "miembro"},
}

DATABASE = 'finca_iberia.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS animales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                arete TEXT NOT NULL UNIQUE,
                nombre TEXT,
                raza TEXT,
                sexo TEXT,
                fecha_nacimiento TEXT,
                peso REAL,
                ubicacion TEXT,
                duenno TEXT,
                vacunas TEXT,
                tratamientos TEXT,
                historial_veterinario TEXT,
                reproduccion TEXT,
                produccion_leche TEXT,
                observaciones TEXT,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.commit()

@app.before_request
def verificar_login():
    rutas_publicas = ['login', 'inicio']
    if request.endpoint not in rutas_publicas and 'usuario' not in session:
        return redirect(url_for('login'))

@app.route('/')
def inicio():
    if 'usuario' in session:
        return redirect(url_for('lista'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        usu = request.form['usuario']
        cla = request.form['clave']
        if usu in usuarios and usuarios[usu]['clave'] == cla:
            session['usuario'] = usu
            session['rol'] = usuarios[usu]['rol']
            return redirect(url_for('lista'))
        return render_template_string("""
        <html style="background:#e8f5e9; font-family:sans-serif;">
        <body style="max-width:400px; margin:50px auto; padding:20px; background:white; border-radius:12px; box-shadow:0 4px 12px #0002;">
            <h2 style="color:#2e7d32; text-align:center;">🐄 Finca Iberia</h2>
            <p style="color:red; text-align:center;">Usuario o clave incorrectos</p>
            <a href="/login" style="display:block; text-align:center; color:#2e7d32;">Volver a intentar</a>
        </body></html>
        """)
    return render_template_string("""
    <html style="background:#e8f5e9; font-family:sans-serif;">
    <body style="max-width:400px; margin:80px auto; padding:30px; background:white; border-radius:12px; box-shadow:0 4px 12px #0002;">
        <h1 style="color:#2e7d32; text-align:center;">🐄 Finca Iberia</h1>
        <h3 style="text-align:center; color:#555;">Iniciar Sesión</h3>
        <form method="POST">
            <div style="margin:15px 0;">
                <label>Usuario:</label>
                <input name="usuario" required style="width:100%; padding:10px; margin-top:5px; border:1px solid #ccc; border-radius:6px;">
            </div>
            <div style="margin:15px 0;">
                <label>Contraseña:</label>
                <input type="password" name="clave" required style="width:100%; padding:10px; margin-top:5px; border:1px solid #ccc; border-radius:6px;">
            </div>
            <button type="submit" style="width:100%; padding:12px; background:#2e7d32; color:white; border:none; border-radius:6px; font-size:16px;">Entrar</button>
        </form>
    </body></html>
    """)

@app.route('/logout')
def salir():
    session.clear()
    return redirect(url_for('login'))

@app.route('/lista')
def lista():
    db = get_db()
    busqueda = request.args.get('buscar','')
    if busqueda:
        animales = db.execute(
            "SELECT id, arete, nombre, raza, duenno FROM animales WHERE arete LIKE ? OR nombre LIKE ? ORDER BY arete",
            (f'%{busqueda}%', f'%{busqueda}%')
        ).fetchall()
    else:
        animales = db.execute("SELECT id, arete, nombre, raza, duenno FROM animales ORDER BY arete").fetchall()

    return render_template_string("""
    <html style="background:#e8f5e9; font-family:sans-serif;">
    <body style="max-width:900px; margin:0 auto; padding:20px;">
        <div style="background:white; padding:20px; border-radius:12px; box-shadow:0 4px 12px #0002; margin-bottom:20px;">
            <h1 style="color:#2e7d32; margin:0;">🐄 Finca Iberia — Lista de Animales</h1>
            <p>Bienvenido {{ session.usuario }} | <a href="/logout" style="color:red;">Salir</a></p>
        </div>

        <div style="background:white; padding:15px; border-radius:12px; margin-bottom:20px;">
            <form method="GET" action="/lista">
                <input type="text" name="buscar" placeholder="🔍 Buscar por arete o nombre..." value="{{ busqueda }}"
                style="width:70%; padding:10px; border:1px solid #ccc; border-radius:6px; font-size:16px;">
                <button type="submit" style="padding:10px 20px; background:#2e7d32; color:white; border:none; border-radius:6px;">Buscar</button>
                <a href="/lista" style="padding:10px 15px; background:#888; color:white; border-radius:6px; text-decoration:none; display:inline-block; margin-left:5px;">Ver todos</a>
            </form>
        </div>

        <div style="margin-bottom:15px;">
            <a href="/registrar" style="padding:12px 25px; background:#2e7d32; color:white; border-radius:6px; text-decoration:none; font-weight:bold;">➕ Registrar Nuevo Animal</a>
        </div>

        <div style="background:white; padding:20px; border-radius:12px; box-shadow:0 4px 12px #0002;">
            <h3>Número de arete — Nombre / Raza / Dueño</h3>
            {% if animales %}
                <ul style="list-style:none; padding:0;">
                {% for a in animales %}
                    <li style="padding:12px; border-bottom:1px solid #ddd;">
                        <a href="/detalle/{{a['id']}}" style="color:#2e7d32; font-weight:bold; font-size:18px; text-decoration:none;">
                            {{ a['arete'] }}
                        </a>
                        — {{ a['nombre'] or 'Sin nombre' }} | {{ a['raza'] or 'Sin raza' }} | Dueño: {{ a['duenno'] or 'No asignado' }}
                    </li>
                {% endfor %}
                </ul>
            {% else %}
                <p style="color:#666;">No hay animales registrados</p>
            {% endif %}
        </div>
    </body></html>
    """, animales=animales, busqueda=busqueda)

@app.route('/registrar', methods=['GET','POST'])
def registrar():
    if request.method == 'POST':
        db = get_db()
        try:
            db.execute('''INSERT INTO animales 
                (arete, nombre, raza, sexo, fecha_nacimiento, peso, ubicacion, duenno,
                 vacunas, tratamientos, historial_veterinario, reproduccion, produccion_leche, observaciones)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (
                    request.form['arete'],
                    request.form['nombre'],
                    request.form['raza'],
                    request.form['sexo'],
                    request.form['fecha_nacimiento'],
                    request.form['peso'],
                    request.form['ubicacion'],
                    request.form['duenno'],
                    request.form['vacunas'],
                    request.form['tratamientos'],
                    request.form['historial_veterinario'],
                    request.form['reproduccion'],
                    request.form['produccion_leche'],
                    request.form['observaciones']
                )
            )
            db.commit()
            return redirect(url_for('lista'))
        except Exception as e:
            return f"Error: El número de arete ya existe"

    return render_template_string("""
    <html style="background:#e8f5e9; font-family:sans-serif;">
    <body style="max-width:700px; margin:0 auto; padding:20px;">
        <div style="background:white; padding:25px; border-radius:12px; box-shadow:0 4px 12px #0002;">
            <h2 style="color:#2e7d32;">➕ Registrar Animal — Finca Iberia</h2>
            <a href="/lista" style="color:#2e7d32;">← Volver a la lista</a><br><br>
            <form method="POST">
                <div style="margin:10px 0;">
                    <label>🏷️ Número de Arete *:</label>
                    <input name="arete" required style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;">
                </div>
                <div style="margin:10px 0;">
                    <label>Nombre:</label>
                    <input name="nombre" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;">
                </div>
                <div style="margin:10px 0;">
                    <label>🧬 Raza / Cruces:</label>
                    <input name="raza" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;">
                </div>
                <div style="margin:10px 0;">
                    <label>🚻 Sexo:</label>
                    <select name="sexo" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;">
                        <option value="">Seleccionar</option>
                        <option>Hembra</option>
                        <option>Macho</option>
                    </select>
                </div>
                <div style="margin:10px 0;">
                    <label>🎂 Fecha Nacimiento:</label>
                    <input type="date" name="fecha_nacimiento" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;">
                </div>
                <div style="margin:10px 0;">
                    <label>⚖️ Peso (kg):</label>
                    <input type="number" step="0.1" name="peso" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;">
                </div>
                <div style="margin:10px 0;">
                    <label>📍 Ubicación / Potrero:</label>
                    <input name="ubicacion" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;">
                </div>
                <div style="margin:10px 0;">
                    <label>👤 Dueño del animal:</label>
                    <input name="duenno" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;">
                </div>
                <div style="margin:10px 0;">
                    <label>💉 Vacunas:</label>
                    <textarea name="vacunas" rows="2" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;"></textarea>
                </div>
                <div style="margin:10px 0;">
                    <label>💊 Tratamientos:</label>
                    <textarea name="tratamientos" rows="2" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;"></textarea>
                </div>
                <div style="margin:10px 0;">
                    <label>🩺 Historial Veterinario:</label>
                    <textarea name="historial_veterinario" rows="2" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;"></textarea>
                </div>
                <div style="margin:10px 0;">
                    <label>🐮 Reproducción / Nacimientos:</label>
                    <textarea name="reproduccion" rows="2" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;"></textarea>
                </div>
                <div style="margin:10px 0;">
                    <label>🥛 Producción de Leche:</label>
                    <textarea name="produccion_leche" rows="2" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;"></textarea>
                </div>
                <div style="margin:10px 0;">
                    <label>📝 Observaciones:</label>
                    <textarea name="observaciones" rows="2" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;"></textarea>
                </div>
                <button type="submit" style="padding:12px 30px; background:#2e7d32; color:white; border:none; border-radius:6px; font-size:16px;">💾 Guardar Animal</button>
            </form>
        </div>
    </body></html>
    """)

@app.route('/detalle/<int:animal_id>')
def detalle(animal_id):
    db = get_db()
    an = db.execute("SELECT * FROM animales WHERE id=?", (animal_id,)).fetchone()
    return render_template_string("""
    <html style="background:#e8f5e9; font-family:sans-serif;">
    <body style="max-width:700px; margin:0 auto; padding:20px;">
        <div style="background:white; padding:25px; border-radius:12px; box-shadow:0 4px 12px #0002;">
            <h2 style="color:#2e7d32;">🐄 Detalle del Animal — Finca Iberia</h2>
            <a href="/lista" style="color:#2e7d32;">← Volver a la lista</a><br><br>

            <table style="width:100%; border-collapse:collapse;">
                <tr><td style="padding:8px; font-weight:bold; width:40%;">🏷️ Arete:</td><td>{{ an['arete'] }}</td></tr>
                <tr style="background:#f9f9f9;"><td style="padding:8px; font-weight:bold;">Nombre:</td><td>{{ an['nombre'] or '—' }}</td></tr>
                <tr><td style="padding:8px; font-weight:bold;">🧬 Raza:</td><td>{{ an['raza'] or '—' }}</td></tr>
                <tr style="background:#f9f9f9;"><td style="padding:8px; font-weight:bold;">🚻 Sexo:</td><td>{{ an['sexo'] or '—' }}</td></tr>
                <tr><td style="padding:8px; font-weight:bold;">🎂 Nacimiento:</td><td>{{ an['fecha_nacimiento'] or '—' }}</td></tr>
                <tr style="background:#f9f9f9;"><td style="padding:8px; font-weight:bold;">⚖️ Peso:</td><td>{{ an['peso'] or '—' }} kg</td></tr>
                <tr><td style="padding:8px; font-weight:bold;">📍 Ubicación:</td><td>{{ an['ubicacion'] or '—' }}</td></tr>
                <tr style="background:#f9f9f9;"><td style="padding:8px; font-weight:bold;">👤 Dueño:</td><td>{{ an['duenno'] or 'No asignado' }}</td></tr>
                <tr><td style="padding:8px; font-weight:bold;">💉 Vacunas:</td><td>{{ an['vacunas'] or '—' }}</td></tr>
                <tr style="background:#f9f9f9;"><td style="padding:8px; font-weight:bold;">💊 Tratamientos:</td><td>{{ an['tratamientos'] or '—' }}</td></tr>
                <tr><td style="padding:8px; font-weight:bold;">🩺 Historial Vet:</td><td>{{ an['historial_veterinario'] or '—' }}</td></tr>
                <tr style="background:#f9f9f9;"><td style="padding:8px; font-weight:bold;">🐮 Reproducción:</td><td>{{ an['reproduccion'] or '—' }}</td></tr>
                <tr><td style="padding:8px; font-weight:bold;">🥛 Producción Leche:</td><td>{{ an['produccion_leche'] or '—' }}</td></tr>
                <tr style="background:#f9f9f9;"><td style="padding:8px; font-weight:bold;">📝 Observaciones:</td><td>{{ an['observaciones'] or '—' }}</td></tr>
            </table>
            <br>
            <a href="/editar/{{an['id']}}" style="padding:10px 20px; background:#f57c00; color:white; border-radius:6px; text-decoration:none;">✏️ Editar</a>
            {% if session.rol == 'jefe' %}
            <a href="/eliminar/{{an['id']}}" onclick="return confirm('¿Eliminar este animal?')" style="padding:10px 20px; background:#d32f2f; color:white; border-radius:6px; text-decoration:none; margin-left:10px;">🗑️ Eliminar</a>
            {% endif %}
        </div>
    </body></html>
    """, an=an)

@app.route('/editar/<int:animal_id>', methods=['GET','POST'])
def editar(animal_id):
    db = get_db()
    if request.method == 'POST':
        db.execute('''UPDATE animales SET
            arete=?, nombre=?, raza=?, sexo=?, fecha_nacimiento=?, peso=?, ubicacion=?, duenno=?,
            vacunas=?, tratamientos=?, historial_veterinario=?, reproduccion=?, produccion_leche=?, observaciones=?
            WHERE id=?''',
            (
                request.form['arete'],
                request.form['nombre'],
                request.form['raza'],
                request.form['sexo'],
                request.form['fecha_nacimiento'],
                request.form['peso'],
                request.form['ubicacion'],
                request.form['duenno'],
                request.form['vacunas'],
                request.form['tratamientos'],
                request.form['historial_veterinario'],
                request.form['reproduccion'],
                request.form['produccion_leche'],
                request.form['observaciones'],
                animal_id
            )
        )
        db.commit()
        return redirect(url_for('detalle', animal_id=animal_id))

    an = db.execute("SELECT * FROM animales WHERE id=?", (animal_id,)).fetchone()
    return render_template_string("""
    <html style="background:#e8f5e9; font-family:sans-serif;">
    <body style="max-width:700px; margin:0 auto; padding:20px;">
        <div style="background:white; padding:25px; border-radius:12px;">
            <h2 style="color:#f57c00;">✏️ Editar Animal</h2>
            <a href="/detalle/{{an['id']}}" style="color:#2e7d32;">← Volver</a><br><br>
            <form method="POST">
                <div style="margin:10px 0;">
                    <label>🏷️ Número de Arete *:</label>
                    <input name="arete" value="{{ an['arete'] }}" required style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;">
                </div>
                <div style="margin:10px 0;">
                    <label>Nombre:</label>
                    <input name="nombre" value="{{ an['nombre'] or '' }}" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;">
                </div>
                <div style="margin:10px 0;">
                    <label>🧬 Raza:</label>
                    <input name="raza" value="{{ an['raza'] or '' }}" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;">
                </div>
                <div style="margin:10px 0;">
                    <label>🚻 Sexo:</label>
                    <select name="sexo" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;">
                        <option value="">Seleccionar</option>
                        <option {% if an['sexo']=='Hembra' %}selected{% endif %}>Hembra</option>
                        <option {% if an['sexo']=='Macho' %}selected{% endif %}>Macho</option>
                    </select>
                </div>
                <div style="margin:10px 0;">
                    <label>🎂 Fecha Nacimiento:</label>
                    <input type="date" name="fecha_nacimiento" value="{{ an['fecha_nacimiento'] or '' }}" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;">
                </div>
                <div style="margin:10px 0;">
                    <label>⚖️ Peso (kg):</label>
                    <input type="number" step="0.1" name="peso" value="{{ an['peso'] or '' }}" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;">
                </div>
                <div style="margin:10px 0;">
                    <label>📍 Ubicación:</label>
                    <input name="ubicacion" value="{{ an['ubicacion'] or '' }}" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;">
                </div>
                <div style="margin:10px 0;">
                    <label>👤 Dueño:</label>
                    <input name="duenno" value="{{ an['duenno'] or '' }}" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;">
                </div>
                <div style="margin:10px 0;">
                    <label>💉 Vacunas:</label>
                    <textarea name="vacunas" rows="2" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;">{{ an['vacunas'] or '' }}</textarea>
                </div>
                <div style="margin:10px 0;">
                    <label>💊 Tratamientos:</label>
                    <textarea name="tratamientos" rows="2" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;">{{ an['tratamientos'] or '' }}</textarea>
                </div>
                <div style="margin:10px 0;">
                    <label>🩺 Historial Vet:</label>
                    <textarea name="historial_veterinario" rows="2" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;">{{ an['historial_veterinario'] or '' }}</textarea>
                </div>
                <div style="margin:10px 0;">
                    <label>🐮 Reproducción:</label>
                    <textarea name="reproduccion" rows="2" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;">{{ an['reproduccion'] or '' }}</textarea>
                </div>
                <div style="margin:10px 0;">
                    <label>🥛 Producción Leche:</label>
                    <textarea name="produccion_leche" rows="2" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;">{{ an['produccion_leche'] or '' }}</textarea>
                </div>
                <div style="margin:10px 0;">
                    <label>📝 Observaciones:</label>
                    <textarea name="observaciones" rows="2" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px;">{{ an['observaciones'] or '' }}</textarea>
                </div>
                <button type="submit" style="padding:12px 30px; background:#2e7d32; color:white; border:none; border-radius:6px;">💾 Guardar Cambios</button>
            </form>
        </div>
    </body></html>
    """, an=an)

@app.route('/eliminar/<int:animal_id>')
def eliminar(animal_id):
    if session.get('rol') != 'jefe':
        return "No tienes permiso"
    db = get_db()
    db.execute("DELETE FROM animales WHERE id=?", (animal_id,))
    db.commit()
    return redirect(url_for('lista'))

init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)