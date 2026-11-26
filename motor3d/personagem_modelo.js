// Ren 3D de verdade: modelo do Hunyuan 3D pintado com as referências (modelos/ren_pintado.glb)
// e esqueleto montado por ferramentas/esqueleto_modelo.py (modelos/ren_esqueleto.json).
// Devolve o mesmo formato do personagem de peças ({ raiz, B, restRen, alturaQuadril }),
// então tudo do mixamo.js (sequencia, aplicarPose) funciona igual.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { gradiente } from './personagem.js';

export async function criarRenModelo(base = 'modelos/') {
  const [gltf, esq] = await Promise.all([
    new GLTFLoader().loadAsync(base + 'ren_pintado.glb'),
    fetch(base + 'ren_esqueleto.json').then(r => r.json()),
  ]);
  let fonte = null;
  gltf.scene.traverse(o => { if (o.isMesh && !fonte) fonte = o; });
  fonte.updateMatrixWorld(true);
  const geo = fonte.geometry.clone();
  geo.applyMatrix4(fonte.matrixWorld);
  geo.computeVertexNormals();
  const n = geo.attributes.position.count;
  geo.setAttribute('skinIndex', new THREE.Uint16BufferAttribute(esq.indices, 4));
  geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(esq.pesos, 4));
  if (esq.indices.length !== n * 4) console.error('esqueleto não bate com a malha', esq.indices.length / 4, n);

  const raiz = new THREE.Group(); raiz.name = 'raiz';
  const B = {}, ossos = [], J = {};
  esq.ossos.forEach((nome, i) => { J[nome] = new THREE.Vector3(...esq.juntas[i]); });
  esq.ossos.forEach((nome, i) => {
    const b = new THREE.Bone(); b.name = nome;
    const pai = esq.pais[i];
    b.position.copy(pai ? J[nome].clone().sub(J[pai]) : J[nome]);
    (pai ? B[pai] : raiz).add(b);
    B[nome] = b; ossos.push(b);
  });
  const mapa = fonte.material.map; if (mapa) mapa.colorSpace = THREE.SRGBColorSpace;
  const mat = new THREE.MeshToonMaterial({ map: mapa, gradientMap: gradiente() });
  const malha = new THREE.SkinnedMesh(geo, mat);
  malha.castShadow = true; malha.receiveShadow = true; malha.frustumCulled = false;
  raiz.add(malha);
  raiz.updateMatrixWorld(true);
  malha.bind(new THREE.Skeleton(ossos));

  // "T-pose" deste esqueleto: o modelo está em pose A, então os braços giram até ficar na horizontal
  const restRen = {};
  for (const nome of esq.ossos) restRen[nome] = new THREE.Quaternion();
  for (const [s, x] of [['L', 1], ['R', -1]]) {
    const dirA = J['hand' + s].clone().sub(J['ua' + s]).normalize();
    const q = new THREE.Quaternion().setFromUnitVectors(dirA, new THREE.Vector3(x, 0, 0));
    for (const o of ['ua', 'fa', 'hand']) restRen[o + s] = q.clone();
  }
  // ponto da palma (para pôr a espada): 40% do caminho do pulso até a ponta da mão
  const fimMao = { L: new THREE.Vector3(0.47, 0.73, 0.09), R: new THREE.Vector3(-0.47, 0.73, 0.09) };
  const palma = {};
  for (const s of ['L', 'R']) palma[s] = fimMao[s].clone().sub(J['hand' + s]).multiplyScalar(0.4);
  return { raiz, B, malha, restRen, alturaQuadril: J.hips.y, palma, modelo3d: true };
}

// prende um objeto na mão: na T-pose ele fica com a orientação "do mundo" (espada apontando para +Z)
export function naMao(per, obj, lado = 'R') {
  const mao = per.B['hand' + lado];
  mao.add(obj);
  obj.position.copy(per.palma[lado]);
  obj.quaternion.copy(per.restRen['hand' + lado]).invert();
}
