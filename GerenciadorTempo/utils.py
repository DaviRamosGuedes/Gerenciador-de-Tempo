from sklearn.cluster import KMeans
import numpy as np

def Sugestao_tempo(tasks):
    # Extrair tempos estimados das tarefas
    data = np.array([[task['estimated_time']] for task in tasks])

    if len(data) < 3:  # Certifique-se de ter pelo menos 3 dados
        return {"message": "Poucos dados para recomendação"}

    # Aplicar k-means clustering
    kmeans = KMeans(n_clusters=3, random_state=0, n_init='auto')
    kmeans.fit(data)

    # Obter centros dos clusters
    cluster_centers = kmeans.cluster_centers_.flatten()
    sorted_indices = np.argsort(cluster_centers)  # Índices dos clusters ordenados

    # Alocar tarefas nos clusters
    task_allocation = {i: [] for i in range(3)}
    for task, label in zip(tasks, kmeans.labels_):
        task_allocation[label].append({
            "name": task['name'],
            "time": task['estimated_time']
        })

    # Criar resultado ordenado por slots
    result = []
    for cluster_index in sorted_indices:
        cluster_time = cluster_centers[cluster_index]
        tasks_in_cluster = sorted(task_allocation[cluster_index], key=lambda x: x['time'])
        result.append({
            "slot": f"{int(cluster_time // 60)}h {int(cluster_time % 60)}min",
            "tasks": tasks_in_cluster
        })

    return {"suggested_slots": result}
