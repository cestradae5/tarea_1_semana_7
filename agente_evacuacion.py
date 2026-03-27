"""
Sistema Inteligente de Evacuación - Agente Solvente
Universidad Mariano Gálvez
Carlo Andree Barquero Boche 090-22-601

Ejecutar: python agente_evacuacion.py
Requisitos: pip install networkx matplotlib
"""

import networkx as nx
import matplotlib.pyplot as plt
import heapq

# =========================================================
# 1. DEFINICIÓN DEL GRAFO (Municipios de Guatemala)
# =========================================================
grafo = {
    "Flores": {"Santa Elena": 5, "Sayaxché": 85},
    "Santa Elena": {"Flores": 5},
    "Sayaxché": {"Flores": 85, "Cobán": 120},
    "Cobán": {"Sayaxché": 120, "Zacapa": 140},
    "Zacapa": {"Cobán": 140, "Ciudad de Guatemala": 130},
    "Ciudad de Guatemala": {"Zacapa": 130}
}

# Posiciones fijas para visualización (coordenadas aproximadas)
posiciones_manual = {
    "Flores": (0, 2),
    "Santa Elena": (0, 0),
    "Sayaxché": (2, 2),
    "Cobán": (4, 2),
    "Zacapa": (6, 2),
    "Ciudad de Guatemala": (7, 0)
}

# =========================================================
# 2. ALGORITMO DE DIJKSTRA CON REGISTRO DE PASOS
# =========================================================
def dijkstra_con_pasos(grafo, inicio, meta):
    """
    Implementación de Dijkstra que retorna:
    - costo: costo total de la ruta óptima
    - ruta: lista de nodos de la ruta óptima
    - pasos: lista de diccionarios con el detalle de cada paso
    """
    cola = [(0, inicio, [inicio])]
    visitados = set()
    pasos = []
    paso_num = 0

    while cola:
        costo, nodo, ruta = heapq.heappop(cola)

        if nodo in visitados:
            continue

        visitados.add(nodo)
        paso_num += 1

        # Registrar el paso
        vecinos_info = []
        for vecino, distancia in grafo.get(nodo, {}).items():
            if vecino not in visitados:
                vecinos_info.append(f"{vecino} ({costo + distancia} km)")

        pasos.append({
            "paso": paso_num,
            "nodo": nodo,
            "costo_acumulado": costo,
            "ruta_parcial": list(ruta),
            "vecinos_por_explorar": vecinos_info
        })

        # ¿Llegamos a la meta?
        if nodo == meta:
            return costo, ruta, pasos

        # Expandir vecinos
        for vecino, distancia in grafo[nodo].items():
            if vecino not in visitados:
                heapq.heappush(cola, (costo + distancia, vecino, ruta + [vecino]))

    return None, None, pasos


# =========================================================
# 3. VISUALIZACIÓN DEL GRAFO CON RUTA ÓPTIMA
# =========================================================
def visualizar_grafo(grafo, ruta_optima=None, inicio=None, meta=None):
    """Dibuja el grafo de municipios y resalta la ruta óptima en rojo."""
    G = nx.Graph()
    for nodo, vecinos in grafo.items():
        for vecino, peso in vecinos.items():
            G.add_edge(nodo, vecino, weight=peso)

    pos = posiciones_manual

    fig, ax = plt.subplots(1, 1, figsize=(14, 6))
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#1a1a2e")

    # Colores de nodos
    colores_nodos = []
    for nodo in G.nodes():
        if nodo == inicio:
            colores_nodos.append("#e74c3c")      # Rojo - origen/incendio
        elif nodo == meta:
            colores_nodos.append("#2ecc71")       # Verde - meta
        elif ruta_optima and nodo in ruta_optima:
            colores_nodos.append("#f39c12")       # Amarillo - en la ruta
        else:
            colores_nodos.append("#3498db")       # Azul - normal

    # Dibujar aristas normales
    aristas_normales = [(u, v) for u, v in G.edges()
                        if not ruta_optima or not _arista_en_ruta(u, v, ruta_optima)]
    nx.draw_networkx_edges(G, pos, edgelist=aristas_normales,
                           edge_color="#555555", width=1.5, ax=ax)

    # Dibujar aristas de la ruta óptima
    if ruta_optima:
        aristas_ruta = list(zip(ruta_optima, ruta_optima[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=aristas_ruta,
                               edge_color="#e74c3c", width=4, ax=ax)

    # Dibujar nodos
    nx.draw_networkx_nodes(G, pos, node_size=2500, node_color=colores_nodos,
                           edgecolors="white", linewidths=2, ax=ax)

    # Etiquetas de nodos
    nx.draw_networkx_labels(G, pos, font_size=9, font_weight="bold",
                            font_color="white", ax=ax)

    # Etiquetas de distancia en aristas
    edge_labels = nx.get_edge_attributes(G, 'weight')
    edge_labels_fmt = {k: f"{v} km" for k, v in edge_labels.items()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels_fmt,
                                 font_size=8, font_color="#cccccc",
                                 bbox=dict(boxstyle="round,pad=0.2",
                                           facecolor="#1a1a2e", edgecolor="none"),
                                 ax=ax)

    # Título
    titulo = "Grafo de Municipios - Sistema de Evacuación"
    if ruta_optima:
        titulo += f"\nRuta óptima: {' → '.join(ruta_optima)}"
    ax.set_title(titulo, fontsize=14, fontweight="bold", color="white", pad=20)

    # Leyenda
    from matplotlib.lines import Line2D
    leyenda = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#e74c3c',
               markersize=12, label='Origen (incendio)'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#2ecc71',
               markersize=12, label='Meta (evacuación)'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#f39c12',
               markersize=12, label='En ruta óptima'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#3498db',
               markersize=12, label='Otros municipios'),
        Line2D([0], [0], color='#e74c3c', linewidth=3, label='Ruta óptima'),
    ]
    ax.legend(handles=leyenda, loc='lower left', fontsize=8,
              facecolor="#2a2a4a", edgecolor="white", labelcolor="white")

    plt.tight_layout()
    plt.savefig("grafo_evacuacion.png", dpi=150, bbox_inches="tight",
                facecolor="#1a1a2e")
    print("\n[✓] Imagen guardada como: grafo_evacuacion.png")
    plt.show()


def _arista_en_ruta(u, v, ruta):
    """Verifica si una arista está en la ruta óptima."""
    for i in range(len(ruta) - 1):
        if (ruta[i] == u and ruta[i+1] == v) or (ruta[i] == v and ruta[i+1] == u):
            return True
    return False


# =========================================================
# 4. IMPRESIÓN DE PASOS DEL ALGORITMO
# =========================================================
def imprimir_pasos(pasos):
    """Muestra paso a paso cómo Dijkstra explora el grafo."""
    print("\n" + "=" * 60)
    print("  PASOS DEL ALGORITMO DE DIJKSTRA")
    print("=" * 60)
    for p in pasos:
        print(f"\n  Paso {p['paso']}: Visitar → {p['nodo']}")
        print(f"    Costo acumulado: {p['costo_acumulado']} km")
        print(f"    Ruta parcial:    {' → '.join(p['ruta_parcial'])}")
        if p['vecinos_por_explorar']:
            print(f"    Vecinos en cola: {', '.join(p['vecinos_por_explorar'])}")
        else:
            print(f"    ¡META ALCANZADA!")
    print("\n" + "=" * 60)


# =========================================================
# 5. ANATOMÍA DEL PROBLEMA (Tabla formal)
# =========================================================
def imprimir_formalizacion(inicio, meta):
    """Imprime la formalización del problema de búsqueda."""
    print("\n" + "=" * 60)
    print("  FORMALIZACIÓN DEL PROBLEMA DE BÚSQUEDA")
    print("=" * 60)
    print(f"""
  ┌──────────────────────┬────────────────────────────────────┐
  │ Componente           │ Valor                              │
  ├──────────────────────┼────────────────────────────────────┤
  │ Estado Inicial       │ Agente en {inicio:<25s}│
  │ Acciones             │ Mover(origen, destino_adyacente)   │
  │ Modelo de Transición │ resultado(s, a) → s'               │
  │ Prueba de Meta       │ ¿estado == {meta}?{' ' * max(0, 16 - len(meta))}│
  │ Costo de Ruta        │ Suma de km entre municipios        │
  └──────────────────────┴────────────────────────────────────┘

  Ciclo del agente:
    PERCIBIR  → Sensor detecta incendio en {inicio}
    FORMULAR  → Definir grafo de municipios y meta
    BUSCAR    → Dijkstra calcula ruta óptima (offline)
    EJECUTAR  → Coordinar evacuación por la ruta encontrada

  Supuestos: Entorno estático, observable, discreto, determinista
""")


# =========================================================
# 6. MENÚ INTERACTIVO
# =========================================================
def menu_interactivo():
    """Menú principal para demostración interactiva."""
    municipios = list(grafo.keys())

    print("\n" + "╔" + "═" * 58 + "╗")
    print("║   SISTEMA INTELIGENTE DE EVACUACIÓN - AGENTE SOLVENTE    ║")
    print("║   Universidad Mariano Gálvez                             ║")
    print("║   Carlo Andree Barquero Boche 090-22-601                 ║")
    print("╚" + "═" * 58 + "╝")

    while True:
        print("\n  Municipios disponibles:")
        for i, m in enumerate(municipios, 1):
            print(f"    {i}. {m}")

        print(f"\n  0. Salir")

        try:
            print("\n  --- Seleccionar origen ---")
            idx_inicio = int(input("  Número del municipio de origen: "))
            if idx_inicio == 0:
                print("\n  ¡Hasta luego!")
                break
            if idx_inicio < 1 or idx_inicio > len(municipios):
                print("  [!] Opción inválida")
                continue

            print("\n  --- Seleccionar meta ---")
            idx_meta = int(input("  Número del municipio meta: "))
            if idx_meta < 1 or idx_meta > len(municipios):
                print("  [!] Opción inválida")
                continue

            inicio = municipios[idx_inicio - 1]
            meta = municipios[idx_meta - 1]

            if inicio == meta:
                print("  [!] El origen y la meta no pueden ser iguales")
                continue

            # Formalización
            imprimir_formalizacion(inicio, meta)

            # Ejecutar Dijkstra
            costo, ruta, pasos = dijkstra_con_pasos(grafo, inicio, meta)

            if ruta:
                print(f"\n  ✅ RUTA ÓPTIMA ENCONTRADA")
                print(f"  Ruta:  {' → '.join(ruta)}")
                print(f"  Costo: {costo} km")

                # Mostrar pasos
                imprimir_pasos(pasos)

                # Visualizar
                print("\n  Generando visualización...")
                visualizar_grafo(grafo, ruta, inicio, meta)
            else:
                print(f"\n  ❌ No se encontró ruta de {inicio} a {meta}")
                visualizar_grafo(grafo, inicio=inicio, meta=meta)

        except ValueError:
            print("  [!] Ingresa un número válido")
        except KeyboardInterrupt:
            print("\n\n  ¡Hasta luego!")
            break


# =========================================================
# 7. EJECUCIÓN PRINCIPAL
# =========================================================
if __name__ == "__main__":
    # Ejecución rápida por defecto
    print("\n  Ejecutando búsqueda por defecto: Flores → Ciudad de Guatemala\n")

    inicio = "Flores"
    meta = "Ciudad de Guatemala"

    imprimir_formalizacion(inicio, meta)

    costo, ruta, pasos = dijkstra_con_pasos(grafo, inicio, meta)

    print(f"  ✅ Ruta óptima: {' → '.join(ruta)}")
    print(f"  📏 Costo total: {costo} km")

    imprimir_pasos(pasos)
    visualizar_grafo(grafo, ruta, inicio, meta)

    # Preguntar si quiere modo interactivo
    print("\n  ¿Deseas probar con otros municipios?")
    resp = input("  (s/n): ").strip().lower()
    if resp == 's':
        menu_interactivo()
