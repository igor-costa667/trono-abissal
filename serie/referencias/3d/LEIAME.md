# Ren em 3 vistas (para gerar o modelo 3D)

Feitas a partir de `../ren_fase1_viajante.png` (25/11/2026), fundo branco, mãos vazias, sem texto.

- `ren_frente.png`: frente, pose A (braços a ~45°). É a imagem principal para geradores de imagem→3D (Tripo, Meshy, Hunyuan 3D).
- `ren_lado.png` e `ren_costas.png`: para geradores que aceitam várias vistas. A vista de lado está com os braços para baixo.
- `ren_3vistas.png`: as três lado a lado, para conferência.

Depois de gerar o modelo: baixar em .glb ou .fbx, acabamento no Blender, esqueleto no Mixamo (auto-rig) e ligar no motor (`motor3d/`).
