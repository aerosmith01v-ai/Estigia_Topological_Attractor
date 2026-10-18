"""
THERMODYNAMIC TOPOLOGICAL ATTRACTOR SIMULATION v4.1
=====================================================
Simulación animada del colapso espontáneo de un sistema caótico
(Atractor de Lorenz) hacia un Módulo de Atracción Topológica (MAT).

El MAT NO fuerza, NO reemplaza, NO ordena.
Solo emite un campo de potencial termodinámico.
El sistema se reorganiza SOLO porque es el camino de menor resistencia.

Autor: [Tu nombre]
Repositorio: thermodynamic-topological-attractor-sim
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import FancyArrowPatch
import os

# ============================================================
# CLASE 1: SISTEMA LEGADO - ATRACTOR DE LORENZ CAÓTICO
# ============================================================
class AtractorLorenzLegado:
    """
    Sistema caótico de Lorenz: representa el estado anterior
    de alta entropía termodinámica y lógica.
    Parámetros clásicos: σ=10, ρ=28, β=8/3
    """
    def __init__(self, sigma=10.0, rho=28.0, beta=8/3):
        self.sigma = sigma
        self.rho = rho
        self.beta = beta
        self.dt = 0.01

    def derivadas(self, estado):
        x, y, z = estado
        dx = self.sigma * (y - x)
        dy = x * (self.rho - z) - y
        dz = x * y - self.beta * z
        return np.array([dx, dy, dz])

    def evolucionar(self, estado):
        """Un paso de Runge-Kutta 4."""
        k1 = self.derivadas(estado)
        k2 = self.derivadas(estado + 0.5 * self.dt * k1)
        k3 = self.derivadas(estado + 0.5 * self.dt * k2)
        k4 = self.derivadas(estado + self.dt * k3)
        return estado + (self.dt / 6) * (k1 + 2*k2 + 2*k3 + k4)


# ============================================================
# CLASE 2: MÓDULO DE ATRACCIÓN TOPOLÓGICA (MAT)
# ============================================================
class ModuloAtraccionTopologica:
    """
    El MAT: no fuerza, no reemplaza, no ordena.
    Emite un campo de potencial que redefine la línea base de eficiencia.
    """
    def __init__(self, posicion=np.array([0.0, 0.0, 25.0]), 
                 fuerza_atraccion=3.0, radio_influencia=20.0):
        self.posicion = posicion
        self.fuerza = fuerza_atraccion
        self.radio = radio_influencia
        self.estabilidad = 0.0

    def campo_potencial(self, estados):
        """Campo de potencial termodinámico: pozo suave en el centro."""
        distancias = np.linalg.norm(estados - self.posicion, axis=1)
        return -self.fuerza * np.exp(-distancias**2 / (2 * self.radio**2))

    def fuerza_atraccion_vector(self, estados):
        """Fuerza direccional hacia el MAT (gradiente del potencial)."""
        vectores = self.posicion - estados
        distancias = np.linalg.norm(vectores, axis=1, keepdims=True)
        distancias = np.maximum(distancias, 1e-10)
        direcciones = vectores / distancias
        magnitud = self.fuerza * np.exp(-distancias**2 / (2 * self.radio**2))
        return direcciones * magnitud

    def calcular_estabilidad(self, estados):
        distancias = np.linalg.norm(estados - self.posicion, axis=1)
        distancia_media = np.mean(distancias)
        self.estabilidad = np.exp(-distancia_media / self.radio) * 100
        return self.estabilidad


# ============================================================
# CLASE 3: SIMULADOR PRINCIPAL
# ============================================================
class SimuladorMAT:
    def __init__(self, num_puntos=1500, pasos_totales=1000):
        self.lorenz = AtractorLorenzLegado()
        self.mat = ModuloAtraccionTopologica()
        self.num_puntos = num_puntos
        self.pasos_totales = pasos_totales
        
        # Inicializar estados aleatorios (caos inicial)
        self.estados = np.random.uniform(-15, 15, (num_puntos, 3))
        self.historial_eficiencia = []
        self.historial_estabilidad = []
        self.iteracion_actual = 0

    def calcular_eficiencia(self):
        distancias = np.linalg.norm(self.estados - self.mat.posicion, axis=1)
        entropia = np.std(distancias)
        return 1.0 / (1.0 + entropia)

    def paso_simulacion(self):
        """Un paso: Lorenz evoluciona + MAT emite campo pasivamente."""
        nuevos_estados = np.zeros_like(self.estados)
        for i in range(self.num_puntos):
            nuevos_estados[i] = self.lorenz.evolucionar(self.estados[i])
        
        # El MAT solo EMITE su campo, no impone nada
        fuerza_mat = self.mat.fuerza_atraccion_vector(nuevos_estados)
        
        # Los estados se mueven naturalmente hacia menor energía
        self.estados = nuevos_estados + fuerza_mat * 0.3
        
        self.iteracion_actual += 1
        eficiencia = self.calcular_eficiencia()
        estabilidad = self.mat.calcular_estabilidad(self.estados)
        
        self.historial_eficiencia.append(eficiencia)
        self.historial_estabilidad.append(estabilidad)
        
        return eficiencia, estabilidad


# ============================================================
# CLASE 4: VISUALIZADOR ANIMADO
# ============================================================
class VisualizadorAnimado:
    def __init__(self, simulador):
        self.sim = simulador
        self.fig = plt.figure(figsize=(16, 8), facecolor='#0a0e1a')
        
        # Título
        self.fig.suptitle('THERMODYNAMIC TOPOLOGICAL ATTRACTOR SIMULATION v4.1', 
                         color='#00d4ff', fontsize=14, fontweight='bold', y=0.98)
        
        # Panel izquierdo: State Space
        self.ax1 = self.fig.add_subplot(121, facecolor='#050810')
        self.ax1.set_facecolor('#050810')
        self.ax1.set_title('ATTRACTOR STATE SPACE COLLAPSE', 
                          color='#00d4ff', fontsize=12, fontweight='bold')
        self.ax1.set_xlabel('Φ1 (State)', color='#00d4ff', fontsize=11)
        self.ax1.set_ylabel('Φ2 (State)', color='#00d4ff', fontsize=11)
        self.ax1.set_xlim(-30, 30)
        self.ax1.set_ylim(-25, 25)
        self.ax1.grid(True, alpha=0.2, color='#00d4ff')
        for spine in self.ax1.spines.values():
            spine.set_color('#00d4ff')
            spine.set_linewidth(1.5)
        
        # Scatter de puntos
        self.scatter = self.ax1.scatter([], [], c='#00ffff', s=3, alpha=0.7)
        # MAT (estrella roja)
        self.mat_marker = self.ax1.scatter(
            [self.sim.mat.posicion[0]], [self.sim.mat.posicion[1]], 
            c='red', marker='*', s=300, zorder=10, 
            edgecolors='yellow', linewidths=1.5
        )
        self.mat_text = self.ax1.text(
            self.sim.mat.posicion[0], self.sim.mat.posicion[1]-2.5, 'MAT', 
            color='white', fontsize=10, fontweight='bold', ha='center'
        )
        
        # Texto de iteración y estabilidad
        self.iter_text = self.fig.text(0.02, 0.95, 'Iteration: 0', 
                                       color='#00d4ff', fontsize=10)
        self.stab_text = self.fig.text(0.75, 0.95, 'MAT Stability: 0.0%', 
                                       color='#00d4ff', fontsize=10)
        
        # Panel derecho: Efficiency Curve
        self.ax2 = self.fig.add_subplot(122, facecolor='#050810')
        self.ax2.set_facecolor('#050810')
        self.ax2.set_title('EFFICIENCY DECAY CURVE', 
                          color='#00d4ff', fontsize=12, fontweight='bold')
        self.ax2.set_xlabel('Time T (Iteration)', color='#00d4ff', fontsize=11)
        self.ax2.set_ylabel('Efficiency η', color='#00d4ff', fontsize=11)
        self.ax2.set_xlim(0, self.sim.pasos_totales)
        self.ax2.set_ylim(0, 1.05)
        self.ax2.grid(True, alpha=0.2, color='#00d4ff')
        for spine in self.ax2.spines.values():
            spine.set_color('#00d4ff')
            spine.set_linewidth(1.5)
        
        # Líneas de la curva
        self.line_eficiencia, = self.ax2.plot([], [], color='#9b59b6', 
                                               linewidth=2, label='Efficiency η')
        self.line_baseline, = self.ax2.plot([], [], color='#2ecc71', 
                                             linestyle='--', linewidth=1.5, 
                                             label='Baseline')
        self.baseline_text = self.ax2.text(
            0, 0, 'NEW EFFICIENCY BASELINE', 
            color='#2ecc71', fontsize=9, fontweight='bold'
        )
        self.ax2.legend(loc='upper right', facecolor='#0a0e1a', 
                       edgecolor='#00d4ff', labelcolor='white', fontsize=8)

    def actualizar(self, frame):
        # Ejecutar varios pasos por frame para acelerar la animación
        pasos_por_frame = 5
        for _ in range(pasos_por_frame):
            if self.sim.iteracion_actual >= self.sim.pasos_totales:
                break
            self.sim.paso_simulacion()
        
        # Actualizar scatter
        phi1 = self.sim.estados[:, 0]
        phi2 = self.sim.estados[:, 1]
        self.scatter.set_offsets(np.column_stack([phi1, phi2]))
        
        # Actualizar textos
        self.iter_text.set_text(f'Iteration: {self.sim.iteracion_actual}')
        stab = self.sim.historial_estabilidad[-1] if self.sim.historial_estabilidad else 0
        self.stab_text.set_text(f'MAT Stability: {stab:.1f}%')
        
        # Actualizar curva de eficiencia
        x_data = range(len(self.sim.historial_eficiencia))
        y_data = self.sim.historial_eficiencia
        self.line_eficiencia.set_data(x_data, y_data)
        
        # Línea base (promedio de los últimos 50 valores)
        if len(y_data) > 50:
            baseline = np.mean(y_data[-50:])
            self.line_baseline.set_data([0, self.sim.iteracion_actual], 
                                        [baseline, baseline])
            self.baseline_text.set_position((
                self.sim.iteracion_actual * 0.5, baseline + 0.03
            ))
        
        return self.scatter, self.line_eficiencia, self.line_baseline

    def crear_animacion(self, nombre_archivo='MAT_Animation.gif', fps=30):
        print("🎬 Creando animación...")
        print(f"   Pasos totales: {self.sim.pasos_totales}")
        print(f"   Puntos: {self.sim.num_puntos}")
        print(f"   FPS: {fps}")
        
        anim = FuncAnimation(
            self.fig, self.actualizar, 
            frames=self.sim.pasos_totales // 5,
            interval=1000//fps, blit=True, repeat=False
        )
        
        anim.save(nombre_archivo, writer='pillow', fps=fps, dpi=100)
        print(f"✅ Animación guardada como '{nombre_archivo}'")
        return anim


# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("🔬 THERMODYNAMIC TOPOLOGICAL ATTRACTOR SIMULATION v4.1")
    print("=" * 60)
    print()
    print("📌 Principio fundamental:")
    print("   El MAT NO fuerza, NO reemplaza, NO ordena.")
    print("   Solo EMITE un campo de potencial termodinámico.")
    print("   El sistema se REORGANIZA SOLO porque es el")
    print("   camino de MENOR RESISTENCIA.")
    print()
    
    # Crear simulador
    simulador = SimuladorMAT(num_puntos=1500, pasos_totales=1000)
    
    # Crear visualizador
    visualizador = VisualizadorAnimado(simulador)
    
    # Generar animación
    animacion = visualizador.crear_animacion(
        nombre_archivo='MAT_Animation.gif', 
        fps=24
    )
    
    print()
    print("🎯 Simulación completada.")
    print(f"   Estabilidad final del MAT: {simulador.historial_estabilidad[-1]:.1f}%")
    print(f"   Eficiencia final: {simulador.historial_eficiencia[-1]:.4f}")
    
    # Mostrar la animación (opcional, puede comentarse si solo quieres el GIF)
    plt.show()
