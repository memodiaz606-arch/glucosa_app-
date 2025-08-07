from flask import Flask, render_template, request, redirect, send_file
import json, os
from datetime import datetime
import pytz
import pandas as pd
from io import BytesIO

app = Flask(__name__)

MEDICAMENTOS = [
    {"nombre": "Metformina 850mg - Mañana", "id": "met_m"},
    {"nombre": "Metformina 850mg - Noche", "id": "met_n"},
    {"nombre": "Trayenta Linagliptina 5mg", "id": "trayenta"},
    {"nombre": "Dapagliflozina 10mg", "id": "dapagliflozina"},
    {"nombre": "Ibesartan-Hidroclorotiazida 150mg-12.5mg", "id": "ibesartan"},
    {"nombre": "Glibenclamida 5mg", "id": "glibenclamida"},
]

def evaluar_glucosa(valor):
    if valor < 70:
        return "Baja"
    elif 70 <= valor <= 140:
        return "Normal"
    else:
        return "Alta"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        glucosa = int(request.form['glucosa'])
        medicamentos = request.form.getlist('medicamentos')
        zona = pytz.timezone('America/Mexico_City')
        fecha = datetime.now(zona).strftime('%Y-%m-%d %H:%M:%S')
        estado = evaluar_glucosa(glucosa)

        nuevo_registro = {
            'fecha': fecha,
            'glucosa': glucosa,
            'estado': estado,
            'medicamentos': medicamentos
        }

        registros = []
        if os.path.exists('data.json'):
            with open('data.json', 'r') as f:
                registros = json.load(f)

        registros.append(nuevo_registro)

        with open('data.json', 'w') as f:
            json.dump(registros, f, indent=4)

        return redirect('/')

    registros = []
    if os.path.exists('data.json'):
        with open('data.json', 'r') as f:
            registros = json.load(f)

    return render_template('index.html', registros=registros, medicamentos=MEDICAMENTOS)

@app.route('/descargar')
def descargar():
    if not os.path.exists('data.json'):
        return "No hay datos para exportar."

    with open('data.json', 'r') as f:
        registros = json.load(f)

    df = pd.DataFrame(registros)
    df['medicamentos'] = df['medicamentos'].apply(lambda x: ', '.join(x))

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Historial')

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="historial_glucosa.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
