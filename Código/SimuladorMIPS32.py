#Arthur Palma e Pedro Tiene

import tkinter as tk
from tkinter import filedialog, scrolledtext

class SimuladorMIPS32:
    def __init__(self):
        self.registradores = self.inicializar_registradores()
        self.cont = 0
        self.instrucoes = []
        self.saidas = []
        self.bin = []
        self.rotulos = {}
        self.dados = {}
        self.vetores = {}

    def inicializar_registradores(self):
        return {
            '$zero': 0, '$at': 0, '$v0': 0, '$v1': 0, '$a0': 0, '$a1': 0, '$a2': 0, '$a3': 0,
            '$t0': 0, '$t1': 0, '$t2': 0, '$t3': 0, '$t4': 0, '$t5': 0, '$t6': 0, '$t7': 0,
            '$s0': 0, '$s1': 0, '$s2': 0, '$s3': 0, '$s4': 0, '$s5': 0, '$s6': 0, '$s7': 0,
            '$t8': 0, '$t9': 0, '$k0': 0, '$k1': 0, '$gp': 0, '$sp': 0, '$fp': 0, '$ra': 0
        }

    def carregar_instrucoes(self, nome_arquivo):
        self.instrucoes = []
        self.rotulos = {}
        self.dados = {}
        self.vetores = {}
        with open(nome_arquivo, 'r') as arquivo:
            secao = None
            for linha in arquivo.readlines():
                linha = linha.split('#')[0].strip()
                if not linha:
                    continue
                if linha.startswith('.data'):
                    secao = 'data'
                elif linha.startswith('.text'):
                    secao = 'text'
                elif secao == 'data' and linha:
                    partes = linha.split()
                    if len(partes) >= 2:
                        var = partes[0]
                        var = var[:-1]
                        tipo = partes[1]
                        if tipo == '.word':
                            try:
                                valores = [int(valor.strip()) for valor in partes[2].split(',')]
                                self.vetores[var] = valores
                            except ValueError:
                                print(f"Erro: Valor inválido na linha1: {linha}")
                        elif tipo == '.byte':
                            try:
                                valores = [int(valor.strip()) for valor in partes[2].split(',')]
                                self.vetores[var] = valores
                            except ValueError:
                                print(f"Erro: Valor inválido na linha2: {linha}")
                        elif tipo == '.space':
                            try:
                                tamanho = int(partes[2])
                                self.vetores[var] = [0] * tamanho
                            except ValueError:
                                print(f"Erro: Tamanho inválido na linha: {linha}")
                        elif tipo == '.asciiz':
                            string_valor = linha.split('.asciiz')[1].strip().strip('"')
                            self.dados[var] = string_valor
                        else:
                            try:
                                valor = int(partes[2]) if len(partes) > 2 else 0
                                self.dados[var] = valor
                            except ValueError:
                                print(f"Erro: Valor inválido na linha3: {linha}")
                elif secao == 'text' and linha:
                    if linha.endswith(':'):
                        rotulo = linha[:-1]
                        self.rotulos[rotulo] = len(self.instrucoes)
                    else:
                        self.instrucoes.append(linha)

    def executar(self):
        self.saidas.clear()
        while self.cont < len(self.instrucoes):
            instrucao = self.instrucoes[self.cont]
            if instrucao.startswith("syscall"):
                if self.registradores['$v0'] == 10:
                    break
                elif self.registradores['$v0'] == 1:
                    self.saidas.append(self.registradores['$a0'])
                elif self.registradores['$v0'] == 4:
                    endereco = self.registradores['$a0']
                    for chave, valor in self.dados.items():
                        if endereco == hash(chave):
                            self.saidas.append(valor)
            self.cont += 1
            self.executar_instrucao(instrucao)

    def executar_instrucao(self, instrucao):
        partes = instrucao.replace(',', '').split()
        opcode = partes[0]

        binario = self.traduzir_para_binario(instrucao)
        self.bin.append(f"Instrução: {instrucao} -> Binário: {binario}")

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
        elif opcode == 'slt':
            _, rd, rs, rt = partes
            if self.registradores[rs] < self.registradores[rt]:
                self.registradores[rd] = 1
            else:
                self.registradores[rd] = 0
        elif opcode == 'slti':
            _, rt, rs, imediato = partes
            if self.registradores[rs] < int(imediato):
                self.registradores[rt] = 1
            else:
                self.registradores[rt] = 0
        elif opcode == 'li':
            _, rt, imediato = partes
            self.registradores[rt] = int(imediato)
        elif opcode == 'la':
            _, rt, label = partes
            self.registradores[rt] = hash(label) if label in self.dados else 0
        elif opcode == 'lw':
            if len(partes) < 3:
                print(f"Erro: Instrução 'lw' malformada: {instrucao}")
                return
            rt = partes[1]
            offset_endereco = partes[2]
            try:
                offset, endereco = offset_endereco.split('(')
                endereco = endereco[:-1]
                offset = int(offset)
                if endereco in self.vetores:
                    if isinstance(self.vetores[endereco], list):
                        indice = offset // 4 
                        if 0 <= indice < len(self.vetores[endereco]):
                            self.registradores[rt] = self.vetores[endereco][indice]
                        else:
                            print(f"Erro: Índice fora dos limites no vetor '{endereco}'")
                    else:
                        print(f"Erro: '{endereco}' não é um vetor de palavras")
                elif endereco in self.dados:
                    self.registradores[rt] = self.dados[endereco]
                else:
                    print(f"Erro: Endereço '{endereco}' não encontrado")
            except ValueError:
                print(f"Erro: Formato inválido na instrução 'lw': {instrucao}")
        elif opcode == 'sw':
            if len(partes) < 3:
                print(f"Erro: Instrução 'sw' malformada: {instrucao}")
                return
            rt = partes[1]
            offset_endereco = partes[2]
            try:
                offset, endereco = offset_endereco.split('(')
                endereco = endereco[:-1]
                offset = int(offset)
                if endereco in self.vetores:
                    if isinstance(self.vetores[endereco], list):
                        indice = offset // 4
                        if 0 <= indice < len(self.vetores[endereco]):
                            self.vetores[endereco][indice] = self.registradores[rt]
                        else:
                            print(f"Erro: Índice fora dos limites no vetor '{endereco}'")
                    else:
                        print(f"Erro: '{endereco}' não é um vetor de palavras")
                else:
                    self.dados[endereco] = self.registradores[rt]
            except ValueError:
                print(f"Erro: Formato inválido na instrução 'sw': {instrucao}")

    def traduzir_para_binario(self, instrucao):
        partes = instrucao.replace(',', '').split()
        opcode = partes[0]

        tabela_opcode = {
            'add': '000000',
            'addi': '001000',
            'sub': '000000',
            'mult': '000000',
            'and': '000000',
            'or': '000000',
            'sll': '000000',
            'li': '001111',
            'syscall': '000000',
            'lw': '100011',
            'sw': '101011',
            'slt': '101010',
            'slti': '001010',
            'la': '001101',
        }

        if opcode in tabela_opcode:
            return tabela_opcode[opcode]
        else:
            return 'Instrução não reconhecida'

    def resetar(self):
        self.registradores = self.inicializar_registradores()
        self.cont = 0
        self.instrucoes.clear()
        self.saidas.clear()
        self.bin.clear()

    def obter_texto_registradores(self):
        return '\n'.join([f'{reg}: {val}' for reg, val in self.registradores.items()])

    def obter_saidas(self):
        return '\n'.join(map(str, self.saidas))

    def obter_texto_vetores(self):
        texto = "Vetores:\n"
        for nome, valores in self.vetores.items():
            texto += f"{nome}: {valores}\n"
        return texto

    def obter_binarios(self):
        return '\n'.join(self.bin)


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

        self.area_registradores = scrolledtext.ScrolledText(self.frame_meio, width=20, height=20)
        self.area_registradores.pack(side=tk.LEFT, padx=10)
        self.area_registradores.insert(tk.INSERT, "Registradores:\n")

        self.area_bin = scrolledtext.ScrolledText(self.frame_meio, width=50, height=20)
        self.area_bin.pack(side=tk.LEFT, padx=10)
        self.area_bin.insert(tk.INSERT, "Binários:\n")

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
        self.area_registradores.insert(tk.INSERT, "Registradores:\n" + self.simulador.obter_texto_registradores())

        self.area_saidas.delete(1.0, tk.END)
        self.area_saidas.insert(tk.INSERT, "Saidas:\n" + self.simulador.obter_saidas())

        self.area_bin.delete(1.0, tk.END)
        self.area_bin.insert(tk.INSERT, "Binários:\n")
        self.area_bin.insert(tk.INSERT, self.simulador.obter_binarios())


if __name__ == '__main__':
    root = tk.Tk()
    app = MIPS_GUI(root)
    root.mainloop()
