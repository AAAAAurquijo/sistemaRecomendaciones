import tkinter as tk
from tkinter import messagebox
from tkinter import PhotoImage
from PIL import Image, ImageTk
from tkinter import Tk, Canvas
from itertools import count
import networkx as nx
import matplotlib.pyplot as plt
import heapq
from networkx.algorithms.clique import find_cliques


# ========== DATOS DE EJEMPLO ==========
# Géneros musicales
generos = ["Pop", "Rock", "Electrónica", "Clásica", "Hip-Hop", "Jazz", "Kpop"]

# Usuarios existentes y sus preferencias (similitud 0-1)
usuarios = {
    "Juan": {"Pop": 0.8, "Rock": 0.6, "Electrónica": 0.7},
    "Marianna": {"Clásica": 0.9, "Jazz": 0.85},
    "Adriana": {"Hip-Hop": 0.75, "Electrónica": 0.6, "Pop": 0.4},
    "Kat": {},
}

# Canciones de ejemplo asociadas a géneros
canciones_por_genero = {
    "Pop": ["Shape of You - Ed Sheeran", "Blinding Lights - The Weeknd"],
    "Rock": ["Bohemian Rhapsody - Queen", "Sweet Child O' Mine - Guns N' Roses"],
    "Electrónica": ["Strobe - Deadmau5", "Animals - Martin Garrix"],
    "Clásica": ["Fur Elise - Beethoven", "Moonlight Sonata - Beethoven"],
    "Hip-Hop": ["SICKO MODE - Travis Scott", "God's Plan - Drake"],
    "Jazz": ["Take Five - Dave Brubeck", "So What - Miles Davis"],
    "Kpop": ["Kingdom Come - Red Velvet", "favOrite - LOONA"]
}

# ========== CREAR GRAFO ==========
G = nx.DiGraph()
G.add_nodes_from(generos, tipo='genero')
G.add_nodes_from(usuarios.keys(), tipo='usuario')

# Añadir preferencias como aristas
for usuario, pref in usuarios.items():
    for genero, peso in pref.items():
        G.add_edge(usuario, genero, weight=peso)

# ========== FUNCIÓN: RECOMENDAR USUARIOS SIMILARES==========
def recomendar_usuarios_similares(usuario_nuevo, pref_nuevo, usuarios_existentes):
    similitudes = {} 
    for usuario_existente, pref_existente in usuarios_existentes.items():
        if usuario_existente == usuario_nuevo:
            continue
        generos_comunes = set(pref_nuevo.keys()) & set(pref_existente.keys())
        if not generos_comunes:
            continue
        diferencia_total = sum(abs(pref_nuevo[g] - pref_existente[g]) for g in generos_comunes)
        similitud = 1 - (diferencia_total / len(generos_comunes))
        similitudes[usuario_existente] = similitud
    return sorted(similitudes.items(), key=lambda x: x[1], reverse=True)

# ========== FUNCIÓN: RECOMENDAR CANCIONES ==========
def recomendar_canciones(preferencias):
    # Verificar si todas las preferencias son 0
    if all(valor == 0 for valor in preferencias.values()):
        return ["No hay recomendaciones (todos los gustos están en 0)"]
    
    generos_preferidos = sorted(preferencias.items(), key=lambda x: x[1], reverse=True)[:2]
    canciones_recomendadas = []
    for genero, _ in generos_preferidos:
        canciones_recomendadas.extend(canciones_por_genero.get(genero, []))
    return canciones_recomendadas

# ========== FUNCIÓN: DIJKSTRA Y CLIQUES ===========
def dijkstra_camino_musical(grafo, inicio, fin):
    # Crear una copia no dirigida del grafo para el cálculo
    grafo_nd = grafo.to_undirected()
    distancias = {n: float('inf') for n in grafo_nd.nodes()}

    # Inicializar distancias
    distancias[inicio] = 0
    heap = [(0, inicio)]
    camino = {}

    while heap:
        distancia_actual, nodo_actual = heapq.heappop(heap)
        if nodo_actual == fin:
            break
        for vecino in grafo_nd.neighbors(nodo_actual):
            peso = 1 - grafo_nd[nodo_actual][vecino]['weight']
            distancia_nueva = distancia_actual + peso
            if distancia_nueva < distancias[vecino]:
                distancias[vecino] = distancia_nueva
                heapq.heappush(heap, (distancia_nueva, vecino))
                camino[vecino] = nodo_actual

    # Reconstruir camino
    if fin not in camino and inicio != fin:
        return None, None
    
    if inicio == fin:
        return [inicio], 0.0
    
    ruta = []
    nodo = fin
    while nodo != inicio:
        ruta.append(nodo)
        nodo = camino[nodo]
    ruta.append(inicio)
    ruta.reverse()
    return ruta, distancias[fin]

#CLIQUES
def encontrar_usuarios_identicos(usuarios):
    # Crear grafo de compatibilidad (no dirigido)
    G_compatibilidad = nx.Graph()
    G_compatibilidad.add_nodes_from(usuarios.keys())

    # Añadir aristas si dos usuarios tienen las mismas preferencias
    for u1 in usuarios:
        for u2 in usuarios:
            if u1 != u2 and usuarios[u1] == usuarios[u2]:
                G_compatibilidad.add_edge(u1, u2)

    # Encontrar cliques maximales (grupos de usuarios idénticos)
    cliques = list(find_cliques(G_compatibilidad))
    return [clique for clique in cliques if len(clique) > 1] # Filtrar cliques no triviales

#========== FUNCIÓN: VISUALIZAR GRAFO ==========
def mostrar_grafo(nombre_nuevo):
    plt.figure(figsize=(20, 15))
    pos = {}
    for i, usuario in enumerate(usuarios):
        pos[usuario] = (i * 2, 1)
    for i, genero in enumerate(generos):
        pos[genero] = (i * 1.5, 0)
    nx.draw_networkx_nodes(G, pos, nodelist=usuarios.keys(), node_color='lightblue', node_size=1500)
    nx.draw_networkx_nodes(G, pos, nodelist=generos, node_color='lightgreen', node_size=1500)
    edge_widths = [d['weight'] * 3 for (_, _, d) in G.edges(data=True)]
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), width=edge_widths, edge_color='gray', alpha=0.6)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
    edge_labels = {(u, v): f"{d['weight']:.2f}" for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    plt.title(f"Sistema de Recomendación Musical: {nombre_nuevo}")
    plt.axis('off')
    plt.tight_layout()
    plt.show()

# ========== FUNCIÓN: ENTRADA DE NUEVO USUARIO, PREFERENCIAS Y MOSTRAR RECOMENDACIONES==========
def ejecutar_recomendaciones():
    #entrada de datos de nuevo usuario
    nombre_nuevo = entrada_nombre.get()
    if not nombre_nuevo:
        messagebox.showerror("Error", "Debes ingresar tu nombre.")
        return

    preferencias = {}
    for genero in generos:
        valor = entradas_genero[genero].get()
        try:
            fval = float(valor)
            if 0 <= fval <= 1:
                preferencias[genero] = fval
            else:
                messagebox.showerror("Error", f"Valor inválido en {genero}: debe estar entre 0 y 1")
                return
        except ValueError:
            messagebox.showerror("Error", f"Valor inválido en {genero}: debe ser un número")
            return

    # Paso 1: Ingresar nuevo usuario
    usuarios[nombre_nuevo] = {g: p for g, p in preferencias.items() if p > 0}
    G.add_node(nombre_nuevo, tipo='usuario')

    # Paso 2: Añadir aristas PRIMERO (para que Dijkstra funcione)
    for genero, peso in preferencias.items():
        if peso > 0:
            G.add_edge(nombre_nuevo, genero, weight=peso)

    # Paso 3: Dijkstra (usar un usuario existente que tenga conexiones)
    usuario_ejemplo = "Juan"
    resultados = ""
    if usuario_ejemplo in usuarios:
        camino, distancia = dijkstra_camino_musical(G, nombre_nuevo, usuario_ejemplo)
        if camino:
            resultados += f"🛣️ Camino hacia {usuario_ejemplo}: {' → '.join(camino)}\nDistancia: {distancia:.2f}\n\n"
        else:
            resultados += f"🔍 No hay camino hacia {usuario_ejemplo}\n\n"

    cliques = encontrar_usuarios_identicos(usuarios)
    if cliques:
        resultados += "👥 Grupos con gustos idénticos:\n"
        for i, c in enumerate(cliques, 1):
            resultados += f"  Grupo {i}: {', '.join(c)}\n"
    else:
        resultados += "🔍 No hay grupos con gustos idénticos.\n"

    # Paso 3: Recomendar usuarios similares
    similares = recomendar_usuarios_similares(nombre_nuevo, preferencias, usuarios)
    resultados += "\n🎧 Usuarios similares:\n"
    for u, s in similares:
        resultados += f"- {u} (Similitud: {s:.2f})\n"

    # Paso 4: Recomendar canciones
    canciones_recomendadas = recomendar_canciones(preferencias)
    resultados += "\n🎵 Canciones recomendadas:\n"
    for c in canciones_recomendadas:
        resultados += f"- {c}\n"

    # Paso 5: Visualizar resultados y el grafo
    messagebox.showinfo("Resultados", resultados)
    mostrar_grafo(nombre_nuevo)

class AnimatedGIF(tk.Label): #todo esto para un miserable gif...
    def __init__(self, master, path, width=None, height=None):
        self.frames = []
        try:
            # Cargar el GIF y extraer frames
            img = Image.open(path)
            for i in count(1):
                self.frames.append(ImageTk.PhotoImage(
                    img.resize((width, height), Image.LANCZOS) if width and height else img.copy()
                ))
                img.seek(i)
        except EOFError:
            pass
        except Exception as e:
            print(f"Error al cargar GIF: {e}")
            return

        super().__init__(master)
        self.delay = img.info.get('duration', 100)  # Delay entre frames en ms
        self.idx = 0
        self.animate()

    def animate(self):
        self.config(image=self.frames[self.idx])
        self.idx = (self.idx + 1) % len(self.frames)
        self.after(self.delay, self.animate)

def mostrar_gif(ventana, ruta_gif, ancho=None, alto=None):
    try:
        gif = AnimatedGIF(ventana, ruta_gif, ancho, alto)
        return gif
    except Exception as e:
        print(f"Error al cargar GIF: {e}")
        return None

def set_background(root, image_path):
    # Cargar la imagen
    img = Image.open(image_path)
    img = img.resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.LANCZOS)
    bg_image = ImageTk.PhotoImage(img)
    
    # Crear Canvas
    canvas = Canvas(root)
    canvas.pack(fill="both", expand=True)
    
    # Añadir imagen al Canvas
    canvas.create_image(0, 0, image=bg_image, anchor="nw")
    
    # Guardar referencia para evitar garbage collection
    canvas.image = bg_image
    
    return canvas

# ========== VENTANA PRINCIPAL ==========
ventana = tk.Tk()
ventana.title("Sistema de Recomendación Musical")
ventana.geometry("1000x800")

try:
    img_fondo = Image.open("fondo_musica.png")
    img_fondo = img_fondo.resize((1000, 800), Image.LANCZOS)
    bg_image = ImageTk.PhotoImage(img_fondo)
    canvas = tk.Canvas(ventana, width=1000, height=800)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=bg_image, anchor="nw")
    canvas.image = bg_image  # ¡Mantener referencia!
except:
    canvas = tk.Canvas(ventana, bg='lightgray')  # Fallback si no hay imagen
    canvas.pack()

# 2. Añadir widgets SOBRE el fondo (con create_window)
frame_contenido = tk.Frame(canvas, bg='gray', bd=5, relief='ridge')
canvas.create_window(500, 400, window=frame_contenido)

# Mover todo tu contenido actual al frame_contenido
tk.Label(frame_contenido, text="Ingresa tu nombre:", bg = 'lightgray').pack()
entrada_nombre = tk.Entry(frame_contenido, bg = 'lightgray')
entrada_nombre.pack()

tk.Label(frame_contenido, text="Califica tus preferencias por género (0 a 1):", font=('Arial', 12, 'bold'), bg = 'lightgray').pack(pady=10)

img_logo = mostrar_gif(frame_contenido, "logo_musica_gif.gif", 200, 100)
if img_logo:
    img_logo.pack(pady=10)

entradas_genero = {}
for genero in generos:
    tk.Label(frame_contenido, text=genero, bg = 'lightgray').pack()
    entrada = tk.Entry(frame_contenido, bg = 'lightgray')
    entrada.pack()
    entradas_genero[genero] = entrada

tk.Button(frame_contenido, text="Recomendar", command=ejecutar_recomendaciones, bg='lightblue').pack(pady=20)

# ========== EJECUCIÓN INTERFAZ ==========
ventana.mainloop()
