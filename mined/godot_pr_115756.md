# PR 115756 [CLOSED] — Add native USD scene import module using tinyusdz
AUTHOR: Aiacos

## BODY
## Summary

Adds a new `modules/usd` module that provides native import support for **Universal Scene Description** (.usd, .usda, .usdc, .usdz) files, using the lightweight [tinyusdz](https://github.com/syoyo/tinyusdz) library (v0.9.1, Apache 2.0 license).

This implements the long-requested USD import capability (see godotengine/godot-proposals#7744 — 60+ upvotes) following the same architecture as the existing glTF and FBX importers.

### What's included

**Scene import pipeline:**
- `EditorSceneFormatImporterUSD` — registers `.usd`, `.usda`, `.usdc`, `.usdz` extensions in Godot's 3D import pipeline
- `USDDocument` — core parser that reads USD files via tinyusdz and converts to Godot scene trees
- `USDState` — import state container holding all parsed data (nodes, meshes, materials, lights, cameras)

**Mesh import:**
- Vertices, normals, UV coordinates (st primvar), face vertex indices
- Fan triangulation for N-gon face support
- Per-vertex and face-varying attribute interpolation
- Bounds checking on vertex indices

**Material import:**
- UsdPreviewSurface → `StandardMaterial3D` conversion (diffuse, metallic, roughness, emission, opacity, IOR, clearcoat)
- Texture path resolution for all PBR channels
- **MaterialX XML** parsing and compilation to Godot spatial shaders (`USDMaterialXConverter`)
  - Supports 50+ MaterialX node types (math, geometry, color, noise, image/texture)
  - Hash-based shader cache for performance

**Light import:**
- Distant, Sphere, Disk, Rect, Dome light types
- Color, intensity, radius, width/height parameters

**Camera import:**
- Perspective and orthographic projection
- Focal length, aperture, clipping range

**Coordinate system:**
- Automatic Z-up (USD default) → Y-up (Godot) conversion
- metersPerUnit scaling (USD default: centimeters → Godot: meters)

### Thirdparty: tinyusdz

The module uses [tinyusdz](https://github.com/syoyo/tinyusdz) — a dependency-free, header-centric C++14 USD library that supports USDA (ASCII), USDC (binary Crate), and USDZ formats. This was chosen over the full OpenUSD SDK because:
- **Zero external dependencies** (no TBB, Boost, or Python required)
- **Small footprint** (~222 files, compiles in ~60 seconds)
- **Permissive license** (Apache 2.0)

Two patches were applied to tinyusdz for compatibility:
1. Added `#include <cstdint>` to `value-types.hh` (GCC 15 removed transitive `<cstdint>` includes)
2. Wrapped `texture-types.hh` definitions in `namespace tinyusdz` (avoided name collision with Godot's `Texture` class)

### What's NOT included (future work)

- Skeletal animation import (UsdSkel — stub classes are in place)
- Transform/property animation import
- Point instancing (USD's scene-level instancing)
- USD export
- Variant set support
- Layer composition (sublayers, references with composition arcs)

### Architecture

```
modules/usd/
├── config.py                    # Module build configuration
├── SCsub                        # Build script (compiles tinyusdz + module)
├── register_types.cpp/h         # Module registration
├── usd_defines.h                # Type aliases and constants
├── editor/
│   └── editor_scene_importer_usd.cpp/h   # EditorSceneFormatImporter
└── structures/
    ├── usd_document.cpp/h       # Core parser (tinyusdz integration)
    ├── usd_state.cpp/h          # Import state container
    ├── usd_mesh.cpp/h           # Mesh data → ImporterMesh
    ├── usd_material.cpp/h       # UsdPreviewSurface → StandardMaterial3D
    ├── usd_materialx_converter.cpp/h  # MaterialX → Spatial Shader
    ├── usd_light.cpp/h          # Light types
    ├── usd_camera.cpp/h         # Camera parameters
    ├── usd_node.cpp/h           # Base node data
    ├── usd_skeleton.cpp/h       # Skeleton stub
    └── usd_animation.cpp/h      # Animation stub
```

Closes godotengine/godot-proposals#7744.
Partially addresses godotengine/godot-proposals#714 (MaterialX import).

## Test plan

- [ ] Build with `scons platform=linuxbsd target=editor module_usd_enabled=yes` — verified on GCC 15.2.1
- [ ] Build with `module_usd_enabled=no` — module is optional, engine builds without it
- [ ] Import a `.usda` ASCII file containing a simple mesh
- [ ] Import a `.usdc` binary Crate file
- [ ] Import a `.usdz` package file
- [ ] Verify mesh geometry (vertices, normals, UVs) imports correctly
- [ ] Verify UsdPreviewSurface materials map to StandardMaterial3D
- [ ] Verify lights and cameras import with correct parameters
- [ ] Verify coordinate system conversion (Z-up → Y-up, cm → m)
- [ ] Test with Kitchen Set USD sample scene
- [ ] Test with MaterialX materials (verify shader compilation)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## COMMENTS
--- AThousandShips:
Thank you for your contribution, however we do not permit [fully AI generated contributions](https://contributing.godotengine.org/en/latest/pull_requests/pull_request_guidelines.html#ai-assisted-contributions)

Closing this as it violates our contribution guidelines

