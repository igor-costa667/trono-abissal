# Pacote de ações (serie/acoes.py)

Pedido do Igor (22/11/2026): os personagens ficavam parados enquanto o narrador contava a ação. Agora **toda ação narrada precisa aparecer na tela**. O pacote amplia o modo historinha do kit Viral Sem Aparecer.

## Como usar na rotina
1. `KIT=$(bash serie/preparar_kit.sh)`: copia o kit para `/home/claude/kit_trono` e liga o pacote de ações.
2. Renderize com `python $KIT/produzir_historia.py historia.json vozes saida vertical` (no lugar do kit original).
3. Se o `preparar_kit.sh` ou o render falhar com "acoes.py: o kit mudou", renderize com o kit original (sem ações), publique normalmente e avise o Igor que o pacote de ações precisa ser atualizado.

Bônus: com o pacote, as `etiqueta` das falas aparecem de verdade (o kit original as descartava sem avisar).

## No historia.json
Na fala, o campo `acao` (um objeto ou uma lista):

```json
{"quem": "narrador", "txt": "Força: zero. Pontaria: zero.",
 "acao": [{"id": "ren", "tipo": "erra", "palavra": "Força"}, {"id": "ren", "tipo": "ofegante", "palavra": "fôlego"}]}
```

- `id`: quem faz a ação (padrão: quem fala; se o narrador fala, o protagonista).
- `palavra`: a ação começa quando o narrador diz essa palavra (sincronizado pelo Whisper). Ou `em`: segundos depois do início da fala.
- `dur`: duração em segundos (opcional).
- `alvo`: id de quem recebe o golpe ou o feitiço. O alvo reage sozinho (`atingido`, ou `"reacao": "queda"`) e é empurrado para longe de quem atacou.
- `cor` (feitiço, faísca, aura): roxo, azul, dourado, vermelho, verde, branco, gelo.
- `arma` (golpe, erra): espada (padrão), machado, cajado, tocha.
- `camera: false` não deixa a câmera ir para a ação.
- `dist` (investida): quanto anda, em fração da largura da tela (padrão 0.18). Depois da investida o personagem fica onde chegou.

| tipo | o que aparece |
| --- | --- |
| `golpe` | prepara, golpeia com a arma, rastro branco, avança; com `alvo`: estrela de impacto, linhas de anime, tremida |
| `erra` | golpe que passa do ponto: desequilibra e cai sentado, poeira (bom para humor) |
| `feitico` | braço à frente, energia carregando na mão, projétil voando até o `alvo` (ou para a frente), explosão |
| `faisca` | faísca pequena na ponta dos dedos com anel de mana (câmera fecha na mão) |
| `pulo` | pulo com poeira na saída e na chegada |
| `investida` | corrida rápida para a frente com linhas de velocidade |
| `atingido` | pisca branco, é empurrado e inclina |
| `queda` | é derrubado para trás, poeira |
| `ofegante` | curvado, mãos na cintura, gotas de suor |
| `aura` | brilho colorido pulsando em volta do corpo e partículas subindo (arma abissal: `"cor": "roxo"`) |
| `impacto` | linhas de anime em volta do personagem, flash e tremida (para frases de efeito) |

No personagem da cena: `"segura": "espada"` (ou machado, cajado, tocha, escudo) deixa o objeto na mão durante a cena toda; `"aura": "roxo"` deixa a aura ligada.

## Regras de roteiro (ação)
- **Coerência (Igor, 27/11/2026):** a ação mostra exatamente o que a frase diz, na mesma hora. Quem está só conversando não ataca nem é atacado. Frase sem nada físico: `impacto`, `aura` ou nada.
- Só narre o que esta tabela tem. Sumir, teletransporte, voar, carregar alguém e bichos não existem no motor: reescreva a frase.
- História do passado contada por alguém vira cena de flashback com os personagens dela (ex.: ep. 6, os ninjas cercando a casa de Kuroha na `aldeia`). Criança: `"altura": "crianca"` no elenco.
- Os 3 primeiros segundos precisam ter movimento forte (investida, golpe, feitiço, queda, impacto). Nada de personagem parado na abertura.
- Pelo menos uma ação a cada ~5 s. Se o narrador conta algo físico, o personagem faz.
- Separe os personagens na cena (x 0.15 / 0.45 / 0.85) para que golpes e quedas não fiquem atrás de outro personagem.
- Teste antes do render completo: renderize 3 ou 4 quadros das ações com `motor_video.py still` (veja o passo 6 do CLAUDE.md).
