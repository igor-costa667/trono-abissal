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

## Animações reais do Mixamo (25/11/2026)
- `mixamo.js`: carrega os .fbx de `animacoes/` (Y Bot, T-pose, cm) e redireciona cada osso para o esqueleto do Ren pela diferença em relação ao T-pose. `sequencia()` encadeia clipes com transição suave (mistura), quadril contínuo entre um clipe e outro e raiz andando nos clipes "In Place" na velocidade medida do pé de apoio (o pé não patina).
- `prototipo_mixamo.html`: cena de teste só com movimento capturado (chega andando, golpe no boneco de palha, o boneco volta e derruba o Ren, ele levanta, gesto de raiva, guarda). HUD só no golpe (vida aparece, perde, some). Vídeo: `testes/prototipo_3d_mixamo.mp4`.
- `teste_mixamo.html`: folha de conferência. `?f=0.5` mostra o Ren no meio das 28 animações; `?clip=Getting%20Up` mostra 28 quadros de uma animação só (bom para achar o tempo de cada fase).
- `sfx_mixamo.py`: efeitos e trilha da cena (`python3 sfx_mixamo.py <pasta scripts do kit>` dentro de `saida/`).
- Render: `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node servidor.js prototipo_mixamo.html saida/quadros 0 13.41 30` (~1 s por quadro) e depois ffmpeg com `saida/sfx.wav` + `saida/musica.wav`.

## Ren modelado em 3D (26/11/2026)
- `modelos/ren_hy.glb`: forma gerada no Hunyuan 3D a partir de `serie/referencias/3d/ren_frente.png` (só malha, sem cor).
- `modelos/ren_modelo.obj`: a mesma malha em cm, pés no chão, olhando para +Z (a versão que foi para o Mixamo).
- `ferramentas/pintar_modelo.py`: pinta o modelo projetando as 3 vistas de referência (frente, costas, lado), ignora o fundo branco e preenche o que nenhuma vista enxerga com a cor da vizinhança. Sai `modelos/ren_pintado.glb` (com UV e textura 2048) e `modelos/ren_textura.png`.
- `ferramentas/esqueleto_modelo.py`: esqueleto montado no código (o auto-rig do Mixamo recusou o modelo 3 vezes sem dizer o motivo). Juntas colocadas à mão na forma do modelo; pesos por difusão na malha a partir dos ossos, com a mochila presa ao peito. Sai `modelos/ren_esqueleto.json`.
- `personagem_modelo.js`: carrega o modelo pintado com o esqueleto (mesmo formato do Ren de peças, então serve no `mixamo.js`). `naMao()` prende a espada.
- `prototipo_modelo.html`: a cena do boneco de palha com o Ren modelado. Vídeo: `testes/prototipo_3d_modelo.mp4`. `ver_modelo.html` mostra o modelo pintado de 4 lados.
- Ainda falta: rosto com expressão (hoje o rosto é a pintura parada, sem piscar nem mudar a boca) e cabelo com mola.
