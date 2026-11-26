// Elenco 3D: monta qualquer personagem da ficha (historia.json "elenco") no estilo de cápsulas do Ren.
// Usa o corpo de personagem.js e acrescenta o que a ficha pede: cores, barba, coroa, careca, manto, fone, tipo de corpo.
import * as THREE from 'three';
import { criarPersonagem, criarEspada, toon, DEG, PALETAS } from './personagem.js';

const CORES = {
  preto: 0x1d1d24, branco: 0xe9e6df, cinza: 0x6d6f78, vermelho: 0x9c2a2a, vinho: 0x6a1f2e, roxo: 0x5b2a86, azul: 0x2c4f8f,
  marinho: 0x1f2c4f, verde: 0x3f6b3a, oliva: 0x6f7542, marrom: 0x6b4a30, bege: 0xcdb48e, amarelo: 0xd8b13a, dourado: 0xc9a13e,
  laranja: 0xc8692a, rosa: 0xd77a9a, prata: 0xb9bec8,
};
const PELES = { clara: 0xf1c7a0, media: 0xc99872, morena: 0xa5714c, escura: 0x6e4630, negra: 0x5a3826 };
const CABELOS = { preto: 0x1b1b24, castanho: 0x4a2f1f, loiro: 0xd8b45a, ruivo: 0xa3471f, grisalho: 0x9a9aa2, branco: 0xe6e6ea, roxo: 0x4b2a70 };
const OLHOS = { castanho: 0x3a2618, azul: 0x2a5a9a, verde: 0x2f6a3a, vermelho: 0xb3261e, cinza: 0x5a5f66 };

const cor = (tab, v, padrao) => (v && tab[v] !== undefined ? tab[v] : padrao);

function paletaDe(f) {
  if (f.id === 'ren' || f.nome === 'Ren') {
    const base = (f.roupa === 'moletom' || f.fase === 'moletom') ? PALETAS.ren_moletom : PALETAS.ren_f1;
    return { ...base };
  }
  const roupa = cor(CORES, f.roupa_cor, 0x5a5a66);
  const escurecer = (c, k = 0.78) => { const o = new THREE.Color(c); o.multiplyScalar(k); return o.getHex(); };
  return {
    pele: cor(PELES, f.pele, 0xe0b48e), cabelo: cor(CABELOS, f.cabelo_cor, 0x2a2420), tunica: roupa, tunica2: escurecer(roupa),
    calca: cor(CORES, f.baixo_cor, escurecer(roupa, 0.6)), bota: 0x3a2a20, cinto: 0x3d2a1c, mochila: null, olho: cor(OLHOS, f.olhos, 0x3a2618),
  };
}

export function criarDoElenco(id, f = {}) {
  const P = paletaDe({ ...f, id });
  const nome = '_p_' + id;
  PALETAS[nome] = P;
  const per = criarPersonagem({ paleta: nome, cabeca: f.cabeca || 1.18 });
  const { B, raiz } = per;
  per.id = id;
  // tipo de corpo: largura do tronco e das pernas
  const larg = { magro: 0.92, medio: 1.0, forte: 1.16, gordo: 1.3 }[f.corpo] || 1;
  for (const k of ['spine', 'chest']) B[k].children.forEach(o => { if (o.isMesh) o.scale.x *= larg; });
  B.hips.children.forEach(o => { if (o.isMesh) o.scale.x *= larg; });
  const altura = { crianca: 0.75, baixo: 0.92, alto: 1.08 }[f.altura] || 1;
  raiz.scale.setScalar(altura);
  per.altura = altura;
  // careca: esconde o cabelo (as mechas ficam num grupo filho da cabeça)
  if (f.cabelo === 'careca') {
    B.cabelo.visible = false;
  }
  // barba
  if (f.barba) {
    const longa = f.barba === 'longa';
    const mb = toon(cor(CABELOS, f.cabelo_cor, 0x6b6b70));
    const queixo = new THREE.Mesh(new THREE.SphereGeometry(0.1, 16, 12), mb); queixo.position.set(0, 0.01, 0.1); queixo.scale.set(1.15, 0.9, 0.7); B.head.add(queixo);
    if (longa) { const bar = new THREE.Mesh(new THREE.ConeGeometry(0.1, 0.24, 12), mb); bar.position.set(0, -0.12, 0.11); bar.rotation.x = Math.PI + 0.3; bar.scale.z = 0.6; B.head.add(bar); }
    const bigode = new THREE.Mesh(new THREE.CapsuleGeometry(0.018, 0.08, 4, 8), toon(cor(CABELOS, f.cabelo_cor, 0x6b6b70)));
    bigode.rotation.z = Math.PI / 2; bigode.position.set(0, 0.05, 0.16); B.head.add(bigode);
  }
  // coroa
  if (f.acessorio === 'coroa') {
    const ouro = toon(0xd4ad3f);
    const coroa = new THREE.Group(); coroa.position.set(0, 0.33, 0.0); B.head.add(coroa);
    coroa.add(new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.12, 0.06, 20, 1, true), ouro));
    for (let i = 0; i < 8; i++) {
      const p = new THREE.Mesh(new THREE.ConeGeometry(0.025, 0.07, 6), ouro);
      const a = i / 8 * Math.PI * 2; p.position.set(Math.cos(a) * 0.125, 0.06, Math.sin(a) * 0.125); coroa.add(p);
    }
    const gema = new THREE.Mesh(new THREE.SphereGeometry(0.018, 10, 8), toon(0xb3261e)); gema.position.set(0, 0.01, 0.13); coroa.add(gema);
  }
  // fone de ouvido (Ren de moletom)
  if (f.acessorio === 'fone') {
    const m = toon(0x2a2a33);
    const arco = new THREE.Mesh(new THREE.TorusGeometry(0.19, 0.016, 8, 24, Math.PI), m); arco.position.set(0, 0.16, 0); arco.rotation.z = 0; B.head.add(arco);
    for (const l of [1, -1]) { const c = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.04, 16), m); c.rotation.z = Math.PI / 2; c.position.set(l * 0.18, 0.14, 0); B.head.add(c); }
  }
  // manto ou túnica longa: saia comprida presa ao quadril
  if (f.roupa === 'manto' || f.roupa === 'tunica' || f.roupa === 'vestido') {
    const pts = [new THREE.Vector2(0.17, 0.06), new THREE.Vector2(0.2, -0.1), new THREE.Vector2(0.25, -0.45), new THREE.Vector2(0.29, -0.8)];
    const saia = new THREE.Mesh(new THREE.LatheGeometry(pts, 26), toon(P.tunica, { side: THREE.DoubleSide }));
    saia.scale.set(larg, 1, 0.85); saia.castShadow = true; B.hips.add(saia);
    per.saiaLonga = saia;
    if (f.roupa === 'manto') {   // capa nas costas
      const capa = new THREE.Mesh(new THREE.PlaneGeometry(0.46, 1.25, 1, 6), toon(P.tunica2, { side: THREE.DoubleSide }));
      capa.position.set(0, -0.42, -0.16); B.chest.add(capa); per.capa = capa;
      const gola = new THREE.Mesh(new THREE.TorusGeometry(0.17, 0.035, 8, 24), toon(0xe9e2d0)); gola.rotation.x = Math.PI / 2; gola.position.y = 0.2; B.chest.add(gola);
    }
  }
  return per;
}

// objetos na mão (acoes.md: espada, machado, cajado, tocha, escudo)
export function criarObjeto(tipo) {
  if (!tipo || tipo === 'espada') return criarEspada();
  const g = new THREE.Group();
  const madeira = toon(0x6b4a2c), metal = toon(0xb9bec8);
  if (tipo === 'cajado') {
    const c = new THREE.Mesh(new THREE.CylinderGeometry(0.016, 0.02, 1.3, 8), madeira); c.rotation.x = Math.PI / 2; c.position.z = 0.25; g.add(c);
    const gema = new THREE.Mesh(new THREE.OctahedronGeometry(0.06), new THREE.MeshBasicMaterial({ color: 0xb48cff })); gema.position.z = 0.92; g.add(gema);
  } else if (tipo === 'machado') {
    const c = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.02, 0.8, 8), madeira); c.rotation.x = Math.PI / 2; c.position.z = 0.25; g.add(c);
    const l = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.22, 0.16), metal); l.position.set(0, 0.06, 0.58); g.add(l);
  } else if (tipo === 'tocha') {
    const c = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.025, 0.45, 8), madeira); c.rotation.x = Math.PI / 2; c.position.z = 0.1; g.add(c);
    const fogo = new THREE.Mesh(new THREE.ConeGeometry(0.06, 0.16, 10), new THREE.MeshBasicMaterial({ color: 0xffa53a })); fogo.rotation.x = Math.PI / 2; fogo.position.z = 0.4; g.add(fogo);
    const luz = new THREE.PointLight(0xffa040, 1.4, 4); luz.position.z = 0.45; g.add(luz);
  } else if (tipo === 'escudo') {
    const e = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.22, 0.04, 24), toon(0x7a5a3a)); e.rotation.z = Math.PI / 2; g.add(e);
    const b = new THREE.Mesh(new THREE.SphereGeometry(0.05, 10, 8), metal); b.position.x = 0.03; g.add(b);
  }
  return g;
}
