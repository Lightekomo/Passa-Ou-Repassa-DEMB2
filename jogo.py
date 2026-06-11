from flask import Flask, render_code, render_template, request, jsonify
import os

app = Flask(__name__, template_folder='.', static_folder='.')

# BANCO DE QUESTÕES (Reduzido para 5 por nível para exemplo dinâmico)
PERGUNTAS = {
    "facil": {
        "titulo": "Nível Fácil: As Oxítonas Desesperadas",
        "contexto": "Oxítonas levam acento quando terminam em A, E, O (seguidas ou não de S), EM e ENS. O resto fica sem nada!",
        "questoes": [
            {"pergunta": "O herói da quebrada, o 'Café', perdeu o acento e virou 'Cafe'. Como ele recupera o seu brilho?", "opcoes": ["Colocando acento agudo porque termina em 'E'.", "Deixando sem acento.", "Colocando acento circunflexo."], "correta": 0},
            {"pergunta": "A palavra 'Parabéns' está numa festa. Por que ela usa um acento agudo elegante?", "opcoes": ["Porque termina em 'ENS'.", "Porque é véspera de feriado.", "Para não ser confundida."], "correta": 0},
            {"pergunta": "A palavra 'Caju' tentou entrar na área VIP do acento. Por que ela foi barrada?", "opcoes": ["Porque terminou em 'U'.", "Porque o segurança não quis.", "Porque esqueceu o RG."], "correta": 0},
            {"pergunta": "O 'Sofá' desmaiou de cansaço. Qual o remédio ortográfico para ele?", "opcoes": ["Acento agudo no 'A'.", "Um travesseiro novo.", "Deixá-lo como 'Sofa'."], "correta": 0},
            {"pergunta": "A palavra 'Também' está num dilema. Ela precisa de acento?", "opcoes": ["Sim, agudo no 'E' porque termina em 'EM'.", "Não, prefere ficar sem.", "Apenas no início."], "correta": 0}
        ]
    },
    "medio": {
        "titulo": "Nível Médio: A Revolta das Paroxítonas",
        "contexto": "Paroxítonas SÓ levam acento se NÃO terminarem em A, E, O, EM, ENS.",
        "questoes": [
            {"pergunta": "A palavra 'Ideia' perdeu o acento. Por quê?", "opcoes": ["O acento escorregou.", "Ditongos abertos em paroxítonas perderam o acento.", "Ficou famosa demais."], "correta": 1},
            {"pergunta": "A palavra 'Fácil' anda muito orgulhosa. Por que ela tem acento?", "opcoes": ["Porque é uma paroxítona terminada em 'L'.", "Porque o antônimo também tem.", "Para humilhar."], "correta": 0},
            {"pergunta": "O 'Caráter' de uma palavra é tudo. Por que ela é acentuada?", "opcoes": ["Porque termina em 'R'.", "Porque é séria.", "Porque sim."], "correta": 0},
            {"pergunta": "A palavra 'Mesa' está triste porque não tem acento. Qual o motivo?", "opcoes": ["Termina em 'A'.", "Prefere uma toalha.", "Esqueceram na fábrica."], "correta": 0},
            {"pergunta": "O 'Tórax' foi ao médico gramatical. Por que ele precisa de acento?", "opcoes": ["Porque termina em 'X'.", "Porque protege os pulmões.", "O X exigiu."], "correta": 0}
        ]
    },
    "dificil": {
        "titulo": "Nível Difícil: A Ditadura das Proparoxítonas",
        "contexto": "Regra Suprema e Absoluta: TODAS as proparoxítonas são acentuadas. Sem exceção!",
        "questoes": [
            {"pergunta": "Qual é o lema oficial do partido das Proparoxítonas?", "opcoes": ["'Sílaba forte na antepenúltima leva acento e ponto final!'", "'Apenas algumas merecem.'", "'Quem tem acento manda.'"], "correta": 0},
            {"pergunta": "A palavra 'Médico' examinou o dicionário. Qual a receita que ele passou?", "opcoes": ["Acentuar todas as proparoxítonas.", "Tomar duas pílulas.", "Retirar o acento."], "correta": 0},
            {"pergunta": "Se encontrares uma proparoxítona sem acento na rua, o que deves fazer?", "opcoes": ["Chamar a polícia gramatical!", "Ignorar.", "Dar um abraço."], "correta": 0},
            {"pergunta": "A palavra 'Público' está cheia de gente. O que todos têm em comum?", "opcoes": ["Todos respeitam o acento na antepenúltima sílaba.", "Esqueceram os óculos.", "Ver a paródia."], "correta": 0},
            {"pergunta": "A palavra 'Árvore' cresceu muito na floresta. O que brilha no topo dela?", "opcoes": ["O acento agudo no 'Á'.", "Uma maçã.", "Um passarinho."], "correta": 0}
        ]
    }
}

# Estado global da sessão em memória
estado_jogo = {
    "equipe1": "",
    "equipe2": "",
    "pontos": {},
    "nivel_atual": "",
    "titulo": "",
    "contexto": "",
    "pergunta_index": 0,
    "equipe_atual": "",
    "outra_equipe": "",
    "estado_pergunta": "normal", # normal, passou, repassou
    "usou_dica": False,
    "fim_do_nivel": False,
    "questao": None
}

def carregar_questao_atual():
    nivel = PERGUNTAS[estado_jogo["nivel_atual"]]
    idx = estado_jogo["pergunta_index"]
    if idx < len(nivel["questoes"]):
        estado_jogo["questao"] = nivel["questoes"][idx]
        estado_jogo["titulo"] = nivel["titulo"]
        estado_jogo["contexto"] = nivel["contexto"]
        estado_jogo["fim_do_nivel"] = False
    else:
        estado_jogo["fim_do_nivel"] = True

def alternar_turnos():
    estado_jogo["equipe_atual"], estado_jogo["outra_equipe"] = estado_jogo["outra_equipe"], estado_jogo["equipe_atual"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/iniciar', methods=['POST'])
def iniciar():
    data = request.json
    estado_jogo["equipe1"] = data.get("equipe1", "Equipe A")
    estado_jogo["equipe2"] = data.get("equipe2", "Equipe B")
    estado_jogo["pontos"] = {estado_jogo["equipe1"]: 0, estado_jogo["equipe2"]: 0}
    return jsonify(estado_jogo)

@app.route('/api/selecionar_nivel', methods=['POST'])
def selecionar_nivel():
    data = request.json
    estado_jogo["nivel_atual"] = data.get("nivel")
    estado_jogo["pergunta_index"] = 0
    estado_jogo["equipe_atual"] = estado_jogo["equipe1"]
    estado_jogo["outra_equipe"] = estado_jogo["equipe2"]
    estado_jogo["estado_pergunta"] = "normal"
    estado_jogo["usou_dica"] = False
    carregar_questao_atual()
    return jsonify(estado_jogo)

@app.route('/api/jogada', methods=['POST'])
def jogada():
    data = request.json
    acao = data.get("acao")
    valor = data.get("valor")
    feedback = None

    # AÇÃO: PEDIR DICA
    if acao == "dica" and estado_jogo["estado_pergunta"] == "normal" and not estado_jogo["usou_dica"]:
        estado_jogo["usou_dica"] = True
        return jsonify({"estado": estado_jogo, "feedback": None})

    # AÇÃO: PASSAR
    if acao == "passa" and estado_jogo["estado_pergunta"] == "normal" and not estado_jogo["usou_dica"]:
        estado_jogo["estado_pergunta"] = "passou"
        alternar_turnos()
        return jsonify({"estado": estado_jogo, "feedback": None})

    # AÇÃO: REPASSAR
    if acao == "repassa" and estado_jogo["estado_pergunta"] == "passou":
        estado_jogo["estado_pergunta"] = "repassou"
        alternar_turnos()
        return jsonify({"estado": estado_jogo, "feedback": None})

    # AÇÃO: RESPONDER
    if acao == "resposta":
        correta = estado_jogo["questao"]["correta"]
        if int(valor) == correta:
            # ACERTOU
            estado_jogo["pontos"][estado_jogo["equipe_atual"]] += 1
            feedback = {
                "tipo": "sucesso",
                "emoji": "🎉",
                "msg": f"Sensacional! Ponto para a equipe {estado_jogo['equipe_atual']}!"
            }
            # Avança pergunta
            estado_jogo["pergunta_index"] += 1
            estado_jogo["estado_pergunta"] = "normal"
            estado_jogo["usou_dica"] = False
            # Alterna quem inicia a próxima pergunta baseada no índice
            if estado_jogo["pergunta_index"] % 2 == 0:
                estado_jogo["equipe_atual"] = estado_jogo["equipe1"]
                estado_jogo["outra_equibe"] = estado_jogo["equipe2"]
            else:
                estado_jogo["equipe_atual"] = estado_jogo["equipe2"]
                estado_jogo["outra_equipe"] = estado_jogo["equipe1"]
            carregar_questao_atual()
        else:
            # ERROU
            if estado_jogo["estado_pergunta"] == "normal" and not estado_jogo["usou_dica"]:
                # Se errou na normal sem dica, passa automaticamente para a outra responder
                estado_jogo["estado_pergunta"] = "passou"
                alternar_turnos()
                feedback = {
                    "tipo": "erro",
                    "emoji": "❌",
                    "msg": "Errou! A vez passou automaticamente para a outra equipe tentar!"
                }
            else:
                # Se errou com dica, errou no passa ou no repassa: ninguém pontua, avança o jogo
                feedback = {
                    "tipo": "erro",
                    "emoji": "💥",
                    "msg": "Errou feio! Torta na cara e ninguém pontua nesta rodada."
                }
                estado_jogo["pergunta_index"] += 1
                estado_jogo["estado_pergunta"] = "normal"
                estado_jogo["usou_dica"] = False
                if estado_jogo["pergunta_index"] % 2 == 0:
                    estado_jogo["equipe_atual"] = estado_jogo["equipe1"]
                    estado_jogo["outra_equipe"] = estado_jogo["equipe2"]
                else:
                    estado_jogo["equipe_atual"] = estado_jogo["equipe2"]
                    estado_jogo["outra_equipe"] = estado_jogo["equipe1"]
                carregar_questao_atual()

    return jsonify({"estado": estado_jogo, "feedback": feedback})

if __name__ == '__main__':
    # Roda o servidor local na porta 5000
    app.run(debug=True, port=5000)