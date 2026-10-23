from flask import Flask, render_template_string, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "finca_iberia_clave_segura_2026"

# ================== USUARIOS ==================
usuarios = {
    "admin": {"clave": "123456", "rol": "jefe"},
    "familia": {"clave": "123456", "rol": "miembro"}
}

# ================== BASE DE DATOS ==================
def init_db():
    conn = sqlite3.connect('animales.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS animales
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  numero TEXT NOT NULL,
                  tipo TEXT NOT NULL,
                  raza TEXT,
                  fecha_nacimiento TEXT,
                  peso TEXT,
                  genero TEXT,
                  color TEXT,
                  observaciones TEXT,
                  dueño TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()

# ================== PÁGINA DE INICIO DE SESIÓN ==================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip()
        clave = request.form.get('clave', '').strip()
        
        for u, datos in usuarios.items():
            if u.lower() == usuario.lower() and datos['clave'] == clave:
                session['usuario'] = u
                session['rol'] = datos['rol']
                return redirect(url_for('lista'))
        
        return render_template_string(LOGIN_HTML, error=True)
    
    return render_template_string(LOGIN_HTML)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ================== LISTA DE ANIMALES ==================
@app.route('/')
def lista():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    buscar = request.args.get('buscar', '').strip()
    
    conn = sqlite3.connect('animales.db')
    c = conn.cursor()
    
    if buscar:
        c.execute("SELECT * FROM animales WHERE numero LIKE ? OR tipo LIKE ? OR dueño LIKE ? ORDER BY numero", 
                  (f'%{buscar}%', f'%{buscar}%', f'%{buscar}%'))
    else:
        c.execute("SELECT * FROM animales ORDER BY numero DESC")
    
    animales = c.fetchall()
    conn.close()
    
    return render_template_string(LISTA_HTML, animales=animales, buscar=buscar)

# ================== VER DETALLES DE UN ANIMAL ==================
@app.route('/animal/<int:id>')
def ver_animal(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('animales.db')
    c = conn.cursor()
    c.execute("SELECT * FROM animales WHERE id = ?", (id,))
    animal = c.fetchone()
    conn.close()
    
    if not animal:
        return "Animal no encontrado", 404
    
    return render_template_string(DETALLE_HTML, animal=animal)

# ================== FORMULARIO DE REGISTRO ==================
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        numero = request.form.get('numero')
        tipo = request.form.get('tipo')
        raza = request.form.get('raza')
        fecha_nacimiento = request.form.get('fecha_nacimiento')
        peso = request.form.get('peso')
        genero = request.form.get('genero')
        color = request.form.get('color')
        observaciones = request.form.get('observaciones')
        dueño = request.form.get('dueño')
        
        conn = sqlite3.connect('animales.db')
        c = conn.cursor()
        c.execute('''INSERT INTO animales 
                     (numero, tipo, raza, fecha_nacimiento, peso, genero, color, observaciones, dueño)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (numero, tipo, raza, fecha_nacimiento, peso, genero, color, observaciones, dueño))
        conn.commit()
        conn.close()
        
        return redirect(url_for('lista'))
    
    return render_template_string(REGISTRO_HTML)

# ================== EDITAR ANIMAL ==================
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('animales.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        numero = request.form.get('numero')
        tipo = request.form.get('tipo')
        raza = request.form.get('raza')
        fecha_nacimiento = request.form.get('fecha_nacimiento')
        peso = request.form.get('peso')
        genero = request.form.get('genero')
        color = request.form.get('color')
        observaciones = request.form.get('observaciones')
        dueño = request.form.get('dueño')
        
        c.execute('''UPDATE animales SET numero=?, tipo=?, raza=?, fecha_nacimiento=?, 
                     peso=?, genero=?, color=?, observaciones=?, dueño=? WHERE id=?''',
                  (numero, tipo, raza, fecha_nacimiento, peso, genero, color, observaciones, dueño, id))
        conn.commit()
        conn.close()
        return redirect(url_for('ver_animal', id=id))
    
    c.execute("SELECT * FROM animales WHERE id = ?", (id,))
    animal = c.fetchone()
    conn.close()
    
    if not animal:
        return "Animal no encontrado", 404
    
    return render_template_string(EDITAR_HTML, animal=animal)

# ================== ELIMINAR ANIMAL ==================
@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('animales.db')
    c = conn.cursor()
    c.execute("DELETE FROM animales WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('lista'))

# ================== PLANTILLAS HTML ==================

ESTILOS = '''
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; font-family: Arial, sans-serif; }
    body { 
        background: linear-gradient(rgba(255,255,255,0.85), rgba(255,255,255,0.85)), 
                    url("https://images.unsplash.com/photo-1500382017920-7a9b2d285c06?w=1200");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        min-height: 100vh;
        padding: 20px;
    }
    .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    h1 { text-align: center; color: #2c5f2d; margin-bottom: 30px; }
    h2 { color: #4a7c4b; margin-bottom: 20px; }
    .nav { display: flex; gap: 10px; margin-bottom: 25px; flex-wrap: wrap; }
    .btn { padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; text-decoration: none; display: inline-block; transition: 0.3s; }
    .btn-nuevo { background: #2c5f2d; color: white; }
    .btn-nuevo:hover { background: #1f4520; }
    .btn-editar { background: #f9a825; color: white; }
    .btn-editar:hover { background: #f57c00; }
    .btn-eliminar { background: #d32f2f; color: white; }
    .btn-eliminar:hover { background: #b71c1c; }
    .btn-volver { background: #6c757d; color: white; }
    .btn-volver:hover { background: #545b62; }
    .btn-salir { background: #343a40; color: white; }
    .buscador { width: 100%; padding: 12px; margin-bottom: 20px; border: 2px solid #ddd; border-radius: 6px; font-size: 16px; }
    .lista { width: 100%; border-collapse: collapse; margin-top: 15px; }
    .lista th, .lista td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
    .lista th { background: #2c5f2d; color: white; }
    .lista tr:hover { background: #f1f8f1; }
    .lista a { color: #2c5f2d; font-weight: bold; text-decoration: none; }
    .form-group { margin-bottom: 15px; }
    label { display: block; margin-bottom: 5px; font-weight: bold; color: #333; }
    input, select, textarea { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 15px; }
    .detail-row { padding: 10px 0; border-bottom: 1px solid #eee; }
    .label { font-weight: bold; display: inline-block; width: 120px; color: #2c5f2d; }
    .error { color: #d32f2f; text-align: center; margin: 15px 0; }
    .login-box { max-width: 400px; margin: 100px auto; padding: 30px; background: white; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center; }
    .login-box h1 { margin-bottom: 25px; }
</style>
'''

LOGIN_HTML = ESTILOS + '''
<div class="login-box">
    <h1>🌿 Finca Iberia</h1>
    <h2>Iniciar Sesión</h2>
    {% if error %}
    <p class="error">Usuario o clave incorrectos</p>
    {% endif %}
    <form method="post">
        <div class="form-group">
            <label>Usuario:</label>
            <input type="text" name="usuario" required autofocus>
        </div>
        <div class="form-group">
            <label>Contraseña:</label>
            <input type="password" name="clave" required>
        </div>
        <button type="submit" class="btn btn-nuevo" style="width:100%; margin-top:10px;">Ingresar</button>
    </form>
</div>
'''

LISTA_HTML = ESTILOS + '''
<div class="container">
    <h1>🐄 Finca Iberia — Lista de Animales</h1>
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
        <a href="{{ url_for('registro') }}" class="btn btn-nuevo">+ Registrar Nuevo</a>
        <a href="{{ url_for('logout') }}" class="btn btn-salir">Cerrar Sesión</a>
    </div>
    
    <form method="get" style="margin-top:20px;">
        <input type="text" name="buscar" class="buscador" placeholder="🔍 Buscar por número, tipo o dueño..." value="{{ buscar }}">
    </form>
    
    {% if animales %}
    <table class="lista">
        <tr>
            <th>Número</th>
            <th>Tipo</th>
            <th>Raza</th>
            <th>Dueño</th>
        </tr>
        {% for animal in animales %}
        <tr>
            <td><a href="{{ url_for('ver_animal', id=animal[0]) }}">{{ animal[1] }}</a></td>
            <td>{{ animal[2] }}</td>
            <td>{{ animal[3] or '-' }}</td>
            <td>{{ animal[9] }}</td>
        </tr>
        {% endfor %}
    </table>
    {% else %}
    <p style="text-align:center; padding:30px; color:#666;">No hay animales registrados. ¡Registra el primero con el botón arriba!</p>
    {% endif %}
</div>
'''

DETALLE_HTML = ESTILOS + '''
<div class="container">
    <h1>🐂 Datos del Animal — {{ animal[1] }}</h1>
    
    <div class="detail-row">
        <span class="label">🔢 Número:</span>
        <span class="value">{{ animal[1] }}</span>
    </div>
    <div class="detail-row">
        <span class="label">🐄 Tipo:</span>
        <span class="value">{{ animal[2] }}</span>
    </div>
    <div class="detail-row">
        <span class="label">🐮 Raza:</span>
        <span class="value">{{ animal[3] or '-' }}</span>
    </div>
    <div class="detail-row">
        <span class="label">📅 Nacimiento:</span>
        <span class="value">{{ animal[4] or '-' }}</span>
    </div>
    <div class="detail-row">
        <span class="label">⚖️ Peso:</span>
        <span class="value">{{ animal[5] or '-' }}</span>
    </div>
    <div class="detail-row">
        <span class="label">🚻 Género:</span>
        <span class="value">{{ animal[6] or '-' }}</span>
    </div>
    <div class="detail-row">
        <span class="label">🎨 Color:</span>
        <span class="value">{{ animal[7] or '-' }}</span>
    </div>
    <div class="detail-row">
        <span class="label">👤 Dueño:</span>
        <span class="value">{{ animal[9] }}</span>
    </div>
    <div class="detail-row">
        <span class="label">📝 Observaciones:</span>
        <span class="value">{{ animal[8] or '-' }}</span>
    </div>
    
    <div style="margin-top:30px; display:flex; gap:10px; flex-wrap:wrap;">
        <a href="{{ url_for('editar', id=animal[0]) }}" class="btn btn-editar">✏️ Editar</a>
        <form action="{{ url_for('eliminar', id=animal[0]) }}" method="post" onsubmit="return confirm('⚠️ ¿Seguro que quieres ELIMINAR este animal?\\nEsta acción NO se puede deshacer.');" style="display:inline;">
            <button type="submit" class="btn btn-eliminar">🗑️ Eliminar</button>
        </form>
        <a href="{{ url_for('lista') }}" class="btn btn-volver">← Volver a la Lista</a>
    </div>
</div>
'''

REGISTRO_HTML = ESTILOS + '''
<div class="container">
    <h1>➕ Registrar Nuevo Animal</h1>
    
    <form method="post">
        <div class="form-group">
            <label>🔢 Número / Identificación:</label>
            <input type="text" name="numero" required>
        </div>
        <div class="form-group">
            <label>🐄 Tipo de animal:</label>
            <input type="text" name="tipo" placeholder="Ej: Vaca, Toro, Ternera..." required>
        </div>
        <div class="form-group">
            <label>🐮 Raza:</label>
            <input type="text" name="raza">
        </div>
        <div class="form-group">
            <label>📅 Fecha de nacimiento:</label>
            <input type="date" name="fecha_nacimiento">
        </div>
        <div class="form-group">
            <label>⚖️ Peso:</label>
            <input type="text" name="peso" placeholder="Ej: 450 kg">
        </div>
        <div class="form-group">
            <label>🚻 Género:</label>
            <select name="genero">
                <option value="">Seleccionar...</option>
                <option value="Macho">Macho</option>
                <option value="Hembra">Hembra</option>
            </select>
        </div>
        <div class="form-group">
            <label>🎨 Color / Señas particulares:</label>
            <input type="text" name="color">
        </div>
        <div class="form-group">
            <label>👤 Dueño:</label>
            <input type="text" name="dueño" required>
        </div>
        <div class="form-group">
            <label>📝 Observaciones:</label>
            <textarea name="observaciones" rows="4"></textarea>
        </div>
        
        <div style="margin-top:25px; display:flex; gap:10px;">
            <button type="submit" class="btn btn-nuevo">✅ Guardar Animal</button>
            <a href="{{ url_for('lista') }}" class="btn btn-volver">← Cancelar</a>
        </div>
    </form>
</div>
'''

EDITAR_HTML = ESTILOS + '''
<div class="container">
    <h1>✏️ Editar Animal — {{ animal[1] }}</h1>
    
    <form method="post">
        <div class="form-group">
            <label>🔢 Número / Identificación:</label>
            <input type="text" name="numero" value="{{ animal[1] }}" required>
        </div>
        <div class="form-group">
            <label>🐄 Tipo de animal:</label>
            <input type="text" name="tipo" value="{{ animal[2] }}" required>
        </div>
        <div class="form-group">
            <label>🐮 Raza:</label>
            <input type="text" name="raza" value="{{ animal[3] or '' }}">
        </div>
        <div class="form-group">
            <label>📅 Fecha de nacimiento:</label>
            <input type="date" name="fecha_nacimiento" value="{{ animal[4] or '' }}">
        </div>
        <div class="form-group">
            <label>⚖️ Peso:</label>
            <input type="text" name="peso" value="{{ animal[5] or '' }}">
        </div>
        <div class="form-group">
            <label>🚻 Género:</label>
            <select name="genero">
                <option value="">Seleccionar...</option>
                <option value="Macho" {{ 'selected' if animal[6] == 'Macho' else '' }}>Macho</option>
                <option value="Hembra" {{ 'selected' if animal[6] == 'Hembra' else '' }}>Hembra</option>
            </select>
        </div>
        <div class="form-group">
            <label>🎨 Color / Señas particulares:</label>
            <input type="text" name="color" value="{{ animal[7] or '' }}">
        </div>
        <div class="form-group">
            <label>👤 Dueño:</label>
            <input type="text" name="dueño" value="{{ animal[9] }}" required>
        </div>
        <div class="form-group">
            <label>📝 Observaciones:</label>
            <textarea name="observaciones" rows="4">{{ animal[8] or '' }}</textarea>
        </div>
        
        <div style="margin-top:25px; display:flex; gap:10px;">
            <button type="submit" class="btn btn-nuevo">💾 Guardar Cambios</button>
            <a href="{{ url_for('ver_animal', id=animal[0]) }}" class="btn btn-volver">← Cancelar</a>
        </div>
    </form>
</div>
'''

if __name__ == '__main__':
    app.run(debug=True)