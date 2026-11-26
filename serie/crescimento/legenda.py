#!/usr/bin/env python3
"""legenda.py - confere a legenda do post antes de publicar e mostra o que aparece antes do "... mais".

Checagens: primeira linha (o que o feed mostra), tamanho, hashtags, link morto na legenda,
quantos pedidos (CTA), emojis, palavras de busca e aviso de publicidade em afiliado.

Adaptado do caption.py do Instagram Agent Skill (Jake Schincariol, MIT). Ver CREDITOS.md.

Uso
  python legenda.py legenda.txt
  python legenda.py legenda.txt --busca "receita fit,marmita congelada"
  python legenda.py legenda.txt --plataforma tiktok
  python legenda.py legenda.txt --afiliado
  python legenda.py titulo.txt --plataforma youtube      # confere o título do Shorts
"""
import argparse, re, sys

EMOJI = re.compile(r"[\U0001F300-\U0001FAFF☀-➿]")
HASHTAG = re.compile(r"#[\wÀ-ÿ]+")
LINK = re.compile(r"https?://|www\.|\.com\b|\.com\.br\b", re.I)
PEDIDOS = re.compile(r"\b(?:comenta|comente|salva|salve|segue|siga|compartilha|compartilhe|manda (?:pra|para)|envia (?:pra|para)|link na bio|clica|clique|marca (?:um|uma|quem|algu[eé]m)|vota)\b", re.I)
GENERICAS = {"#viral", "#fyp", "#foryou", "#foryoupage", "#explore", "#explorepage", "#paravoce", "#paravocê", "#reels",
             "#reelsinstagram", "#tiktok", "#trend", "#trending", "#instagood", "#viralvideo", "#viralreels"}
SAUDACAO = re.compile(r"(?i)^\s*(?:oi|ol[aá]|e a[ií]|bom dia|boa tarde|boa noite|fala,? galera)\b")
PUBLI = re.compile(r"(?i)#publi\b|#publicidade\b|link de afiliado|#ad\b|parceria paga|#afiliado\b")
LIMITES = {"instagram": (2200, 125), "tiktok": (2200, 100), "youtube": (100, 60)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivo")
    ap.add_argument("--busca", default="", help="termos que o público digita na busca, separados por vírgula")
    ap.add_argument("--plataforma", default="instagram", choices=list(LIMITES))
    ap.add_argument("--afiliado", action="store_true", help="post com link de afiliado ou produto de marca")
    a = ap.parse_args()
    txt = open(a.arquivo, encoding="utf-8").read().strip()
    lim, visivel = LIMITES[a.plataforma]
    res = []  # (nivel, msg)

    def r(n, m):
        res.append((n, m))

    primeira = txt.splitlines()[0] if txt else ""
    corte = txt.replace("\n", " ")[:visivel]
    if a.plataforma == "youtube":
        if len(txt) > lim:
            r("FALHA", f"Título com {len(txt)} caracteres. O YouTube aceita até {lim}.")
        elif len(txt) > visivel:
            r("ATENÇÃO", f"Título com {len(txt)} caracteres. No celular aparecem ~{visivel}; o gancho tem que estar no começo.")
    else:
        if len(txt) > lim:
            r("FALHA", f"{len(txt)} caracteres. O limite é {lim}.")
        if len(primeira) > visivel:
            r("ATENÇÃO", f"Primeira linha com {len(primeira)} caracteres; o feed corta em ~{visivel}. Termine a ideia antes do corte.")
    if primeira[:1] and (EMOJI.match(primeira[:2]) or primeira.startswith("#")):
        r("FALHA", "Começa com emoji ou hashtag. A primeira coisa tem que ser palavra.")
    if SAUDACAO.search(primeira):
        r("FALHA", "Começa com saudação. Comece pelo gancho ou pelo pedido.")
    tags = HASHTAG.findall(txt)
    gen = [t for t in tags if t.lower() in GENERICAS]
    if len(tags) > 5:
        r("FALHA", f"{len(tags)} hashtags. Use até 5, específicas do nicho (hashtag hoje é etiqueta, não alcance).")
    if gen:
        r("ATENÇÃO", "Hashtags que não dizem nada: " + " ".join(gen) + ". Troque por hashtags do nicho.")
    if LINK.search(txt) and a.plataforma != "youtube":
        r("FALHA", "Link na legenda. No Instagram e no TikTok link na legenda não é clicável: use 'link na bio' ou mande por DM.")
    peds = [m.group(0).lower() for m in PEDIDOS.finditer(txt)]
    tipos = sorted(set(p.split()[0] for p in peds))
    if len(tipos) > 2:
        r("FALHA", f"{len(tipos)} pedidos diferentes ({', '.join(tipos)}). Um pedido só (no máximo dois, como 'comenta A ou B' + 'segue pra parte 2').")
    elif len(tipos) == 2:
        r("ATENÇÃO", f"Dois pedidos ({', '.join(tipos)}). Funciona em série com escolha; nos outros, fique com um.")
    elif not tipos and a.plataforma != "youtube":
        r("ATENÇÃO", "Nenhum pedido. Diga o que a pessoa deve fazer: salvar, comentar, seguir ou link na bio.")
    n_emo = len(EMOJI.findall(txt))
    if txt and n_emo / max(len(txt), 1) * 100 > 4:
        r("ATENÇÃO", f"{n_emo} emojis: mais de 4 a cada 100 caracteres. Emoji é pontuação, não enfeite.")
    for termo in [t.strip() for t in a.busca.split(",") if t.strip()]:
        if termo.lower() in txt.lower():
            pos = txt.lower().splitlines()
            linha = next((i + 1 for i, l in enumerate(pos) if termo.lower() in l), "?")
            r("OK", f"busca \"{termo}\" aparece na linha {linha}")
        else:
            r("ATENÇÃO", f"O termo de busca \"{termo}\" não aparece no texto. Coloque numa frase normal (a busca do Instagram lê a legenda).")
    if a.afiliado and not PUBLI.search(txt):
        r("FALHA", "Post de afiliado sem aviso de publicidade. Acrescente #publi ou 'link de afiliado'.")

    print("\nO QUE APARECE ANTES DO \"... mais\"" if a.plataforma != "youtube" else "\nTÍTULO DO SHORTS")
    print("┌" + "─" * 66 + "┐")
    for i in range(0, len(corte), 64):
        print("│ " + corte[i:i + 64].ljust(64) + " │")
    print("└" + "─" * 66 + "┘")
    print(f"{len(txt)} caracteres · {len(tags)} hashtag(s) · {len(tipos)} tipo(s) de pedido · {n_emo} emoji(s)\n")
    falhas = [m for n, m in res if n == "FALHA"]
    for n, m in res:
        print(f"  {n:<8} {m}")
    print("\n" + ("PRONTA" if not falhas else f"ARRUMAR ({len(falhas)} falha(s))") + "\n")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
