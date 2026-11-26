# Aprendizados do canal

O que está funcionando e o que não está, episódio a episódio. A tarefa diária lê isto antes de escrever o próximo episódio e acrescenta uma entrada nova depois de olhar as métricas.

## Regras que valem agora
- Ritmo rápido (padrão do kit): corte a cada ~2 s, legenda karaokê, narrador conduzindo com frases curtas, cortes sem som.
- Primeira frase já na ação. Nada de "Era uma vez".
- Escolha A ou B com consequência das duas opções no cartão final.

- Ação na tela (Igor, 22/11): personagens não podem ficar parados enquanto o narrador conta a ação. Toda ação narrada aparece (serie/acoes.md); abertura com movimento forte nos 3 primeiros segundos.

## Histórico
- Ep. 1 (21/11/2026): 59,5 s, sem anúncio. 327 views, alcance 281, tempo médio 4,9 s (8% do vídeo), 81% pularam nos 3 primeiros segundos, 1 comentário (0,3% das views), 0 compart., 1 salvo, 4 curtidas. Vídeo de vendas (22/11, fora da série): 159 views, 4,7 s, 71% de pulo.
  - Hipótese: o gancho é o problema. "Ren tinha dezoito anos. Nenhum amigo." é apresentação, não ação; quem chega pelo feed não vê motivo para ficar. Pouquíssimos chegam ao cartão A/B, por isso só 1 voto.
  - Mudança do ep. 2: (1) primeira frase com conflito e segredo ("Ren engoliu a raiva. E ficou calado. Foi assim que ouviu o que não devia."), sem apresentação; (2) episódio mais enxuto (144 palavras, ~62 s + 7 s de anúncio). Medir amanhã: skip rate < 81% e tempo médio > 4,9 s.
  - Anúncio do curso: o ep. 1 não tinha anúncio, então ainda não dá para medir o efeito; comparar a partir do ep. 2 (com anúncio).
- Ep. 2 (22/11/2026, medido em 26/11): 69 s com anúncio. 271 views, alcance 244, tempo médio 29,1 s (42% do vídeo; ep. 1: 5,0 s), 48% pularam nos 3 s (ep. 1: 81%), 0 comentários, 0 compart., 0 salvos, 5 curtidas. Ep. 1 atualizado: 336 views, 5,0 s, 81% de pulo.
  - O gancho com conflito e segredo funcionou: o pulo caiu 33 pontos e o tempo médio ficou 6x maior. Manter: primeira frase com tensão, sem apresentação.
  - Anúncio do curso: o ep. 2 já tinha anúncio e mesmo assim reteve muito mais que o ep. 1. Por enquanto o anúncio não está derrubando retenção; alcance um pouco menor (244 x 290), mas o ep. 1 teve mais dias no ar. Seguir medindo.
  - Problema agora: 0 comentário, 0 compartilhamento. Quem assiste não vota. Hipótese: a escolha só aparecia escrita no fim e quase ninguém chega lá (29 de 69 s).
  - Mudança do ep. 3 (26/11): (1) gancho fórmula #3 "Ninguém te conta" com nota 81 ("Ninguém te conta o preço que Ren pagou."), promessa paga antes da metade; (2) pergunta direta ao público no meio do vídeo ("Você pagaria esse preço?") e o narrador lendo a pergunta e as opções A e B em voz alta no fim, com o chamado segue/compartilha. Medir amanhã: comentários > 0 e pulo nos 3 s ≤ 48%.
  - Seguidores: 16 em 26/11. Meta de 100 mil até 11/12 pede ~6.666 por dia; o ritmo real ainda não tem histórico (começa hoje).
- 26/11 (rodada das 12h, ep. 4): o ep. 3 saiu às 8h30 e ainda não aparece no Windsor (cache sem o post de hoje), então não deu para medir as mudanças do ep. 3. Ep. 1 e 2 sem mudança (336 e 271 views). Nenhum comentário no ep. 3: o destino escolheu A (Kagegakure). Seguidores: 16 (sem mudança); faltam 99.984 em 15 dias, ~6.665,6 por dia.
  - Hipótese: com dois episódios por dia, vídeo mais curto deixa mais gente chegar ao cartão A ou B (o ep. 2 reteve 42% de 69 s; o ep. 3 teve 76,6 s com anúncio).
  - Mudança do ep. 4 (só uma): episódio mais curto, 145 palavras, ~63 s de história (ep. 3: 69,9 s). Mantidos: gancho #3 "Ninguém te conta" (nota 81), narrador lendo a pergunta e as opções, chamado segue/compartilha.
  - Técnica: o Whisper do kit separou mal as falas do narrador quando duas frases seguidas terminavam com a mesma palavra ("sombras") e a pausa entre elas era curta; a fala do Kuroha caiu no lugar errado. Correção: antes do render, pôr 0,4 s de silêncio entre as falas do voz_narrador.wav (corte no silêncio mais perto do fim de cada fala) e conferir com o Whisper no timeline_audio.wav.
