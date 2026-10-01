---
title: 3D Generation Representation Datasheet v2.0
tags: [ai, 3d, mesh, nerf, gaussian-splatting, slat, cad]
updated: 2026-10-01
---

# 3D Generation Representation Datasheet v2.0

> In 3D, question #1 is not “which guidance scale?” It is **which geometric representation the model is generating**. The same prompt may end as a mesh, field, Gaussians, or structured latents — and each format follows different mathematics and failure modes.

## 1. Representation spaces

### Explicit mesh

\[
\mathcal M=(V,F)
\]

- \(V\): vertices;
- \(F\): faces/triangles.

It may carry:

- normals;
- UVs;
- material IDs;
- vertex colors;
- textures/PBR maps.

### Implicit field

A continuous function:

\[
f_\theta(\mathbf x)\rightarrow \rho,\ SDF,\ occupancy,\ radiance
\]

Geometry may be extracted as an isosurface:

\[
f(\mathbf x)=\tau
\]

### NeRF / radiance field

\[
F_\theta(\mathbf x,\mathbf d)\rightarrow(\sigma,\mathbf c)
\]

Rendering integrates density and color along rays.

### 3D Gaussian Splatting

Each primitive may be represented as:

\[
G_i=(\mu_i,\Sigma_i,\alpha_i,c_i,\ldots)
\]

where position, covariance/orientation, opacity, and appearance are explicitly parameterized.

### Structured latent / sparse voxel latent

State:

\[
Z=\{(p_i,z_i)\}_{i=1}^{N}
\]

with sparse positions/voxels + learned latent features. TRELLIS/SLAT demonstrates that a single latent can be decoded into mesh, Gaussian, or radiance representations.

---

# PART I — THE MODERN PIPELINE

## 2. Conceptual graph

\[
text/image/multiview\rightarrow condition\ encoder\rightarrow 3D\ latent/structure\rightarrow generator\rightarrow representation\ decoder\rightarrow geometry/material
\]

Shape and appearance are often separate subsystems:

\[
Shape\ Generation\neq Texture/Material\ Generation
\]

Hunyuan3D 2.1 is an explicit example: Hunyuan3D-DiT for shape and Hunyuan3D-Paint for PBR texture/material generation.

---

## 3. Conditioning

Possible inputs:

- text;
- single image;
- multiview images;
- camera poses;
- normal/depth maps;
- masks;
- existing mesh;
- partial latent.

### Single-image ambiguity

A single 2D image does not uniquely determine 3D geometry:

\[
P(Shape\mid Image)
\]

is multimodal.

The model fills unobserved surfaces from a learned prior. “Janus” and backside hallucination are consequences of this observability problem, not merely “bugs.”

---

# PART II — FLOW/DIFFUSION IN 3D

## 4. Latent flow

For structured latents:

\[
\frac{dZ_t}{dt}=v_\theta(Z_t,t,C)
\]

Integration transforms noise/prior latent into 3D structure.

TRELLIS uses rectified-flow Transformers over SLAT.

### Consequence

Parameters such as:

- steps;
- solver;
- guidance;
- seed;

may exist, but they operate in the **3D latent**, not directly on triangles.

---

# PART III — ISOSURFACE AND EXTRACTION

## 5. Isosurface threshold

This is fundamental only when the pipeline has an implicit density/SDF/occupancy field that must be converted into a surface.

\[
Surface=\{\mathbf x\mid f(\mathbf x)=\tau\}
\]

Changing \(\tau\) may:

- inflate/shrink the shape;
- open/close cavities;
- remove fine features.

### Rule

`Isosurface Threshold` is not a universal AI-3D variable. It is a **representation-extraction** parameter.

---

## 6. Marching Cubes

Converts a discretized scalar field into a triangular mesh.

Quality depends on:

- grid resolution;
- threshold;
- interpolation;
- field smoothness.

Higher grid resolution increases memory/compute approximately with volume:

\[
N_{voxels}\propto N_xN_yN_z
\]

Doubling resolution on each axis:

\[
N\rightarrow8N
\]

---

# PART IV — MESH QUALITY

## 7. Poly count

Poly count is not quality by itself.

\[
Quality\not\propto TriangleCount
\]

Millions of triangles may represent surface noise; a good remesh with fewer faces may preserve perceptual shape better.

### Evaluate

- triangle aspect ratio;
- curvature preservation;
- topology;
- normals;
- manifoldness;
- UV distortion.

---

## 8. Manifoldness and watertightness

For manufacturing, desirable properties include:

- edges with consistent incidence;
- correctly oriented normals;
- no relevant self-intersections;
- closed volume.

A renderable mesh may still be unusable for FDM/resin printing.

\[
RenderValid\not\Rightarrow ManufacturingValid
\]

---

## 9. Floating components

Disconnected components:

\[
\mathcal M=\bigcup_i\mathcal M_i
\]

Filtering by connected-component size is often useful:

\[
\mathcal M^*=\arg\max_i Volume/Area(\mathcal M_i)
\]

But do not blindly remove small components if the object intentionally contains separate parts.

---

# PART V — MATERIAL AND TEXTURE

## 10. UV texture

A 2D image mapped over the surface:

\[
(u,v)=\phi(\mathbf x_{surface})
\]

Texture resolution affects memory and appearance, but not geometry.

### PBR

Separate maps:

- base color/albedo;
- normal;
- roughness;
- metallic;
- AO;
- emissive.

### Baked lighting

Texture may contain “photographed-in” illumination:

\[
Color\approx Albedo\times Illumination
\]

For correct relighting, we want an estimate closer to intrinsic albedo/material.

---

## 11. Delighting

Conceptual objective:

\[
ObservedAppearance\rightarrow MaterialIntrinsic
\]

Reduces baked shadows/highlights before using the asset in a physically based renderer.

---

# PART VI — GAUSSIANS VS MESH

## 12. Gaussian splats

Advantages:

- efficient neural rendering;
- view synthesis;
- rich appearance.

Limitations for manufacturing:

- not directly a solid surface;
- requires conversion/reconstruction to mesh;
- “visual geometry” may not correspond to physical volume.

### Rule

\[
PhotorealisticView\not\Rightarrow AccurateGeometry
\]

---

# PART VII — SCALE AND COORDINATES

## 13. Physical units

Models may generate normalized/arbitrary coordinates.

Transform to physical units:

\[
\mathbf x_{mm}=sR\mathbf x+t
\]

Before printing:

- define millimeters;
- check bounding box;
- minimum wall thickness;
- tolerances;
- base/orientation.

---

# PART VIII — CAD VS GENERATIVE 3D

## 14. The essential boundary

Generative models primarily produce **approximate/perceptual geometry**.

Functional engineering requires:

- parametric constraints;
- exact dimensions;
- tolerances;
- geometric relationships;
- analytic surfaces;
- assemblies.

\[
GenerativeMesh\neq ParametricCAD
\]

Use AI 3D for concepts/organic shapes; rebuild or parameterize in CAD when functional requirements exist.

---

# PART IX — GUIDANCE

## 15. Guidance scale

It exists only according to the generative core.

If CFG-like guidance is used:

\[
f_g=f_u+s(f_c-f_u)
\]

Do not assume universal ranges such as `7–15`.

Artifact surfaces depend on model training, representation, solver, and decoder.

---

# PART X — SYMMETRY

## 16. Symmetry

It may be:

- conditioning;
- data prior;
- explicit geometric postprocess;
- model-specific option.

It is not a universal variable.

Explicit geometric postprocessing:

\[
V'=V\cup Mirror(V,plane)
\]

is different from “asking for symmetry” from the generative model.

---

# PART XI — COUPLING MATRIX

| Control ↑ | Geometry detail | Manifold risk | Compute | Texture quality |
|---|---:|---:|---:|---:|
| latent/grid resolution | ↑ | may ↓/↑ | ↑ sharply | ~ |
| mesh extraction resolution | ↑ | may ↑ noise | ↑ | = |
| poly count | potential ↑ | does not solve | downstream ↑ | = |
| texture resolution | = | = | ↑ | ↑ |
| guidance | adherence ↑ | non-monotonic | ↑ | may ↑ |
| decimation | detail ↓ | may simplify | downstream ↓ | UV risk |

---

# PART XII — 3D-PRINTING WORKFLOW

## 17. From latent to plastic

1. Generate shape.
2. Convert/export mesh.
3. Remove unwanted components.
4. Fix normals/self-intersections.
5. Remesh if necessary.
6. Make watertight.
7. Set physical scale.
8. Verify wall thickness.
9. Create base/orientation.
10. Run slicer manifold check.
11. Add supports and print.

For dimensionally constrained parts: rebuild in CAD before step 8.

---

# PART XIII — DIAGNOSTICS

| Symptom | Investigate |
|---|---|
| good front / invented back | single-view ambiguity |
| “spiky” mesh | latent/model/extraction threshold |
| many triangles without detail | extraction/remesh |
| slicer complains | non-manifold/self-intersection |
| render has fixed shadow | baked lighting/material |
| fragile print | wall thickness/scale, not “AI quality” |

---

## 18. Snapshot 2026

- TRELLIS/SLAT: structured sparse 3D latent decodable into radiance fields, Gaussians, and meshes; rectified-flow Transformers.
- Hunyuan3D 2.1: explicit separation of shape generation and PBR texture synthesis.
- The field no longer fits the description “NeRF/point cloud → marching cubes.”

## References

- TRELLIS / Structured 3D Latents — https://arxiv.org/abs/2412.01506
- Hunyuan3D 2.1 — https://arxiv.org/abs/2506.15442
