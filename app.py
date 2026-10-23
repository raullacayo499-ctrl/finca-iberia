from flask import Flask, render_template_string, request, redirect, url_for, session, g
import sqlite3

app = Flask(__name__)
app.secret_key = "finca_2026_clave_segura"

# ================== USUARIOS ==================
usuarios = {
    "Administrador": {"clave": "guayacan", "rol": "jefe"},
    "Adrian": {"clave": "1990", "rol": "miembro"},
    "Mincho": {"clave": "1984", "rol": "miembro"},
    "Erick": {"clave": "1994", "rol": "miembro"}
}

# ================== BASE DE DATOS ==================
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('finca.db')
        db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS animales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT NOT NULL UNIQUE,
                madre TEXT,
                padre TEXT,
                estado TEXT,
                ubicacion TEXT,
                sexo TEXT,
                raza TEXT,
                edad TEXT,
                peso TEXT,
                observaciones TEXT
            )
        ''')
        db.commit()

@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# ================== PÁGINAS ==================
@app.route('/')
def inicio():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('lista_animales'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    mensaje = ""
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip()
        clave = request.form.get('clave', '').strip()
        
        # Convertir a minúsculas para evitar errores de mayúsculas
        usuario_min = usuario.lower()
        usuario_en_lista = None
        
        for u in usuarios:
            if u.lower() == usuario_min:
                usuario_en_lista = u
                break
        
        if usuario_en_lista and usuarios[usuario_en_lista]['clave'] == clave:
            session['usuario'] = usuario_en_lista
            session['rol'] = usuarios[usuario_en_lista]['rol']
            return redirect(url_for('lista_animales'))
        else:
            mensaje = "❌ Usuario o contraseña incorrectos. Inténtalo de nuevo."
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Iniciar Sesión - Finca Iberia</title>
    <style>
        * { box-sizing: border-box; font-family: Arial, sans-serif; }
        body { 
            background: linear-gradient(135deg, #4a7c59 0%, #2c4a35 100%);
            min-height: 100vh;
            margin: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .login-box {
            background: white;
            border-radius: 12px;
            padding: 30px;
            width: 100%;
            max-width: 400px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        }
        h2 { text-align: center; color: #2c4a35; margin-bottom: 25px; }
        .campo { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #333; font-weight: bold; }
        input {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 16px;
        }
        input:focus { outline: none; border-color: #4a7c59; }
        button {
            width: 100%;
            padding: 14px;
            background: #4a7c59;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
        }
        button:hover { background: #3a6347; }
        .error { color: #d63031; text-align: center; margin-bottom: 15px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>🐄 Finca Iberia</h2>
        <h3 style="text-align:center; color:#555; margin-top:-10px;">Iniciar Sesión</h3>
        {% if mensaje %}<div class="error">{{ mensaje }}</div>{% endif %}
        <form method="POST">
            <div class="campo">
                <label>Usuario:</label>
                <input type="text" name="usuario" required autocomplete="off">
            </div>
            <div class="campo">
                <label>Contraseña:</label>
                <input type="password" name="clave" required>
            </div>
            <button type="submit">Entrar</button>
        </form>
    </div>
</body>
</html>
    ''', mensaje=mensaje)

@app.route('/lista')
def lista_animales():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM animales ORDER BY numero')
    animales = cursor.fetchall()
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lista de Animales - Finca Iberia</title>
    <style>
        * { box-sizing: border-box; font-family: Arial, sans-serif; margin: 0; padding: 0; }
        body { 
            background: #f0f7f0;
            min-height: 100vh;
            padding: 20px;
        }
        .header {
            background: #4a7c59;
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }
        .header h1 { font-size: 22px; }
        .btn {
            padding: 10px 18px;
            border: none;
            border-radius: 6px;
            font-size: 15px;
            font-weight: bold;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }
        .btn-nuevo { background: #27ae60; color: white; }
        .btn-nuevo:hover { background: #219653; }
        .btn-salir { background: #c0392b; color: white; }
        .btn-salir:hover { background: #a93226; }
        
        .buscador {
            margin-bottom: 20px;
        }
        .buscador input {
            width: 100%;
            padding: 12px;
            border: 2px solid #4a7c59;
            border-radius: 8px;
            font-size: 16px;
        }
        
        .lista-container {
            background: white;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .animal-link {
            display: block;
            padding: 14px;
            border-bottom: 1px solid #eee;
            color: #2c4a35;
            text-decoration: none;
            font-size: 16px;
        }
        .animal-link:last-child { border-bottom: none; }
        .animal-link:hover { background: #e8f5e9; }
        .numero-animal { font-weight: bold; font-size: 18px; }
        .vacio { text-align: center; color: #777; padding: 40px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🐄 Lista de Animales</h1>
        <div>
            <a href="{{ url_for('nuevo_animal') }}" class="btn btn-nuevo">+ Registrar Nuevo</a>
            <a href="{{ url_for('logout') }}" class="btn btn-salir">Cerrar Sesión</a>
        </div>
    </div>

    <div class="buscador">
        <input type="text" id="buscar" placeholder="🔍 Buscar por número..." onkeyup="filtrar()">
    </div>

    <div class="lista-container">
        {% if animales %}
            {% for a in animales %}
                <a href="{{ url_for('ver_animal', id=a['id']) }}" class="animal-link" id="fila-{{ a['numero'] }}">
                    <span class="numero-animal">#{{ a['numero'] }}</span> — {{ a['raza'] or 'Sin raza' }} — {{ a['sexo'] or 'Sin sexo' }}
                </a>
            {% endfor %}
        {% else %}
            <p class="vacio">No hay animales registrados todavía.<br>Haz clic en "+ Registrar Nuevo" para empezar.</p>
        {% endif %}
    </div>

    <script>
        function filtrar() {
            var busqueda = document.getElementById('buscar').value.toLowerCase();
            var enlaces = document.querySelectorAll('.animal-link');
            enlaces.forEach(function(enlace) {
                var texto = enlace.textContent.toLowerCase();
                if (texto.indexOf(busqueda) !== -1) {
                    enlace.style.display = 'block';
                } else {
                    enlace.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>
    ''', animales=animales)

@app.route('/animal/<id>')
def ver_animal(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM animales WHERE id = ?', (id,))
    animal = cursor.fetchone()
    
    if not animal:
        return "Animal no encontrado — <a href='" + url_for('lista_animales') + "'>Volver a la lista</a>"
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Animal #{{ animal['numero'] }} - Finca Iberia</title>
    <style>
        * { box-sizing: border-box; font-family: Arial, sans-serif; margin: 0; padding: 0; }
        body { 
            background: #f0f7f0;
            min-height: 100vh;
            padding: 20px;
        }
        .btn-volver {
            display: inline-block;
            background: #666;
            color: white;
            padding: 10px 18px;
            border-radius: 6px;
            text-decoration: none;
            margin-bottom: 20px;
        }
        .btn-volver:hover { background: #444; }
        
        .ficha {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            max-width: 600px;
            margin: 0 auto;
        }
        .ficha h2 {
            text-align: center;
            color: #4a7c59;
            margin-bottom: 25px;
            font-size: 24px;
        }
        .dato {
            padding: 12px 0;
            border-bottom: 1px solid #eee;
        }
        .dato:last-child { border-bottom: none; }
        .etiqueta {
            font-weight: bold;
            color: #2c4a35;
            display: inline-block;
            min-width: 120px;
        }
        .valor { color: #333; }
        .btn-editar {
            display: block;
            background: #f39c12;
            color: white;
            text-align: center;
            padding: 12px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: bold;
            margin-top: 25px;
        }
        .btn-editar:hover { background: #e67e22; }
    </style>
</head>
<body>
    <a href="{{ url_for('lista_animales') }}" class="btn-volver">← Volver a la lista</a>
    
    <div class="ficha">
        <h2>🐂 Animal #{{ animal['numero'] }}</h2>
        
        <div class="dato"><span class="etiqueta">Número:</span> <span class="valor">{{ animal['numero'] }}</span></div>
        <div class="dato"><span class="etiqueta">Madre:</span> <span class="valor">{{ animal['madre'] or '—' }}</span></div>
        <div class="dato"><span class="etiqueta">Padre:</span> <span class="valor">{{ animal['padre'] or '—' }}</span></div>
        <div class="dato"><span class="etiqueta">Estado:</span> <span class="valor">{{ animal['estado'] or '—' }}</span></div>
        <div class="dato"><span class="etiqueta">Ubicación:</span> <span class="valor">{{ animal['ubicacion'] or '—' }}</span></div>
        <div class="dato"><span class="etiqueta">Sexo:</span> <span class="valor">{{ animal['sexo'] or '—' }}</span></div>
        <div class="dato"><span class="etiqueta">Raza:</span> <span class="valor">{{ animal['raza'] or '—' }}</span></div>
        <div class="dato"><span class="etiqueta">Edad:</span> <span class="valor">{{ animal['edad'] or '—' }}</span></div>
        <div class="dato"><span class="etiqueta">Peso:</span> <span class="valor">{{ animal['peso'] or '—' }}</span></div>
        <div class="dato"><span class="etiqueta">Observaciones:</span> <span class="valor">{{ animal['observaciones'] or '—' }}</span></div>
        
        <a href="{{ url_for('editar_animal', id=animal['id']) }}" class="btn-editar">✏️ Editar este animal</a>
    </div>
</body>
</html>
    ''', animal=animal)

@app.route('/nuevo', methods=['GET', 'POST'])
def nuevo_animal():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute('''
                INSERT INTO animales (numero, madre, padre, estado, ubicacion, sexo, raza, edad, peso, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                request.form.get('numero'),
                request.form.get('madre'),
                request.form.get('padre'),
                request.form.get('estado'),
                request.form.get('ubicacion'),
                request.form.get('sexo'),
                request.form.get('raza'),
                request.form.get('edad'),
                request.form.get('peso'),
                request.form.get('observaciones')
            ))
            db.commit()
            return redirect(url_for('lista_animales'))
        except sqlite3.IntegrityError:
            return "⚠️ Ya existe un animal con ese número. <a href='" + url_for('nuevo_animal') + "'>Volver</a>"
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registrar Animal - Finca Iberia</title>
    <style>
        * { box-sizing: border-box; font-family: Arial, sans-serif; margin: 0; padding: 0; }
        body { 
            background: #f0f7f0;
            min-height: 100vh;
            padding: 20px;
        }
        .btn-volver {
            display: inline-block;
            background: #666;
            color: white;
            padding: 10px 18px;
            border-radius: 6px;
            text-decoration: none;
            margin-bottom: 20px;
        }
        .formulario {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            max-width: 500px;
            margin: 0 auto;
        }
        .formulario h2 {
            text-align: center;
            color: #4a7c59;
            margin-bottom: 25px;
        }
        .campo { margin-bottom: 16px; }
        label { display: block; margin-bottom: 6px; font-weight: bold; color: #2c4a35; }
        input, select, textarea {
            width: 100%;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 15px;
        }
        input:focus, select:focus, textarea:focus { outline: none; border-color: #4a7c59; }
        button {
            width: 100%;
            padding: 12px;
            background: #4a7c59;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 10px;
        }
        button:hover { background: #3a6347; }
    </style>
</head>
<body>
    <a href="{{ url_for('lista_animales') }}" class="btn-volver">← Volver a la lista</a>
    
    <div class="formulario">
        <h2>➕ Registrar Nuevo Animal</h2>
        <form method="POST">
            <div class="campo"><label>Número *</label><input type="text" name="numero" required></div>
            <div class="campo"><label>Madre</label><input type="text" name="madre"></div>
            <div class="campo"><label>Padre</label><input type="text" name="padre"></div>
            <div class="campo"><label>Estado</label><input type="text" name="estado" placeholder="Ej: Vivo, Vendido, Muerto"></div>
            <div class="campo"><label>Ubicación</label><input type="text" name="ubicacion" placeholder="Ej: Potrero 1"></div>
            <div class="campo"><label>Sexo</label>
                <select name="sexo">
                    <option value="">Seleccionar...</option>
                    <option value="Macho">Macho</option>
                    <option value="Hembra">Hembra</option>
                </select>
            </div>
            <div class="campo"><label>Raza</label><input type="text" name="raza"></div>
            <div class="campo"><label>Edad</label><input type="text" name="edad" placeholder="Ej: 2 años"></div>
            <div class="campo"><label>Peso</label><input type="text" name="peso" placeholder="Ej: 450 kg"></div>
            <div class="campo"><label>Observaciones</label><textarea name="observaciones" rows="3"></textarea></div>
            <button type="submit">💾 Guardar Animal</button>
        </form>
    </div>
</body>
</html>
    ''')

@app.route('/editar/<id>', methods=['GET', 'POST'])
def editar_animal(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.cursor()
    
    if request.method == 'POST':
        cursor.execute('''
            UPDATE animales SET numero=?, madre=?, padre=?, estado=?, ubicacion=?, sexo=?, raza=?, edad=?, peso=?, observaciones=? WHERE id=?
        ''', (
            request.form.get('numero'),
            request.form.get('madre'),
            request.form.get('padre'),
            request.form.get('estado'),
            request.form.get('ubicacion'),
            request.form.get('sexo'),
            request.form.get('raza'),
            request.form.get('edad'),
            request.form.get('peso'),
            request.form.get('observaciones'),
            id
        ))
        db.commit()
        return redirect(url_for('ver_animal', id=id))
    
    cursor.execute('SELECT * FROM animales WHERE id = ?', (id,))
    animal = cursor.fetchone()
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Editar Animal - Finca Iberia</title>
    <style>
        * { box-sizing: border-box; font-family: Arial, sans-serif; margin: 0; padding: 0; }
        body { background: #f0f7f0; min-height: 100vh; padding: 20px; }
        .btn-volver { display: inline-block; background: #666; color: white; padding: 10px 18px; border-radius: 6px; text-decoration: none; margin-bottom: 20px; }
        .formulario { background: white; border-radius: 12px; padding: 25px; box-shadow: 0 3px 10px rgba(0,0,0,0.1); max-width: 500px; margin: 0 auto; }
        .formulario h2 { text-align: center; color: #f39c12; margin-bottom: 25px; }
        .campo { margin-bottom: 16px; }
        label { display: block; margin-bottom: 6px; font-weight: bold; color: #2c4a35; }
        input, select, textarea { width: 100%; padding: 10px; border: 2px solid #ddd; border-radius: 6px; font-size: 15px; }
        input:focus, select:focus, textarea:focus { outline: none; border-color: #4a7c59; }
        button { width: 100%; padding: 12px; background: #f39c12; color: white; border: none; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; margin-top: 10px; }
        button:hover { background: #e67e22; }
    </style>
</head>
<body>
    <a href="{{ url_for('ver_animal', id=animal['id']) }}" class="btn-volver">← Volver al animal</a>
    
    <div class="formulario">
        <h2>✏️ Editar Animal</h2>
        <form method="POST">
            <div class="campo"><label>Número *</label><input type="text" name="numero" value="{{ animal['numero'] }}" required></div>
            <div class="campo"><label>Madre</label><input type="text" name="madre" value="{{ animal['madre'] or '' }}"></div>
            <div class="campo"><label>Padre</label><input type="text" name="padre" value="{{ animal['padre'] or '' }}"></div>
            <div class="campo"><label>Estado</label><input type="text" name="estado" value="{{ animal['estado'] or '' }}"></div>
            <div class="campo"><label>Ubicación</label><input type="text" name="ubicacion" value="{{ animal['ubicacion'] or '' }}"></div>
            <div class="campo"><label>Sexo</label>
                <select name="sexo">
                    <option value="">Seleccionar...</option>
                    <option value="Macho" {% if animal['sexo'] == 'Macho' %}selected{% endif %}>Macho</option>
                    <option value="Hembra" {% if animal['sexo'] == 'Hembra' %}selected{% endif %}>Hembra</option>
                </select>
            </div>
            <div class="campo"><label>Raza</label><input type="text" name="raza" value="{{ animal['raza'] or '' }}"></div>
            <div class="campo"><label>Edad</label><input type="text" name="edad" value="{{ animal['edad'] or '' }}"></div>
            <div class="campo"><label>Peso</label><input type="text" name="peso" value="{{ animal['peso'] or '' }}"></div>
            <div class="campo"><label>Observaciones</label><textarea name="observaciones" rows="3">{{ animal['observaciones'] or '' }}</textarea></div>
            <button type="submit">💾 Guardar Cambios</button>
        </form>
    </div>
</body>
</html>
    ''', animal=animal)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)