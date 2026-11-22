# Motor 3D do Trono Abissal (protótipo, 22/11/2026)

Pedido do Igor: movimento fluido em 3D, como a série "Ether 2050" do @gabriel.cta. Protótipo: `testes/prototipo_3d_ren.mp4`.

- `personagem.js`: Ren em 3D estilizado (peças presas a um esqueleto, sombreamento de desenho, contorno), rosto com expressões, cabelo e mochila com balanço.
- `anim.js`: poses em graus, curvas suaves entre poses, caminhada com o pé travado no chão, molas (movimento secundário).
- `cenario.js`: céu, campo de treino de Valdenmoor, boneco de palha, luzes.
- `prototipo.html`: a cena (andar, preparar, golpe, tranco, cair sentado), câmera em 5 planos, HUD de jogo, efeitos.
- `servidor.js`: renderiza quadro a quadro no Chromium (three.js). `node servidor.js prototipo.html - 0 8.6 30 | ffmpeg ...`
- Dependências: `npm i three@0.160.0` (node_modules fora do git). Render: ~0,9 s por quadro (1 min de vídeo ≈ 27 min).

## Regras de visual (Igor, 22/11/2026)
- Tem que parecer **série animada**, não jogo. HUD limpo.
- Elementos de jogo só pontuais e rápidos, quando a história pede: levou golpe → barra de vida aparece, mostra a perda e some; subiu de nível → aviso curto; resultado de um teste → painel rápido. Nada fixo na tela (sem barra de vida/mana o tempo todo).
- Movimento: o Igor aprovou a fluidez do protótipo. Próximo passo: animações reais do Mixamo (pasta animacoes/).
