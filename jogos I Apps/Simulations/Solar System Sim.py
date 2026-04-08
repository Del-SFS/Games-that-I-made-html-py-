import tkinter as tk
import random
import math

# --- Tipos de estrelas e planetas (mesmo do código anterior) ---
tipos_estrela = [
    {"nome": "M (Anã Vermelha)", "cor": "#ff4d4d", "hzMin": 0.1, "hzMax": 0.4, "massa": 0.3},
    {"nome": "K (Anã Laranja)", "cor": "#ff9933", "hzMin": 0.3, "hzMax": 0.8, "massa": 0.7},
    {"nome": "G (Sol)", "cor": "#f9d71c", "hzMin": 0.8, "hzMax": 1.6, "massa": 1.0},
    {"nome": "F (Branca)", "cor": "#ffffff", "hzMin": 1.5, "hzMax": 2.8, "massa": 1.4},
]

tipos_planeta = [
    {"nome": "Rochoso", "cor": "#a88e7a"},
    {"nome": "Gigante Gasoso", "cor": "#e3bb76"},
    {"nome": "Oceânico", "cor": "#2b65ec"},
    {"nome": "Desértico", "cor": "#edc9af"},
    {"nome": "Gelado", "cor": "#d0f0f7"},
    {"nome": "Vulcânico", "cor": "#ff4500"},
    {"nome": "Superterra", "cor": "#8b4513"},
    {"nome": "Mini Neptuno", "cor": "#7ec0ee"},
    {"nome": "Terra Alienígena", "cor": "#66ff66"},
]

# --- Funções físicas (mesmas do código anterior) ---
def gerar_raio(tipo):
    if tipo == "Rochoso": return random.uniform(0.5,1.5)
    elif tipo == "Gigante Gasoso": return random.uniform(5,12)
    elif tipo == "Oceânico": return random.uniform(0.8,1.3)
    elif tipo == "Desértico": return random.uniform(0.5,1.5)
    elif tipo == "Gelado": return random.uniform(1,3)
    elif tipo == "Vulcânico": return random.uniform(0.7,1.2)
    elif tipo == "Superterra": return random.uniform(1.5,2.5)
    elif tipo == "Mini Neptuno": return random.uniform(2,4)
    elif tipo == "Terra Alienígena": return random.uniform(0.8,1.5)
    return 1.0

def gerar_massa(tipo):
    if tipo == "Rochoso": return random.uniform(0.5,1.5)
    elif tipo == "Gigante Gasoso": return random.uniform(50,300)
    elif tipo == "Oceânico": return random.uniform(0.8,1.2)
    elif tipo == "Desértico": return random.uniform(0.5,1.5)
    elif tipo == "Gelado": return random.uniform(2,10)
    elif tipo == "Vulcânico": return random.uniform(0.7,1.3)
    elif tipo == "Superterra": return random.uniform(2,10)
    elif tipo == "Mini Neptuno": return random.uniform(10,20)
    elif tipo == "Terra Alienígena": return random.uniform(0.8,1.5)
    return 1.0

def estimar_temperatura(dist, estrela):
    luminosidade = estrela["massa"]**3.5
    temp_k = 288 * (luminosidade / dist**2) ** 0.25
    return round(temp_k - 273.15,1)

def calcular_gravidade(massa, raio):
    return round(massa/(raio**2),2)

def gerar_atmosfera(tipo):
    if tipo in ["Rochoso","Oceânico","Superterra","Terra Alienígena"]:
        return random.choice(["N2/O2","CO2","Metano","Mista"])
    elif tipo in ["Gigante Gasoso","Mini Neptuno"]:
        return random.choice(["H/He","H2O","NH3"])
    return "Irrespirável"

def calcular_vida(habitavel, temp, atmosfera, gravidade):
    if not habitavel: return "Nenhuma"
    if -50<temp<50 and "O2" in atmosfera and 0.5<gravidade<2:
        return random.choice(["Simples","Complexa","Inteligente"])
    return "Limitada"

# --- Simulador ---
class Simulador(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador Estelar Avançado")
        self.geometry("900x700")
        self.configure(bg="#05070a")

        self.zoom_factor = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.drag_data = {"x":0,"y":0}

        self.btn_frame = tk.Frame(self,bg="#eee")
        self.btn_frame.pack(side=tk.BOTTOM,fill=tk.X)
        self.btn_desacelerar = tk.Button(self.btn_frame,text="Desacelerar",command=self.desacelerar)
        self.btn_desacelerar.pack(side=tk.LEFT,padx=5,pady=5)
        self.btn_normal = tk.Button(self.btn_frame,text="Normal",command=self.normalizar)
        self.btn_normal.pack(side=tk.LEFT,padx=5,pady=5)
        self.btn_acelerar = tk.Button(self.btn_frame,text="Acelerar",command=self.acelerar)
        self.btn_acelerar.pack(side=tk.LEFT,padx=5,pady=5)
        self.btn_gerar = tk.Button(self.btn_frame,text="Descobrir Novo Sistema",command=self.gerar_sistema,
                                   bg="#4facfe",fg="white",font=("Arial",14),padx=20,pady=10)
        self.btn_gerar.pack(pady=10)

        self.canvas = tk.Canvas(self,bg="#05070a",highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH,expand=True)
        self.info_label = tk.Label(self,text="",bg="#05070a",fg="white",font=("Arial",10),justify="left")
        self.info_label.pack(side=tk.BOTTOM,pady=5)

        self.planetas = []
        self.animando = False
        self.velocidade_tempo = 1.0

        self.canvas.bind("<ButtonPress-1>",self.iniciar_drag)
        self.canvas.bind("<B1-Motion>",self.arrastar)
        self.canvas.bind("<MouseWheel>",self.zoom)

    def desacelerar(self): self.velocidade_tempo=max(0.1,self.velocidade_tempo/2)
    def normalizar(self): self.velocidade_tempo=1.0
    def acelerar(self): self.velocidade_tempo=min(10.0,self.velocidade_tempo*2)
    def iniciar_drag(self,event): self.drag_data={"x":event.x,"y":event.y}
    def arrastar(self,event):
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        self.offset_x += dx
        self.offset_y += dy
        self.drag_data = {"x":event.x,"y":event.y}
        self.desenhar_sistema()
    def zoom(self,event):
        fator = 1.1 if event.delta>0 else 0.9
        self.zoom_factor *= fator
        self.zoom_factor = max(0.2,min(5.0,self.zoom_factor))
        self.desenhar_sistema()

    def gerar_sistema(self):
        self.planetas.clear()
        # Estrelas múltiplas sem sobreposição
        num_estrelas = random.choices([1,2,3,4],weights=[0.6,0.3,0.08,0.02])[0]
        self.estrelas = []
        self.posicoes_estrelas = []
        min_dist_estrela = 100
        for i in range(num_estrelas):
            estrela = random.choice(tipos_estrela)
            # Posiciona estrela sem sobrepor a outra
            while True:
                x = random.randint(-150,150)
                y = random.randint(-150,150)
                if all(math.hypot(x-ex, y-ey) > min_dist_estrela for ex,ey in self.posicoes_estrelas):
                    break
            self.estrelas.append(estrela)
            self.posicoes_estrelas.append((x,y))

        # Planetas sem sobreposição
        num_planetas = random.randint(4,10)
        orbit_gap = 50
        orbit_positions = []
        for i in range(num_planetas):
            tipo = random.choice(tipos_planeta)
            # Escolhe órbita sem colidir com outras
            while True:
                dist = random.randint(orbit_gap, orbit_gap*10)
                if all(abs(dist - d) > orbit_gap for d in orbit_positions):
                    orbit_positions.append(dist)
                    break
            habitavel = any(e["hzMin"] <= dist/80 <= e["hzMax"] for e in self.estrelas) and tipo["nome"] in ["Rochoso","Oceânico","Superterra","Terra Alienígena"]
            raio = gerar_raio(tipo["nome"])*5
            massa = gerar_massa(tipo["nome"])
            temp = estimar_temperatura(dist/80,self.estrelas[0])
            gravidade = calcular_gravidade(massa,raio/10)
            atmosfera = gerar_atmosfera(tipo["nome"])
            vida = calcular_vida(habitavel,temp,atmosfera,gravidade)
            composicao = tipo["nome"]
            luas = random.randint(0,4)
            anel = random.random()<0.4
            planeta = {"tipo":tipo,"dist":dist,"raio":raio,"angulo":random.uniform(0,360),
                       "velocidade":random.uniform(0.2,1.0),"habitavel":habitavel,"massa":massa,
                       "temp":temp,"gravidade":gravidade,"atmosfera":atmosfera,"vida":vida,
                       "composicao":composicao,"luas":luas,"anel":anel,"luas_ovals":[]}
            self.planetas.append(planeta)

        self.offset_x=0
        self.offset_y=0
        self.zoom_factor=1.0
        self.desenhar_sistema()
        if not self.animando:
            self.animar_planetas()
            self.animando=True

    def desenhar_sistema(self):
        self.canvas.delete("all")
        largura, altura = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = largura/2+self.offset_x, altura/2+self.offset_y

        # Estrelas
        for idx, estrela in enumerate(self.estrelas):
            ex, ey = self.posicoes_estrelas[idx]
            star_radius = 30*self.zoom_factor
            for i in range(5):
                brilho_radius = star_radius + i*5*self.zoom_factor
                self.canvas.create_oval(cx+ex-brilho_radius, cy+ey-brilho_radius,
                                        cx+ex+brilho_radius, cy+ey+brilho_radius,
                                        outline=estrela["cor"], width=1)
            self.canvas.create_oval(cx+ex-star_radius, cy+ey-star_radius,
                                    cx+ex+star_radius, cy+ey+star_radius,
                                    fill=estrela["cor"], outline="")
            self.canvas.create_text(cx+ex, cy+ey+star_radius+15,
                                    text=f"{estrela['nome']}\nHZ: {estrela['hzMin']}-{estrela['hzMax']} UA",
                                    fill="white", font=("Arial",12))

        # Planetas
        for p in self.planetas:
            p["angulo"] += p["velocidade"]*self.velocidade_tempo
            rad = math.radians(p["angulo"])
            x = cx + p["dist"]*math.cos(rad)*self.zoom_factor
            y = cy + p["dist"]*math.sin(rad)*self.zoom_factor
            raio = p["raio"]*self.zoom_factor
            outline_color = "lime" if p["habitavel"] else "white"
            oval = self.canvas.create_oval(x-raio, y-raio, x+raio, y+raio, fill=p["tipo"]["cor"], outline=outline_color, width=2)

            if p["anel"]:
                self.canvas.create_oval(x-raio*1.5, y-raio*1.5, x+raio*1.5, y+raio*1.5, outline="gray", width=2)

            for idx_lua in range(p["luas"]):
                angle_lua = math.radians(p["angulo"]*1.5 + idx_lua*90)
                dist_lua = raio*1.5 + idx_lua*3
                lx = x + dist_lua*math.cos(angle_lua)
                ly = y + dist_lua*math.sin(angle_lua)
                self.canvas.create_oval(lx-2, ly-2, lx+2, ly+2, fill="white")

            info = f"{p['tipo']['nome']} {'[HABITÁVEL]' if p['habitavel'] else ''}\nDist: {round(p['dist']/80,2)} UA | Luas: {p['luas']}\nTemp: {p['temp']}°C | Grav: {p['gravidade']} g\nVida: {p['vida']}\nComposição: {p['composicao']}\nAnel: {'Sim' if p['anel'] else 'Não'}"
            self.canvas.tag_bind(oval,"<Enter>", lambda e,text=info: self.mostrar_info(text))
            self.canvas.tag_bind(oval,"<Leave>", lambda e: self.limpar_info())

    def animar_planetas(self):
        self.desenhar_sistema()
        self.after(50,self.animar_planetas)

    def mostrar_info(self,text): self.info_label.config(text=text)
    def limpar_info(self): self.info_label.config(text="")

if __name__=="__main__":
    app = Simulador()
    app.mainloop()