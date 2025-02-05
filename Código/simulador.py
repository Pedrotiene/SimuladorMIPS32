import tkinter as tk
from tkinter import filedialog, scrolledtext

class SimuladorMIPS32:
    def __init__(self):
        self.registradores = self.inicializar_registradores()
        self.cont = 0 
        self.instrucoes = []
        self.saidas = []
    
    def inicializar_registradores(self):
        return {
            '$zero': 0, '$at': 0, '$v0': 0, '$v1': 0, '$a0': 0, '$a1': 0, '$a2': 0, '$a3': 0,
            '$t0': 0, '$t1': 0, '$t2': 0, '$t3': 0, '$t4': 0, '$t5': 0, '$t6': 0, '$t7': 0,
            '$s0': 0, '$s1': 0, '$s2': 0, '$s3': 0, '$s4': 0, '$s5': 0, '$s6': 0, '$s7': 0,
            '$t8': 0, '$t9': 0, '$k0': 0, '$k1': 0, '$gp': 0, '$sp': 0, '$fp': 0, '$ra': 0
        }
    
    def carregar_instrucoes(self, nome_arquivo):
        with open(nome_arquivo, 'r') as arquivo:
            self.instrucoes = [linha.split('#')[0].strip() for linha in arquivo.readlines() if linha.strip() and not linha.startswith('#')]
    
    def executar(self):
        self.saidas.clear()
        while self.cont < len(self.instrucoes): 
            instrucao = self.instrucoes[self.cont]
            if instrucao.startswith("syscall"):
                if self.registradores['$v0'] == 10:
                    self.saidas.append("Programa encerrado")
                    break
                elif self.registradores['$v0'] == 1:
                    self.saidas.append(f"Saída: {self.registradores['$a0']}")
            self.cont += 1
            self.executar_instrucao(instrucao)
    
    def executar_instrucao(self, instrucao):
        partes = instrucao.replace(',', '').split()
        opcode = partes[0]
    
        if opcode == 'add':
            _, rd, rs, rt = partes
            self.registradores[rd] = self.registradores[rs] + self.registradores[rt]
        elif opcode == 'addi':
            _, rt, rs, imediato = partes
            self.registradores[rt] = self.registradores[rs] + int(imediato)
        elif opcode == 'sub':
            _, rd, rs, rt = partes
            self.registradores[rd] = self.registradores[rs] - self.registradores[rt]
        elif opcode == 'mult':
            _, rd, rs, rt = partes
            self.registradores[rd] = self.registradores[rs] * self.registradores[rt]
        elif opcode == 'and':
            _, rd, rs, rt = partes
            self.registradores[rd] = self.registradores[rs] & self.registradores[rt]
        elif opcode == 'or':
            _, rd, rs, rt = partes
            self.registradores[rd] = self.registradores[rs] | self.registradores[rt]
        elif opcode == 'sll':
            _, rd, rt, shamt = partes
            self.registradores[rd] = self.registradores[rt] << int(shamt)
        elif opcode == 'li':
            _, rt, imediato = partes
            self.registradores[rt] = int(imediato)
    
    def resetar(self):
        self.registradores = self.inicializar_registradores()
        self.cont = 0
        self.instrucoes.clear()
        self.saidas.clear()
    
    def obter_texto_registradores(self):
        return '\n'.join([f'{reg}: {val}' for reg, val in self.registradores.items()])
    
    def obter_saidas(self):
        return '\n'.join(self.saidas)

class MIPS_GUI:
    def __init__(self, root):
        self.simulador = SimuladorMIPS32()
        self.root = root
        self.root.title("Simulador MIPS32")
        
        self.frame_superior = tk.Frame(root)
        self.frame_superior.pack()
        
        self.botao_carregar = tk.Button(self.frame_superior, text="Carregar Programa", command=self.carregar_arquivo)
        self.botao_carregar.pack(side=tk.LEFT)
        
        self.botao_executar = tk.Button(self.frame_superior, text="Executar", command=self.executar_simulacao)
        self.botao_executar.pack(side=tk.LEFT)
        
        self.botao_resetar = tk.Button(self.frame_superior, text="Resetar", command=self.resetar_simulacao)
        self.botao_resetar.pack(side=tk.LEFT)
        
        self.frame_meio = tk.Frame(root)
        self.frame_meio.pack()
        
        self.area_registradores = scrolledtext.ScrolledText(self.frame_meio, width=30, height=20)
        self.area_registradores.pack(side=tk.LEFT, padx=10)
        self.area_registradores.insert(tk.INSERT, "Registradores:\n")
        
        self.area_saidas = scrolledtext.ScrolledText(self.frame_meio, width=50, height=20)
        self.area_saidas.pack(side=tk.RIGHT, padx=10)
        self.area_saidas.insert(tk.INSERT, "Saídas:\n")
    
    def carregar_arquivo(self):
        nome_arquivo = filedialog.askopenfilename(filetypes=[("Arquivos de Texto", "*.txt")])
        if nome_arquivo:
            self.simulador.carregar_instrucoes(nome_arquivo)
    
    def executar_simulacao(self):
        self.simulador.executar()
        self.atualizar_interface()
    
    def resetar_simulacao(self):
        self.simulador.resetar()
        self.atualizar_interface()
    
    def atualizar_interface(self):
        self.area_registradores.delete(1.0, tk.END)
        self.area_registradores.insert(tk.INSERT, self.simulador.obter_texto_registradores())
        
        self.area_saidas.delete(1.0, tk.END)
        self.area_saidas.insert(tk.INSERT, self.simulador.obter_saidas())

if __name__ == '__main__':
    root = tk.Tk()
    app = MIPS_GUI(root)
    root.mainloop()
