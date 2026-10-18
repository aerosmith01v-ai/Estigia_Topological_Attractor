import os
import matplotlib
matplotlib.use("Agg")

import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# THERMODYNAMIC TOPOLOGICAL ATTRACTOR SIMULATION v4.1
# ============================================================

class AtractorLorenzLegado:
    """
    Sistema caótico de Lorenz: representa el estado anterior
    de alta entropía termodinámica y lógica.
    Parámetros clásicos: σ=10, ρ=28, β=8/3
    """
    def __init__(self, sigma=10.0, rho=28.0, beta=8/3, num_puntos=2000):
        self.sigma = sigma
        self.rho = rho
        self.beta = beta
        self.num_puntos = num_puntos
        self.dt = 0.01

    def derivadas(self, estado):
        x, y, z = estado
        dx = self.sigma * (y - x)
        dy = x * (self.rho - z) - y
        dz = x * y - self.beta * z
        return np.array([dx, dy, dz])

    def generar_trayectoria(self, pasos=10000, estado_inicial=None):
        if estado_inicial is None:
            estado_inicial = np.array([1.0, 1.0, 1.0]) + np.random.normal(0, 0.1, 3)

        estados = np.zeros((pasos, 3))
        estados[0] = estado_inicial

        for i in range(1, pasos):
            k1 = self.derivadas(estados[i-1])
            k2 = self.derivadas(estados[i-1] + 0.5 * self.dt * k1)
            k3 = self.derivadas(estados[i-1] + 0.5 * self.dt * k2)
            k4 = self.derivadas(estados[i-1] + self.dt * k3)
            estados[i] = estados[i-1] + (self.dt / 6) * (k1 + 2*k2 + 2*k3 + k4)

        return estados


class ModuloAtraccionTopologica:
    """
    El MAT: no fuerza, no reemplaza.
    Emite un campo de potencial que redefine la línea base de eficiencia.
    """
    def __init__(self, posicion=np.array([0.0, 0.0, 25.0]),
                 fuerza_atraccion=2.0, radio_influencia=15.0):
        self.posicion = posicion
        self.fuerza = fuerza_atraccion
        self.radio = radio_influencia
        self.estabilidad = 0.0

    def campo_potencial(self, estados):
        distancias = np.linalg.norm(estados - self.posicion, axis=1)
        potencial = -self.fuerza * np.exp(-distancias**2 / (2 * self.radio**2))
        return potencial

    def fuerza_atraccion_vector(self, estados):
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


def simular_colapso_atractor(pasos_totales=1000, puntos_muestra=2000):
    print("🔬 THERMODYNAMIC TOPOLOGICAL ATTRACTOR SIMULATION v4.1")
    print("=" * 60)

    lorenz = AtractorLorenzLegado(num_puntos=puntos_muestra)

    todas_trayectorias = []
    for _ in range(50):
        estado_init = np.random.uniform(-15, 15, 3)
        traj = lorenz.generar_trayectoria(pasos=200, estado_inicial=estado_init)
        todas_trayectorias.append(traj[-1])

    estados = np.array(todas_trayectorias)

    mat = ModuloAtraccionTopologica(
        posicion=np.array([0.0, 0.0, 25.0]),
        fuerza_atraccion=3.0,
        radio_influencia=20.0
    )

    print(f"📍 MAT implantado en: {mat.posicion}")
    print(f" Fuerza de atracción: {mat.fuerza}")
    print(f" Radio de influencia: {mat.radio}")
    print()

    historial_estados = []
    historial_eficiencia = []
    estados_actuales = estados.copy()

    for iteracion in range(pasos_totales):
        nuevos_estados = np.zeros_like(estados_actuales)
        for i in range(len(estados_actuales)):
            deriv = lorenz.derivadas(estados_actuales[i])
            nuevos_estados[i] = estados_actuales[i] + lorenz.dt * deriv

        fuerza_mat = mat.fuerza_atraccion_vector(nuevos_estados)
        estados_actuales = nuevos_estados + fuerza_mat * 0.5

        distancias = np.linalg.norm(estados_actuales - mat.posicion, axis=1)
        entropia = np.std(distancias)
        eficiencia = 1.0 / (1.0 + entropia)

        historial_estados.append(estados_actuales.copy())
        historial_eficiencia.append(eficiencia)

    estabilidad_final = mat.calcular_estabilidad(estados_actuales)

    print(f"✅ Iteración final: {pasos_totales}")
    print(f"🎯 MAT Stability: {estabilidad_final:.1f}%")
    print(f"📉 Eficiencia final: {historial_eficiencia[-1]:.4f}")
    print(f"📊 Nueva línea base de eficiencia: {np.mean(historial_eficiencia[-100:]):.4f}")

    return estados, estados_actuales, mat, historial_eficiencia, estabilidad_final


def generar_visualizacion(estados_iniciales, estados_finales, mat,
                          historial_eficiencia, estabilidad):
    fig = plt.figure(figsize=(16, 8), facecolor="#0a0e1a")
    fig.suptitle("THERMODYNAMIC TOPOLOGICAL ATTRACTOR SIMULATION v4.1",
                 color="#00d4ff", fontsize=14, fontweight="bold", y=0.98)

    fig.text(0.02, 0.95, "Iteration: 1000", color="#00d4ff", fontsize=10)
    fig.text(0.85, 0.95, f"MAT Stability: {estabilidad:.1f}%", color="#00d4ff", fontsize=10)

    ax1 = fig.add_subplot(121, facecolor="#0a0e1a")
    ax1.set_facecolor("#050810")

    phi1_inicial = estados_iniciales[:, 0]
    phi2_inicial = estados_iniciales[:, 1]
    phi1_final = estados_finales[:, 0]
    phi2_final = estados_finales[:, 1]

    ax1.scatter(phi1_inicial, phi2_inicial, c="#00ffff", s=2, alpha=0.15)
    ax1.scatter(phi1_final, phi2_final, c="#00ffff", s=3, alpha=0.6)

    ax1.scatter(mat.posicion[0], mat.posicion[1], c="red", marker="*", s=300,
                zorder=10, edgecolors="yellow", linewidths=1)
    ax1.text(mat.posicion[0], mat.posicion[1]-2, "MAT", color="white",
             fontsize=10, fontweight="bold", ha="center")

    theta = np.linspace(0, 2*np.pi, 100)
    x_lorenz = 20 * np.cos(theta) * np.exp(-0.1*theta)
    y_lorenz = 15 * np.sin(2*theta) * np.exp(-0.05*theta)
    ax1.plot(x_lorenz, y_lorenz, "c--", alpha=0.2, linewidth=1)

    ax1.set_xlabel("Φ1 (State)", color="#00d4ff", fontsize=11)
    ax1.set_ylabel("Φ2 (State)", color="#00d4ff", fontsize=11)
    ax1.set_title("ATTRACTOR STATE SPACE COLLAPSE",
                  color="#00d4ff", fontsize=12, fontweight="bold")
    ax1.grid(True, alpha=0.2, color="#00d4ff")
    ax1.set_xlim(-30, 30)
    ax1.set_ylim(-25, 25)

    for spine in ax1.spines.values():
        spine.set_color("#00d4ff")
        spine.set_linewidth(1.5)

    ax2 = fig.add_subplot(122, facecolor="#0a0e1a")
    ax2.set_facecolor("#050810")

    iteraciones = range(len(historial_eficiencia))
    ax2.plot(iteraciones, historial_eficiencia, color="#9b59b6", linewidth=2,
             label="Efficiency η")

    linea_base = np.mean(historial_eficiencia[-100:])
    ax2.axhline(y=linea_base, color="#2ecc71", linestyle="--", linewidth=1.5,
                label="Baseline")
    ax2.text(600, linea_base + 0.02, "NEW EFFICIENCY BASELINE",
             color="#2ecc71", fontsize=9, fontweight="bold")

    ax2.scatter([len(historial_eficiencia)-1], [historial_eficiencia[-1]],
                c="red", marker="*", s=150, zorder=10, label="MAT")

    ax2.set_xlabel("Time T (Iteration)", color="#00d4ff", fontsize=11)
    ax2.set_ylabel("Efficiency η", color="#00d4ff", fontsize=11)
    ax2.set_title("EFFICIENCY DECAY CURVE",
                  color="#00d4ff", fontsize=12, fontweight="bold")
    ax2.grid(True, alpha=0.2, color="#00d4ff")
    ax2.set_xlim(0, 1000)
    ax2.set_ylim(0, 1.05)
    ax2.legend(loc="upper right", facecolor="#0a0e1a", edgecolor="#00d4ff",
               labelcolor="white", fontsize=8)

    for spine in ax2.spines.values():
        spine.set_color("#00d4ff")
        spine.set_linewidth(1.5)

    plt.tight_layout()

    out_dir = os.path.abspath("./outputs")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "MAT_Simulation_v4.1.png")

    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

    print(f"\n📸 Visualización guardada como '{out_path}'")


if __name__ == "__main__":
    estados_ini, estados_fin, mat, eficiencia, estabilidad = simular_colapso_atractor(
        pasos_totales=1000,
        puntos_muestra=2000
    )
    generar_visualizacion(estados_ini, estados_fin, mat, eficiencia, estabilidad)
