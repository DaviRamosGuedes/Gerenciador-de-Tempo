from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_pymongo import PyMongo

app = Flask(__name__)

# Configuração do MongoDB
app.config["MONGO_URI"] = "mongodb+srv://davirg147:i9I1uNi07gf07hle@projetomarlon.sq5wr.mongodb.net/ProjetoMarlon?retryWrites=true&w=majority"
mongo = PyMongo(app)

# Página inicial
@app.route('/')
def home():
    tasks = list(mongo.db.tasks.find())  # Pega todas as tarefas do MongoDB
    return render_template('home.html', tasks=tasks)

# Adicionar tarefa
@app.route('/add', methods=['POST'])
def add_task():
    name = request.form['name']
    estimated_time = int(request.form['estimated_time'])
    priority = request.form['priority']
    category = request.form['category']

    if estimated_time <= 0:
        return "Tempo estimado inválido", 400

    mongo.db.tasks.insert_one({
        "name": name,
        "estimated_time": estimated_time,
        "priority": priority,
        "category": category
    })
    return redirect(url_for('home'))

# Sugerir horários (divisão em blocos)
@app.route('/suggest_times', methods=['GET'])
def suggest_times():
    tasks = list(mongo.db.tasks.find())
    tasks.sort(key=lambda x: x['estimated_time'])  # Ordena por tempo estimado

    block_duration = 60  # Duração de cada bloco em minutos
    time_blocks = []  # Lista de blocos de tempo
    current_block = []
    current_time = 0

    for task in tasks:
        task_time = task['estimated_time']
        if current_time + task_time <= block_duration:
            current_block.append(task)
            current_time += task_time
        else:
            time_blocks.append(current_block)
            current_block = [task]
            current_time = task_time

    if current_block:
        time_blocks.append(current_block)

    # Formatar os blocos para JSON
    formatted_blocks = []
    for i, block in enumerate(time_blocks):
        block_time = sum(task['estimated_time'] for task in block)
        formatted_blocks.append({
            'block_time': f"{block_time // 60}h {block_time % 60}min",
            'tasks': [{'name': t['name'], 'time': t['estimated_time']} for t in block]
        })

    return jsonify({"suggested_slots": formatted_blocks})

# Excluir tarefa
@app.route('/delete_task', methods=['POST'])
def delete_task():
    task_name = request.json.get('name')
    if not task_name:
        return jsonify({"error": "Nome da tarefa é obrigatório"}), 400

    result = mongo.db.tasks.delete_one({"name": task_name})
    if result.deleted_count == 0:
        return jsonify({"error": "Tarefa não encontrada"}), 404

    return jsonify({"message": "Tarefa excluída com sucesso"}), 200

if __name__ == '__main__':
    app.run(debug=True)
