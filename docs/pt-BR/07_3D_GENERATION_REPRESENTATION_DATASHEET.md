---
title: 3D Generation Representation Datasheet v2.0
tags: [ai, 3d, mesh, nerf, gaussian-splatting, slat, cad]
updated: 2026-10-01
---

# 3D Generation Representation Datasheet v2.0

> Em 3D, a pergunta nº 1 não é “qual guidance scale?”. É **qual representação geométrica o modelo está gerando**. O mesmo prompt pode terminar em mesh, field, Gaussians ou structured latents — e cada formato obedece a matemática e failure modes diferentes.

## 1. Espaços de representação

### Mesh explícita

\[
\mathcal M=(V,F)
\]

- \(V\): vértices;
- \(F\): faces/triângulos.

Pode carregar:

- normals;
- UVs;
- material IDs;
- vertex colors;
- textures/PBR maps.

### Implicit field

Uma função contínua:

\[
f_\theta(\mathbf x)\rightarrow \rho,\ SDF,\ occupancy,\ radiance
\]

Geometria pode ser extraída por isosurface:

\[
f(\mathbf x)=\tau
\]

### NeRF / radiance field

\[
F_\theta(\mathbf x,\mathbf d)\rightarrow(\sigma,\mathbf c)
\]

Renderização integra densidade e cor ao longo de rays.

### 3D Gaussian Splatting

Cada primitiva pode ser representada por:

\[
G_i=(\mu_i,\Sigma_i,\alpha_i,c_i,\ldots)
\]

onde posição, covariância/orientação, opacidade e aparência são explicitamente parametrizadas.

### Structured latent / sparse voxel latent

Estado:

\[
Z=\{(p_i,z_i)\}_{i=1}^{N}
\]

com posições/voxels esparsos + features latentes aprendidas. TRELLIS/SLAT demonstra que um mesmo latent pode ser decodificado em mesh, Gaussian ou radiance representation.

---

# PARTE I — A PIPELINE MODERNA

## 2. Grafo conceitual

\[
text/image/multiview\rightarrow condition\ encoder\rightarrow 3D\ latent/structure\rightarrow generator\rightarrow representation\ decoder\rightarrow geometry/material
\]

Frequentemente shape e appearance são subsistemas separados:

\[
Shape\ Generation\neq Texture/Material\ Generation
\]

Hunyuan3D 2.1 é exemplo explícito: Hunyuan3D-DiT para shape e Hunyuan3D-Paint para textura/material PBR.

---

## 3. Conditioning

Entradas possíveis:

- text;
- single image;
- multiview images;
- camera poses;
- normal/depth maps;
- masks;
- existing mesh;
- partial latent.

### Single-image ambiguity

Uma imagem 2D não determina unicamente geometria 3D:

\[
P(Shape\mid Image)
\]

é multimodal.

O modelo preenche superfícies não observadas com prior aprendido. “Janus” e back-side hallucination são consequências desse problema de observabilidade, não apenas “bugs”.

---

# PARTE II — FLOW/DIFFUSION EM 3D

## 4. Latent flow

Em structured latents:

\[
\frac{dZ_t}{dt}=v_\theta(Z_t,t,C)
\]

Integração transforma noise/prior latent em estrutura 3D.

TRELLIS usa rectified-flow Transformers sobre SLAT.

### Consequência

Parâmetros como:

- steps;
- solver;
- guidance;
- seed;

podem existir, mas operam no **latent 3D**, não diretamente em triângulos.

---

# PARTE III — ISOSURFACE E EXTRAÇÃO

## 5. Isosurface threshold

Só é fundamental quando o pipeline possui implicit density/SDF/occupancy a ser convertido em surface.

\[
Surface=\{\mathbf x\mid f(\mathbf x)=\tau\}
\]

Alterar \(\tau\) pode:

- inflar/encolher a forma;
- abrir/fechar cavidades;
- remover features finas.

### Regra

`Isosurface Threshold` não é variável universal de AI-3D. É um parâmetro de **representation extraction**.

---

## 6. Marching Cubes

Converte campo escalar discretizado em mesh triangulada.

Qualidade depende de:

- grid resolution;
- threshold;
- interpolation;
- field smoothness.

Mais grid resolution aumenta memória/compute aproximadamente com volume:

\[
N_{voxels}\propto N_xN_yN_z
\]

Dobrar resolução em cada eixo:

\[
N\rightarrow8N
\]

---

# PARTE IV — MESH QUALITY

## 7. Poly count

Não é qualidade por si só.

\[
Quality\not\propto TriangleCount
\]

Milhões de triângulos podem representar ruído superficial; uma remesh boa com menos faces pode preservar melhor forma perceptual.

### Avaliar

- aspect ratio de triângulos;
- curvature preservation;
- topology;
- normals;
- manifoldness;
- UV distortion.

---

## 8. Manifold e watertightness

Para fabricação, desejável:

- arestas com incidência consistente;
- normals orientadas;
- ausência de self-intersections relevantes;
- volume fechado.

Uma mesh renderizável pode ser impraticável para FDM/resina.

\[
RenderValid\not\Rightarrow ManufacturingValid
\]

---

## 9. Floating components

Componentes desconectados:

\[
\mathcal M=\bigcup_i\mathcal M_i
\]

Filtrar por connected-component size costuma ser etapa útil:

\[
\mathcal M^*=\arg\max_i Volume/Area(\mathcal M_i)
\]

Mas não remover cegamente componentes pequenos se o objeto tiver peças deliberadamente separadas.

---

# PARTE V — MATERIAL E TEXTURA

## 10. UV texture

Imagem 2D mapeada sobre a superfície:

\[
(u,v)=\phi(\mathbf x_{surface})
\]

Resolução de textura afeta memória e aparência, mas não geometria.

### PBR

Separar mapas:

- base color/albedo;
- normal;
- roughness;
- metallic;
- AO;
- emissive.

### Baked lighting

Textura pode conter iluminação “fotografada”:

\[
Color\approx Albedo\times Illumination
\]

Para relighting correto queremos estimar mais próximo de albedo/material intrínseco.

---

## 11. Delighting

Objetivo conceitual:

\[
ObservedAppearance\rightarrow MaterialIntrinsic
\]

Reduz sombras/highlights baked antes de usar o asset em renderer físico.

---

# PARTE VI — GAUSSIANS VS MESH

## 12. Gaussian splats

Vantagens:

- renderização neural eficiente;
- view synthesis;
- aparência rica.

Limitações para fabricação:

- não é superfície sólida diretamente;
- precisa conversão/reconstruction para mesh;
- “geometria visual” pode não corresponder a volume físico.

### Regra

\[
PhotorealisticView\not\Rightarrow AccurateGeometry
\]

---

# PARTE VII — SCALE E COORDINATES

## 13. Unidade física

Modelos podem gerar coordenadas normalizadas/arbitrárias.

Transformação para unidade física:

\[
\mathbf x_{mm}=sR\mathbf x+t
\]

Antes de impressão:

- definir mm;
- checar bounding box;
- espessura mínima;
- tolerâncias;
- base/orientação.

---

# PARTE VIII — CAD VS GENERATIVE 3D

## 14. O limite essencial

Modelos generativos produzem principalmente **geometria aproximada/perceptual**.

Engenharia funcional exige:

- constraints paramétricos;
- dimensões exatas;
- tolerâncias;
- relações geométricas;
- superfícies analíticas;
- assemblies.

\[
GenerativeMesh\neq ParametricCAD
\]

Usar AI 3D para concept/organic shape; reconstruir ou parametrizar em CAD quando houver requisito funcional.

---

# PARTE IX — GUIDANCE

## 15. Guidance scale

Só existe conforme o generative core.

Se houver CFG-like:

\[
f_g=f_u+s(f_c-f_u)
\]

Não assumir ranges universais como `7–15`.

Artifact surface depende de model training, representation, solver e decoder.

---

# PARTE X — SYMMETRY

## 16. Symmetry

Pode ser:

- conditioning;
- data prior;
- explicit geometric postprocess;
- model-specific option.

Não é variável universal.

Pós-processo geométrico explícito:

\[
V'=V\cup Mirror(V,plane)
\]

é diferente de “pedir simetria” ao generative model.

---

# PARTE XI — COUPLING MATRIX

| Controle ↑ | Geometry detail | Manifold risk | Compute | Texture quality |
|---|---:|---:|---:|---:|
| latent/grid resolution | ↑ | pode ↓/↑ | ↑ forte | ~ |
| mesh extraction resolution | ↑ | pode ↑ ruído | ↑ | = |
| poly count | potencial ↑ | não resolve | downstream ↑ | = |
| texture resolution | = | = | ↑ | ↑ |
| guidance | adherence ↑ | não monotônico | ↑ | pode ↑ |
| decimation | detalhe ↓ | pode simplificar | downstream ↓ | UV risk |

---

# PARTE XII — WORKFLOW PARA IMPRESSÃO 3D

## 17. Do latent ao plástico

1. Gerar shape.
2. Converter/exportar mesh.
3. Remover componentes indesejados.
4. Corrigir normals/self-intersections.
5. Remesh se necessário.
6. Tornar watertight.
7. Definir escala física.
8. Verificar wall thickness.
9. Criar base/orientação.
10. Slicer manifold check.
11. Suportes e impressão.

Para peças dimensionais: reconstruir no CAD antes do passo 8.

---

# PARTE XIII — DIAGNÓSTICO

| Sintoma | Investigar |
|---|---|
| frente boa / costas inventadas | single-view ambiguity |
| mesh “espinhosa” | latent/model/extraction threshold |
| muitos triângulos sem detalhe | extraction/remesh |
| slicer reclama | non-manifold/self-intersection |
| render com sombra fixa | baked lighting/material |
| impressão frágil | wall thickness/scale, não “AI quality” |

---

## 18. Snapshot 2026

- TRELLIS/SLAT: structured sparse 3D latent decodificável para radiance fields, Gaussians e meshes; rectified-flow Transformers.
- Hunyuan3D 2.1: separação shape generation e PBR texture synthesis.
- Campo já não cabe na descrição “NeRF/point cloud → marching cubes”.

## Referências

- TRELLIS / Structured 3D Latents — https://arxiv.org/abs/2412.01506
- Hunyuan3D 2.1 — https://arxiv.org/abs/2506.15442
