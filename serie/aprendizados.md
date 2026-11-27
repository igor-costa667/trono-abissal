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
- 26/11 (rodada das 12h, ep. 4): ep. 3 com 3,4 h no ar: 184 views, alcance 165, tempo médio 10,2 s (13% de 76,6 s), pulo nos 3 s 43% (ep. 2: 48%; o gancho #3 nota 81 ajudou um pouco), 1 comentário (texto ainda não aparece no Windsor), 0 compart., 0 salvos, 3 curtidas. Tempo médio bem abaixo do ep. 2 (29 s), mas o ep. 2 foi medido com 4 dias no ar; comparar de novo amanhã. Ep. 1 e 2 sem mudança (336 e 271 views). Nenhum voto legível no ep. 3 (o único comentário ainda não tem texto no Windsor): o destino escolheu A (Kagegakure). Seguidores: 16 (sem mudança); faltam 99.984 em 15 dias, ~6.665,6 por dia.
  - Hipótese: com dois episódios por dia, vídeo mais curto deixa mais gente chegar ao cartão A ou B (o ep. 2 reteve 42% de 69 s; o ep. 3 teve 76,6 s com anúncio).
  - Mudança do ep. 4 (só uma): episódio mais curto, 145 palavras, ~63 s de história (ep. 3: 69,9 s). Mantidos: gancho #3 "Ninguém te conta" (nota 81), narrador lendo a pergunta e as opções, chamado segue/compartilha.
  - Técnica: o Whisper do kit separou mal as falas do narrador quando duas frases seguidas terminavam com a mesma palavra ("sombras") e a pausa entre elas era curta; a fala do Kuroha caiu no lugar errado. Correção: antes do render, pôr 0,4 s de silêncio entre as falas do voz_narrador.wav (corte no silêncio mais perto do fim de cada fala) e conferir com o Whisper no timeline_audio.wav.

## Monitor 26/11 17h: voto perdido pelo cache
- O comentário do ep. 3 ("frostheim", voto B) foi feito às 09:42, antes da produção do ep. 4, mas o Windsor só mostrou o texto às 17h (plano sem atualização sob demanda). O ep. 4 saiu com A pelo "destino", contra a regra "se houver voto, o público decide".
- Hipótese: com o cache, a contagem de votos da rotina pode chegar horas atrasada. Sugestão ao Igor (regra não mudada): quando `media_comments_count` for maior que o número de comentários com texto na tabela, tratar como voto pendente e citar no recap; ou assinar o plano Standard do Windsor (atualização de hora em hora).

## 26/11 (rodada das 20h, ep. 5)
- Números: ep. 4 com 7,7 h no ar: 163 views, alcance 145, tempo médio 10,1 s (15% de 69,5 s), pulo nos 3 s 50% (ep. 3: 43,9%), 0 comentários, 0 compart., 0 salvos, 2 curtidas. Ep. 3: 199 views, 11,4 s, 43,9% (sem mudança, cache do Windsor). Seguidores: 16 (sem mudança no dia). Faltam 99.984 em 15 dias: 6.665,6 por dia; ritmo real: 0 por dia.
- Anúncio do curso: não é ele que derruba a retenção. Ep. 1 (sem anúncio) segurou 5,0 s; eps. 2 a 4 (com anúncio) seguraram 10 a 29 s. Quase ninguém chega aos últimos 7 s, então o anúncio quase não é visto.
- Votação do ep. 4: nenhum comentário. O destino seguiu a lore (A, recusar: ética +1, reputação em Kagegakure cai).
- Hipótese: o gancho #3 repetido cansou (pulo 43,9% → 50%) e quem sai cedo nunca descobre que vai votar.
- Mudanças do ep. 5 (os 2 ajustes do monitor): (1) gancho #18 Abre na ação, "Olha só: Ren disse não e virou inimigo." (nota 85,8); (2) "No fim, você decide o que o Ren faz." aos ~9 s. Medir: pulo nos 3 s abaixo de 50% e pelo menos 1 comentário.
- Técnica: o montar_historia juntou duas falas do narrador na cena 2 de novo (pausa de 0,4 s curta demais para o corte por silêncio). Corrigido antes do render: Whisper com marcação de palavras no voz_narrador.wav, corte no ponto mais silencioso entre a última palavra de uma fala e a primeira da seguinte, e 0,6 s de silêncio colado ali. Vale fazer sempre.
- Roteiro: o motor 3D não tem bichos (ratos, coelhos, Vorgath). A descida ao andar 1 da ficha foi adiada; o ep. 5 seguiu a consequência da recusa (expulsão e o desertor, que a lore já prevê: Kuroha é perseguido por ex-companheiros).

## Monitor 27/11 7h: ep. 5 melhor que o ep. 4
- Ep. 5 com ~11 h: 262 views (23/h; ep. 4 ~21/h), pulo nos 3 s 46,3% (ep. 4: 50,7%), 1º compartilhamento da série, 6 curtidas. Tempo médio 9,7 s, igual aos eps. 3 e 4. 0 comentários.
- Hipótese: o gancho #18 Abre na ação funciona melhor que o #3 repetido; o aviso "no fim, você decide" aos 9 s não segurou ninguém além dos 10 s.
- Ajustes para o ep. 6: manter #18; pôr uma revelação ou ameaça nova entre 8 e 12 s.

## 27/11 (rodada das 12h, ep. 6)
- Números (Windsor em cache, iguais aos das 7h): ep. 5 com ~15,7 h: 262 views, alcance 217, tempo médio 9,7 s (14% de 71,2 s), pulo nos 3 s 46,3%, 1 compart., 6 curtidas, 0 comentários. Ep. 4: 173 views, 50,7%. Ep. 3: 211 views, 44,5%. Seguidores: 16 (sem mudança desde 26/11). Faltam 99.984 em 14 dias: 7.141,7 por dia; ritmo real: 0 por dia.
- Votação do ep. 5: nenhum comentário. O destino seguiu a lore (A, ouvir o desertor; entregar à morte iria contra a ética que subiu no ep. 4).
- Hipótese: o #18 Abre na ação segura melhor nos 3 s; o que falta é motivo para passar dos 10 s.
- Mudanças do ep. 6 (os 2 ajustes do monitor): (1) gancho #18 de novo, "Olha só: Kuroha deixou a esposa morrer." (nota 85,8); (2) revelação nova aos 8,7 s, na voz do desertor: "Ela era minha irmã." Medir: tempo médio acima de 10 s e pulo nos 3 s até 46%.
- Roteiro: com o Ren e o desertor na floresta, a escolha virou treino (desertor x Frostheim). Frostheim volta como opção porque teve o único voto de vila (ep. 3).
- Técnica: o Whisper ouviu "Ren ouviu" como "ou Will" e desalinhou a contagem de palavras do corte automático; os cortes da cena 1 foram marcados à mão pelos tempos das palavras. Conferir sempre a lista de palavras antes de colar os silêncios.
- Igor reprovou a 1ª versão do ep. 6 (27/11): personagens se atacando enquanto conversavam, ações sem relação com a narração e "sumiu nas sombras e apareceu atrás do Ren" mostrado como um pulo (o motor não tem sumir/teletransportar). Refeito e republicado: cada ação mostra exatamente o que o narrador conta; nada de golpe ou feitiço em quem está só conversando; a história contada (os ninjas cercando a casa de Kuroha) virou flashback na aldeia. Lição: só narrar o que existe no pacote de ações; o que não existe (teleporte, sumir, carregar alguém) sai do roteiro.

## Monitor 27/11 15h: ep. 6 é o mais compartilhado
- Ep. 6 com ~2,6 h: 149 views (ritmo igual ao do ep. 4 na mesma idade), mas 7 compartilhamentos (eps. 1 a 5 somados: 1), pulo nos 3 s 46,9%, tempo médio 9,4 s, 1 comentário.
- Hipótese: o drama pessoal (esposa morta, "ela era minha irmã", flashback) faz as pessoas mandarem o vídeo; a retenção ainda trava em ~10 s.
- Ajuste para o ep. 7: manter gancho #18 com revelação pessoal/trágica e flashback quando houver história contada.
