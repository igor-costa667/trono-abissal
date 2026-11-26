#!/usr/bin/env python3
"""nota_gancho.py - dá nota de 0 a 100 para o gancho (a primeira frase) de um vídeo curto
e ranqueia vários ganchos entre si. Também diz qual das 27 fórmulas (ganchos.json) ele usa.

O que é: cinco checagens feitas só com o texto, no computador do aluno:
  TAMANHO      dá pra falar em até ~3 segundos (5 a 12 palavras)
  CONCRETO     tem número, nome, valor ou algo que se vê (rei, coroa, panela)
  TENSÃO       tem algo em jogo (erro, perda, proibição, segredo, contraste)
  NA FRENTE    a palavra forte aparece logo no começo, sem enrolação
  COM QUEM     fala com quem assiste ("você"), ou manda fazer algo

O que NÃO é: previsão de visualizações. Serve para pegar gancho fraco (saudação,
introdução, nada concreto, frase comprida). Entre dois ganchos bons, quem decide
é a retenção do vídeo publicado.

Adaptado do hookscore.py do Instagram Agent Skill (Jake Schincariol, MIT). Ver CREDITOS.md.

Uso
  python nota_gancho.py ganchos.txt            # um gancho por linha, ranqueados
  python nota_gancho.py --gancho "Pare de lavar o arroz assim."
  python nota_gancho.py ganchos.txt --json
"""
import argparse, json, os, re, statistics, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
PAL_RE = re.compile(r"[\wÀ-ÿ$%'’-]+", re.UNICODE)
NUM_RE = re.compile(r"r\$\s?\d[\d.,]*|\b\d[\d.,]*\s?(?:%|mil\b|k\b|x\b|h\b|horas?\b|min\b|minutos?\b|segundos?\b|dias?\b|semanas?\b|meses\b|m[eê]s\b|anos?\b|reais\b|kg\b)?", re.I)
PROPRIO_RE = re.compile(r"(?<!^)(?<![.!?]\s)\b[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]{2,}\b")
HASHTAG_RE = re.compile(r"(?:^|\s)#\w+")
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF☀-➿]")

NUMEROS_FALADOS = {"zero", "dois", "duas", "três", "tres", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez",
    "onze", "doze", "quinze", "vinte", "trinta", "quarenta", "cinquenta", "sessenta", "setenta", "oitenta", "noventa",
    "cem", "cento", "duzentos", "trezentos", "quinhentos", "mil", "milhão", "milhões", "bilhão", "dúzia", "metade",
    "dobro", "triplo", "primeiro", "primeira", "último", "última"}
DINHEIRO = {"reais", "real", "conto", "contos", "pila", "grana", "dinheiro", "salário", "aluguel", "lucro", "prejuízo",
    "porcento", "cento", "barato", "caro", "grátis", "gratis", "promoção", "desconto"}
VISUAIS = {"rei", "rainha", "príncipe", "princesa", "gigante", "dragão", "monstro", "coroa", "espada", "torre", "castelo",
    "vila", "menino", "menina", "soldado", "bruxa", "fantasma", "porta", "caixa", "arca", "mapa", "chave", "troll", "goblin",
    "lobo", "navio", "ilha", "templo", "profeta", "anjo", "panela", "air", "fryer", "geladeira", "marmita", "arroz", "celular"}
TENSAO = {"pare", "para", "nunca", "errado", "errada", "erro", "erros", "perdi", "perdeu", "perder", "custou", "custa",
    "quebrou", "falhou", "ninguém", "ninguem", "não", "nao", "nem", "proibido", "proibida", "perigo", "perigoso", "cuidado",
    "segredo", "escondido", "escondida", "mentira", "mentiu", "verdade", "pior", "odeio", "lixo", "golpe", "jogou", "fora",
    "antes", "até", "mas", "só", "sem", "contra", "versus", "vs", "realmente", "acabou", "acaba", "último", "última",
    "morreu", "caiu", "matou", "venceu", "ganhou", "traiu", "fugiu", "sumiu", "desapareceu", "maldição", "medo", "estranho",
    "ninguém", "jamais", "deveria", "devia", "arrependo", "arrependimento", "troca", "trocou", "substituiu", "economiza",
    "economizei", "grátis", "ainda", "já", "única", "único", "morresse", "morre", "morrer", "morto", "morta", "mortos",
    "sozinho", "sozinha", "preso", "presa", "monstro", "fantasma", "sangue", "gigante", "escuro", "escuridão", "trancado",
    "trancada", "coroa", "inimigo", "traição", "sumisse", "perdesse", "nunca", "condenado", "amaldiçoado", "última"}
ABERTURAS_FRACAS = ["então", "entao", "bom", "bem", "olá", "ola", "oi", "e aí", "eai", "fala galera", "galera", "pessoal",
    "gente", "hoje", "basicamente", "sinceramente", "tipo", "é o seguinte", "e o seguinte", "vamos", "bora", "neste vídeo",
    "nesse vídeo", "no vídeo de hoje", "eu queria", "eu quero", "vocês sabiam", "você sabia", "sabia que", "tem um",
    "existe um", "isso é", "esse é um", "era uma vez", "um dia", "certo dia"]
IMPERATIVOS = {"pare", "para", "copia", "copie", "salva", "salve", "olha", "olhe", "veja", "repara", "faz", "faça", "faca",
    "usa", "use", "testa", "teste", "nunca", "sempre", "não", "nao", "coloca", "coloque", "manda", "comenta", "escuta",
    "presta", "lembra", "imagina", "esquece", "joga", "troca", "compra", "evita", "evite"}

ELIMINATORIOS = [
    (re.compile(r"(?i)^\s*(?:para de rolar|pare de rolar|não passa|nao passa|espera a[ií])"),
     "Começa com 'para de rolar'. Pedir atenção prova que ela ainda não foi conquistada."),
    (re.compile(r"(?i)\b(?:n[oe]ss?e v[ií]deo|no v[ií]deo de hoje|hoje eu vou (?:te )?(?:mostrar|ensinar|falar)|vou te mostrar como)\b"),
     "Introdução de vídeo. Apague e comece pela parte boa."),
    (re.compile(r"(?i)^\s*(?:oi|ol[aá]|e a[ií]|fala,? galera|bom dia|boa tarde|boa noite|seja bem.vind)"),
     "Saudação. Ninguém abriu o feed para ser cumprimentado."),
    (HASHTAG_RE, "Hashtag no gancho. Hashtag vai no fim da legenda, se for."),
    (EMOJI_RE, "Emoji no gancho. No tamanho de gancho, a tela tem espaço para palavra ou para emoji, não para os dois."),
]


def limita(n):
    return max(0.0, min(100.0, n))


def palavras(t):
    return PAL_RE.findall(re.sub(r"(?<=\d)[.,](?=\d)", "", t))


def baixa(t):
    return [p.lower().strip("'’") for p in palavras(t)]


def ch_tamanho(t):
    n = len(palavras(t)); seg = n / 2.75; c = len(t.strip())
    s = 100.0 if 5 <= n <= 12 else (limita(100 - (5 - n) * 20) if n < 5 else limita(100 - (n - 12) * 11))
    if c > 70:
        s -= 12
    return limita(s), f"{n} palavras, {c} caracteres, ~{seg:.1f}s falado (ideal: 5 a 12 palavras)"


def ch_concreto(t):
    nums = [x.strip() for x in NUM_RE.findall(t) if x.strip()]
    props = set(PROPRIO_RE.findall(t))
    fal = [p for p in baixa(t) if p in NUMEROS_FALADOS or p in DINHEIRO or p in VISUAIS]
    h = len(nums) + len(props) + len(fal)
    s = 15.0 if h == 0 else limita(45 + h * 30)
    achou = ", ".join(nums[:2] + sorted(props)[:2] + fal[:2])
    return s, f"{h} marca(s) concreta(s)" + (f": {achou}" if achou else " - sem número, sem nome, nada checável")


def ch_tensao(t):
    m = sorted(set(p for p in baixa(t) if p in TENSAO))
    if re.search(r"r\$\s?\d", t, re.I):
        m.append("um preço")
    if re.match(r"\s*e se\b", t, re.I):
        m.append("e se")
    s = {0: 20.0, 1: 70.0}.get(len(m), 100.0)
    return s, f"{len(m)} marca(s) de tensão" + (f": {', '.join(m[:4])}" if m else " - nada está em jogo nessa frase")


def ch_frente(t):
    w = palavras(t)
    if not w:
        return 0.0, "vazio"
    lw = baixa(t); ini = " ".join(lw[:3]); pen = 0; fraca = None
    for a in ABERTURAS_FRACAS:
        if ini.startswith(a):
            pen, fraca = 30, a
            break
    pos = 0 if re.match(r"\s*e se\b", t, re.I) else None
    for i, tok in enumerate(lw if pos is None else []):
        if tok in TENSAO or tok in NUMEROS_FALADOS or tok in DINHEIRO or NUM_RE.fullmatch(w[i] or "") or (i and PROPRIO_RE.match(w[i])):
            pos = i
            break
    if pos is None:
        base, onde = 30.0, "nenhuma palavra forte na frase"
    elif pos <= 3:
        base, onde = 100.0, f"palavra forte na posição {pos + 1}"
    elif pos <= 6:
        base, onde = 70.0, f"palavra forte na posição {pos + 1}, dá pra trazer pra frente"
    else:
        base, onde = 40.0, f"palavra forte na posição {pos + 1}, tarde demais"
    return limita(base - pen), onde + (f"; abertura fraca \"{fraca}\"" if fraca else "")


def ch_com_quem(t):
    lo = t.lower(); lw = baixa(t)
    if re.search(r"\b(voc[eê]|voc[eê]s|seu|sua|seus|suas|te|tu|teu|tua|c[eê])\b", lo):
        return 100.0, "fala com quem assiste"
    if lw and lw[0] in IMPERATIVOS:
        return 90.0, f"começa mandando fazer (\"{lw[0]}\")"
    if re.search(r"\b(eu|meu|minha|me|a gente|nós|nosso|nossa)\b", lo):
        return 70.0, "primeira pessoa, sem falar com quem assiste"
    return 35.0, "terceira pessoa (bom para historinha se a frase já estiver na ação)"


CHECKS = ["TAMANHO", "CONCRETO", "TENSÃO", "NA FRENTE", "COM QUEM"]


def formula(t):
    try:
        d = json.load(open(os.path.join(AQUI, "ganchos.json"), encoding="utf-8"))
    except OSError:
        return None
    por_id = {h["id"]: h for h in d["ganchos"]}
    for i in d["ordem_classificacao"]:
        h = por_id[i]
        if re.search(h["match"], t, re.I):
            return f"#{h['id']} {h['nome']}"
    return None


def avaliar(t):
    r = {"TAMANHO": ch_tamanho(t), "CONCRETO": ch_concreto(t), "TENSÃO": ch_tensao(t),
         "NA FRENTE": ch_frente(t), "COM QUEM": ch_com_quem(t)}
    flags = [m for p, m in ELIMINATORIOS if p.search(t)]
    sc = [r[c][0] for c in CHECKS]
    total = limita(statistics.mean(sc) * 0.6 + min(sc) * 0.4 - len(flags) * 15)
    veredito = "FORTE" if total >= 70 and min(sc) >= 55 and not flags else ("OK" if total >= 50 else "FRACO")
    return r, total, veredito, flags


def barra(s, w=24):
    f = round(s / 100 * w)
    return "#" * f + "." * (w - f)


def main():
    ap = argparse.ArgumentParser(description="Nota do gancho de um vídeo curto.")
    ap.add_argument("arquivo", nargs="?", default="-")
    ap.add_argument("--gancho")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.gancho:
        linhas = [a.gancho]
    else:
        bruto = sys.stdin.read() if a.arquivo == "-" else open(a.arquivo, encoding="utf-8").read()
        linhas = [l.strip() for l in bruto.splitlines() if l.strip()]
    if not linhas:
        print("nada para avaliar", file=sys.stderr); sys.exit(2)
    res = []
    for l in linhas:
        r, tot, ver, fl = avaliar(l)
        res.append({"gancho": l, "nota": round(tot, 1), "veredito": ver, "formula": formula(l),
                    "mais_fraco": min(CHECKS, key=lambda c: r[c][0]), "eliminatorios": fl,
                    "checagens": {k: {"nota": round(v[0], 1), "detalhe": v[1]} for k, v in r.items()}})
    if a.json:
        print(json.dumps(res if len(res) > 1 else res[0], ensure_ascii=False, indent=2))
    elif len(res) == 1:
        x = res[0]
        print("\nNOTA DO GANCHO\n" + "=" * 62 + f"\n  \"{x['gancho']}\"\n  fórmula: {x['formula'] or 'não identificada'}\n")
        for c in CHECKS:
            print(f"  {c:<10} {barra(x['checagens'][c]['nota'])} {x['checagens'][c]['nota']:5.1f}\n  {'':<10} {x['checagens'][c]['detalhe']}")
        print("-" * 62 + f"\n  {'NOTA':<10} {barra(x['nota'])} {x['nota']:5.1f}   {x['veredito']}")
        for f in x["eliminatorios"]:
            print(f"\n  ELIMINATÓRIO  {f}")
        if x["veredito"] != "FORTE":
            print(f"\n  Ponto mais fraco: {x['mais_fraco']}. Arrume esse e rode de novo.")
        print()
    else:
        print("\nRANKING DOS GANCHOS\n" + "=" * 78)
        for i, x in enumerate(sorted(res, key=lambda r: -r["nota"]), 1):
            g = x["gancho"] if len(x["gancho"]) <= 60 else x["gancho"][:57] + "..."
            print(f"{'->' if i == 1 else '  '} {x['nota']:5.1f} {x['veredito']:<6} {g}")
            print(f"        {x['formula'] or 'fórmula não identificada'} | mais fraco: {x['mais_fraco']} ({x['checagens'][x['mais_fraco']]['nota']:.0f})")
            for f in x["eliminatorios"]:
                print(f"        eliminatório: {f}")
        print("\nUse o primeiro. Se o primeiro ficou abaixo de 50, nenhum desses é o gancho ainda.\n")
    sys.exit(0 if max(r["nota"] for r in res) >= 70 else 1)


if __name__ == "__main__":
    main()
