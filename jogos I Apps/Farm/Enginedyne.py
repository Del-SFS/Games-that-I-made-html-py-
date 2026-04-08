import tkinter as tk
from tkinter import ttk
import random

# --- Estado do jogo ---
creditos = 1000
fila = []
historico = []
contratos = []

# Motores de pesquisa reais/fictícios
pesquisa_motores = {
    "RS-25": {"Empuxo": "1860 kN", "ISP": "452 s", "Combustível": "LH2/LOX"},
    "Raptor": {"Empuxo": "1850 kN", "ISP": "330 s", "Combustível": "Metano/LOX"},
    "Merlin": {"Empuxo": "845 kN", "ISP": "311 s", "Combustível": "RP-1/LOX"},
    "Nerva": {"Empuxo": "111 kN", "ISP": "825 s", "Combustível": "Nuclear Thermal"},
    "Darco": {"Empuxo": "500 kN", "ISP": "350 s", "Combustível": "Híbrido"}
}

# --- Funções de jogo ---
def atualizar_creditos():
    creditos_label.config(text=f"Créditos: {creditos} 💰")

def atualizar_fila():
    if fila:
        fila_text.set('\n'.join([f"{i+1}: {m['tipo']} Pot:{m['potencia']} Est:{m['estabilidade']}" 
                                  for i,m in enumerate(fila)]))
    else:
        fila_text.set("Fila vazia")

def atualizar_grafico():
    grafico_canvas.delete("all")
    ultimos = historico[-10:]
    width = 25
    spacing = 10
    for i, val in enumerate(ultimos):
        x0 = i*(width+spacing)
        y0 = 150 - val*1.5
        x1 = x0 + width
        y1 = 150
        grafico_canvas.create_rectangle(x0, y0, x1, y1, fill="#00ffcc")

def gerar_contratos():
    contratos.clear()
    for i in range(3):
        pot = random.randint(30, 79)
        est = random.randint(30, 79)
        pagamento = pot*2 + est*2
        contratos.append({"potenciaMin": pot, "estMin": est, "pagamento": pagamento})
    render_contratos()

def render_contratos():
    for widget in contratos_frame.winfo_children():
        widget.destroy()
    for i, c in enumerate(contratos):
        frame = tk.Frame(contratos_frame, bg="#222", bd=1, relief="solid")
        frame.pack(padx=5, pady=5, fill="x")
        tk.Label(frame, text=f"Contrato {i+1}  Pot≥{c['potenciaMin']}  Est≥{c['estMin']}  💰{c['pagamento']}", 
                 bg="#222", fg="white").pack(side="left")
        tk.Button(frame, text="Aceitar", command=lambda i=i: aceitar_contrato(i), bg="#ff6600", fg="white").pack(side="right")

def aceitar_contrato(idx):
    contrato = contratos.pop(idx)
    motor = {"potencia": contrato["potenciaMin"] + random.randint(0,19),
             "estabilidade": contrato["estMin"] + random.randint(0,19),
             "custo":50,
             "tipo":"Contrato"}
    fila.append(motor)
    atualizar_fila()
    render_contratos()
    if len(fila) == 1:
        produzir_motor()

def adicionar_motor():
    motor = {"potencia": potencia_slider.get(),
             "estabilidade": estabilidade_slider.get(),
             "custo": custo_slider.get(),
             "tipo":"Custom"}
    fila.append(motor)
    atualizar_fila()
    if len(fila) == 1:
        produzir_motor()

def produzir_motor():
    global creditos
    if not fila:
        return
    motor = fila[0]
    resultado_label.config(text="Produzindo motor... 🚀")
    barra_progresso['value'] = 0

    def progresso_step(val=0):
        if val > 100:
            chance = motor['estabilidade'] - (motor['potencia']/2) - (motor['custo']/5) + 50
            chance = max(0, min(100, chance))
            resultado_val = random.uniform(0,100)
            msg = f"Chance de sucesso: {chance:.1f}%\n"
            global creditos
            if resultado_val <= chance:
                msg += "✅ Motor aprovado!"
                ganho = 200 + motor['potencia']//2
                creditos += ganho
                historico.append(100)
                # foguete sobe
                foguete.place(y=foguete.winfo_y()-150)
                root.after(1500, lambda: foguete.place(y=foguete.winfo_y()+150))
            elif resultado_val <= chance+20:
                msg += "⚠️ Falha leve."
                creditos += 50
                historico.append(50)
            else:
                msg += "💥 Falha crítica!"
                creditos -= 100
                historico.append(10)
            resultado_label.config(text=msg)
            atualizar_creditos()
            fila.pop(0)
            atualizar_fila()
            atualizar_grafico()
            if fila:
                root.after(1000, produzir_motor)
            return
        barra_progresso['value'] = val
        root.after(200, lambda: progresso_step(val+10))
    progresso_step()

def mostrar_motor_pesquisa():
    sel = lista_pesquisa.curselection()
    if sel:
        motor = lista_pesquisa.get(sel[0])
        info = pesquisa_motores[motor]
        texto = f"{motor}:\nEmpuxo: {info['Empuxo']}\nISP: {info['ISP']}\nCombustível: {info['Combustível']}"
        pesquisa_label.config(text=texto)

# --- GUI ---
root = tk.Tk()
root.title("Tycoon Aerojet Rocketdyne 🚀")
root.configure(bg="#111")
root.geometry("1100x650")

# Título
tk.Label(root, text="Tycoon Aerojet Rocketdyne 🚀", font=("Arial", 24), fg="#ffcc00", bg="#111").pack(pady=5)
tk.Label(root, text="Desenvolva e teste motores de foguete", font=("Arial", 16), fg="#66ffcc", bg="#111").pack(pady=5)

main_frame = tk.Frame(root, bg="#111")
main_frame.pack(pady=10, fill="both", expand=True)

# Configuração do motor
config_frame = tk.Frame(main_frame, bg="#111")
config_frame.grid(row=0, column=0, padx=10, sticky="n")
tk.Label(config_frame, text="Configuração do Motor", fg="white", bg="#111", font=("Arial",14)).pack(pady=5)
potencia_slider = tk.Scale(config_frame, from_=0, to=100, orient="horizontal", label="Potência", bg="#111", fg="white",
                           troughcolor="#333", highlightthickness=0, length=200)
potencia_slider.set(50)
potencia_slider.pack(pady=5)
estabilidade_slider = tk.Scale(config_frame, from_=0, to=100, orient="horizontal", label="Estabilidade", bg="#111", fg="white",
                               troughcolor="#333", highlightthickness=0, length=200)
estabilidade_slider.set(50)
estabilidade_slider.pack(pady=5)
custo_slider = tk.Scale(config_frame, from_=0, to=100, orient="horizontal", label="Custo", bg="#111", fg="white",
                        troughcolor="#333", highlightthickness=0, length=200)
custo_slider.set(50)
custo_slider.pack(pady=5)
tk.Button(config_frame, text="Produzir Motor", command=adicionar_motor, bg="#ff6600", fg="white").pack(pady=10)

# Fila e progresso
fila_frame = tk.Frame(main_frame, bg="#111")
fila_frame.grid(row=0, column=1, padx=10, sticky="n")
tk.Label(fila_frame, text="Fila de Produção", fg="white", bg="#111", font=("Arial",14)).pack(pady=5)
fila_text = tk.StringVar()
tk.Label(fila_frame, textvariable=fila_text, fg="white", bg="#111", justify="left").pack()
barra_progresso = ttk.Progressbar(fila_frame, orient="horizontal", length=200, mode="determinate")
barra_progresso.pack(pady=5)
resultado_label = tk.Label(fila_frame, text="", fg="white", bg="#111")
resultado_label.pack(pady=5)
creditos_label = tk.Label(fila_frame, text=f"Créditos: {creditos} 💰", fg="white", bg="#111")
creditos_label.pack()

# Estatísticas
estat_frame = tk.Frame(main_frame, bg="#111")
estat_frame.grid(row=0, column=2, padx=10, sticky="n")
tk.Label(estat_frame, text="Estatísticas", fg="white", bg="#111", font=("Arial",14)).pack(pady=5)
grafico_canvas = tk.Canvas(estat_frame, width=300, height=150, bg="#111", bd=1, relief="solid")
grafico_canvas.pack(pady=5)

# Contratos
contratos_frame = tk.Frame(main_frame, bg="#111")
contratos_frame.grid(row=0, column=3, padx=10, sticky="n")
tk.Label(contratos_frame, text="Mercado de Contratos", fg="white", bg="#111", font=("Arial",14)).pack(pady=5)

# Pesquisa de motores
pesquisa_frame = tk.Frame(root, bg="#111")
pesquisa_frame.pack(pady=10)
tk.Label(pesquisa_frame, text="Pesquisa de Motores Reais", fg="#66ffcc", bg="#111", font=("Arial",14)).pack()
lista_pesquisa = tk.Listbox(pesquisa_frame, width=20, height=5, bg="#222", fg="white")
lista_pesquisa.pack(side="left", padx=10)
for motor in pesquisa_motores.keys():
    lista_pesquisa.insert(tk.END, motor)
pesquisa_label = tk.Label(pesquisa_frame, text="", fg="white", bg="#111", justify="left")
pesquisa_label.pack(side="left", padx=10)
tk.Button(pesquisa_frame, text="Ver Detalhes", command=mostrar_motor_pesquisa, bg="#ff6600", fg="white").pack(side="left", padx=10)

# Foguete animado
foguete = tk.Label(root, text="🚀", font=("Arial", 48), bg="#111")
foguete.place(x=500, y=500)

# Inicialização
atualizar_fila()
atualizar_creditos()
gerar_contratos()

root.mainloop()