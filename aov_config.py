# ============================================================
#  aov_config.py  —  AOV Manager · Shared Configuration Core
#
#  Edit this file to update both the standalone app and the
#  Houdini shelf tool simultaneously.
#
#  PASS FORMAT — each pass is a dict:
#    id          → internal identifier used in filenames/folders
#    label       → display name shown in the UI
#    desc        → short description shown in the UI
#    default_on  → bool, whether enabled by default
#    mantra      → Houdini Mantra ROP parameters (see below)
#    karma       → Houdini Karma XPU/CPU parameters (see below)
#    ue5         → Unreal Engine 5 MRQ settings (see below)
#
#  MANTRA KEYS:
#    vm_variable  → VEX export variable to sample (e.g. "Cf", "N")
#    vm_channel   → AOV output channel name
#    vm_vextype   → "vector" | "float" | "int" | "vector4"
#    vm_pfilter   → "gaussian" | "box" | "minmax median" | "minmax min"
#    vm_quantize  → "float16" | "float32" | "uint8"
#    extra        → dict of additional ROP parms {parm_name: value}
#    custom_var   → True = CUSTOM shader export, flagged in generated output
#
#  KARMA KEYS:
#    lpe          → Light Path Expression (leave "" if shader variable export)
#    variable     → shader export variable name (leave "" if LPE-based)
#    type         → "color" | "float" | "vector" | "int"
#    light_group  → light group name for LPE (leave "" = generic, no group)
#                   Once you name light groups, set e.g. "rim", "key", "fill"
#    custom_var   → True = CUSTOM shader export, flagged in generated output
#
#  UE5 KEYS:
#    pass_class    → Unreal MRQ C++ pass class name
#    deferred_only → True if only works in Deferred Rendering mode
#    notes         → setup notes displayed in the export config
#
# ── Naming tokens ────────────────────────────────────────────
# {project}  → project name field
# {layer}    → layer name field
# {pass}     → pass id
# {version}  → zero-padded version (001, 002 …)
# {date}     → YYYY_MM_DD
# {frame}    → $F4 in Houdini, {frame_number} in UE5
# ============================================================

import os
import datetime

# ── Pipeline targets ─────────────────────────────────────────
PIPELINES = ["Houdini / Mantra", "Houdini / Karma", "Unreal Engine 5"]

# ── Output format ────────────────────────────────────────────
OUTPUT_FORMAT    = "EXR"
OUTPUT_BITDEPTH  = "16"
FILM_COLORSPACE  = "ACES_ACEScg"
STYL_COLORSPACE  = "sRGB"

# ── Default project values ───────────────────────────────────
DEFAULT_PROJECT  = "MY_PROJECT"
DEFAULT_LAYER    = "hero_layer"
DEFAULT_VERSION  = 1
DEFAULT_ROOT     = "/renders"
DEFAULT_PRESET   = "ocean"
DEFAULT_PIPELINE = 0

# ============================================================
#  STANDARD PASSES — present in all presets
# ============================================================
STANDARD_PASSES = [
    {
        "id": "beauty", "label": "Beauty", "default_on": True,
        "desc": "Full composite beauty render",
        "mantra": {
            "vm_variable": "Cf+Af", "vm_channel": "beauty",
            "vm_vextype": "vector4", "vm_pfilter": "gaussian",
            "vm_quantize": "float16", "extra": {}, "custom_var": False,
        },
        "karma": {
            "lpe": "C.*", "variable": "", "type": "color",
            "light_group": "", "custom_var": False,
        },
        "ue5": {
            "pass_class": "MoviePipelineDeferredPassBase",
            "deferred_only": False,
            "notes": "Main beauty output. Always enable.",
        },
    },
    {
        "id": "diffuse", "label": "Diffuse", "default_on": True,
        "desc": "Diffuse color contribution",
        "mantra": {
            "vm_variable": "diffuse", "vm_channel": "diffuse",
            "vm_vextype": "vector", "vm_pfilter": "gaussian",
            "vm_quantize": "float16", "extra": {}, "custom_var": False,
        },
        "karma": {
            "lpe": "C<RD>.*", "variable": "", "type": "color",
            "light_group": "", "custom_var": False,
        },
        "ue5": {
            "pass_class": "MoviePipelineImagePassBase",
            "deferred_only": True,
            "notes": "Enable DiffuseColor in Buffer Visualization. Requires Deferred Rendering.",
        },
    },
    {
        "id": "spec", "label": "Specular", "default_on": False,
        "desc": "Specular highlight layer",
        "mantra": {
            "vm_variable": "specular", "vm_channel": "specular",
            "vm_vextype": "vector", "vm_pfilter": "gaussian",
            "vm_quantize": "float16", "extra": {}, "custom_var": False,
        },
        "karma": {
            "lpe": "C<RS>.*", "variable": "", "type": "color",
            "light_group": "", "custom_var": False,
        },
        "ue5": {
            "pass_class": "MoviePipelineImagePassBase",
            "deferred_only": True,
            "notes": "Enable SpecularColor in Buffer Visualization.",
        },
    },
    {
        "id": "sss", "label": "SSS", "default_on": False,
        "desc": "Subsurface scattering pass",
        "mantra": {
            "vm_variable": "sss", "vm_channel": "sss",
            "vm_vextype": "vector", "vm_pfilter": "gaussian",
            "vm_quantize": "float16",
            "extra": {"vm_useshading": 1}, "custom_var": False,
        },
        "karma": {
            "lpe": "C<TD>.*", "variable": "", "type": "color",
            "light_group": "", "custom_var": False,
        },
        "ue5": {
            "pass_class": "MoviePipelineImagePassBase",
            "deferred_only": True,
            "notes": "Enable SubsurfaceColor in Buffer Visualization.",
        },
    },
    {
        "id": "zdepth", "label": "Z-Depth", "default_on": True,
        "desc": "Depth buffer for DOF / fog",
        "mantra": {
            "vm_variable": "Pz", "vm_channel": "zdepth",
            "vm_vextype": "float", "vm_pfilter": "minmax min",
            "vm_quantize": "float32", "extra": {}, "custom_var": False,
        },
        "karma": {
            "lpe": "", "variable": "z", "type": "float",
            "light_group": "", "custom_var": False,
        },
        "ue5": {
            "pass_class": "MoviePipelineImagePassBase",
            "deferred_only": True,
            "notes": "Enable SceneDepth in Buffer Visualization.",
        },
    },
    {
        "id": "id", "label": "ID / Mask", "default_on": False,
        "desc": "Cryptomatte / object ID mask",
        "mantra": {
            "vm_variable": "Op", "vm_channel": "id",
            "vm_vextype": "float", "vm_pfilter": "box",
            "vm_quantize": "float32",
            "extra": {"vm_cryptolayers": 6}, "custom_var": False,
        },
        "karma": {
            "lpe": "", "variable": "cryptomatte", "type": "float",
            "light_group": "", "custom_var": False,
        },
        "ue5": {
            "pass_class": "MoviePipelineObjectIdRenderPass",
            "deferred_only": False,
            "notes": "Built-in Object ID pass. No extra setup required.",
        },
    },
    {
        "id": "emission", "label": "Emission", "default_on": False,
        "desc": "Self-illumination pass",
        "mantra": {
            "vm_variable": "Ce", "vm_channel": "emission",
            "vm_vextype": "vector", "vm_pfilter": "gaussian",
            "vm_quantize": "float16", "extra": {}, "custom_var": False,
        },
        "karma": {
            "lpe": "C[ES].*", "variable": "", "type": "color",
            "light_group": "", "custom_var": False,
        },
        "ue5": {
            "pass_class": "MoviePipelineImagePassBase",
            "deferred_only": True,
            "notes": "Enable Emissive in Buffer Visualization.",
        },
    },
    {
        "id": "normal", "label": "World Normal", "default_on": False,
        "desc": "Surface normal vector pass",
        "mantra": {
            "vm_variable": "N", "vm_channel": "normal",
            "vm_vextype": "vector", "vm_pfilter": "gaussian",
            "vm_quantize": "float16", "extra": {}, "custom_var": False,
        },
        "karma": {
            "lpe": "", "variable": "N", "type": "vector",
            "light_group": "", "custom_var": False,
        },
        "ue5": {
            "pass_class": "MoviePipelineImagePassBase",
            "deferred_only": True,
            "notes": "Enable WorldNormal in Buffer Visualization.",
        },
    },
    {
        "id": "ao", "label": "Ambient Occ.", "default_on": False,
        "desc": "Ambient occlusion pass",
        "mantra": {
            "vm_variable": "occlusion", "vm_channel": "ao",
            "vm_vextype": "float", "vm_pfilter": "gaussian",
            "vm_quantize": "float16",
            "extra": {"vm_occlusionsamples": 16}, "custom_var": False,
        },
        "karma": {
            "lpe": "C<AO>", "variable": "", "type": "float",
            "light_group": "", "custom_var": False,
        },
        "ue5": {
            "pass_class": "MoviePipelineImagePassBase",
            "deferred_only": True,
            "notes": "Enable AmbientOcclusion in Buffer Visualization. Requires SSAO in post process.",
        },
    },
    {
        "id": "shadow", "label": "Shadow Matte", "default_on": False,
        "desc": "Shadow catcher / matte isolation",
        "mantra": {
            "vm_variable": "shadow", "vm_channel": "shadow",
            "vm_vextype": "float", "vm_pfilter": "gaussian",
            "vm_quantize": "float16",
            "extra": {"vm_shadowtype": 1}, "custom_var": False,
        },
        "karma": {
            "lpe": "C.*<L.>", "variable": "", "type": "float",
            "light_group": "", "custom_var": False,
        },
        "ue5": {
            "pass_class": "MoviePipelineImagePassBase",
            "deferred_only": True,
            "notes": "Enable ShadowMask in Buffer Visualization.",
        },
    },
]

# ============================================================
#  STYLE PRESETS
# ============================================================
PRESETS = {

    "ocean": {
        "label": "🌊 Ocean Mode",
        "color_hex": "#00d4ff",
        "naming_template": "{project}_{layer}_ocean_{pass}_v{version}",
        "folder_template": "{root}/{project}/ocean/{layer}/{pass}/",
        "passes": [
            {
                "id": "caustics", "label": "Caustics Pass", "default_on": True,
                "desc": "Underwater light refraction caustics",
                "mantra": {
                    # CUSTOM: your shader must export a variable named 'caustics'
                    # vm_usecaustics=1 enables caustics sampling on the Mantra ROP
                    "vm_variable": "caustics", "vm_channel": "caustics",
                    "vm_vextype": "vector", "vm_pfilter": "minmax median",
                    "vm_quantize": "float16",
                    "extra": {"vm_usecaustics": 1}, "custom_var": True,
                },
                "karma": {
                    # Transmitted diffuse LPE approximates caustic light paths
                    "lpe": "C<TD>.*", "variable": "", "type": "color",
                    "light_group": "", "custom_var": False,
                },
                "ue5": {
                    "pass_class": "MoviePipelineImagePassBase",
                    "deferred_only": True,
                    "notes": "No native caustics pass in UE5 MRQ. Use a CustomDepthStencil mask on caustics decal actors.",
                },
            },
            {
                "id": "fog_vol", "label": "Fog Volume", "default_on": True,
                "desc": "Volumetric underwater haze",
                "mantra": {
                    "vm_variable": "volume", "vm_channel": "fog_vol",
                    "vm_vextype": "vector", "vm_pfilter": "gaussian",
                    "vm_quantize": "float16",
                    "extra": {"vm_volumesteprate": 1.0}, "custom_var": False,
                },
                "karma": {
                    "lpe": "CV.*", "variable": "", "type": "color",
                    "light_group": "", "custom_var": False,
                },
                "ue5": {
                    "pass_class": "MoviePipelineImagePassBase",
                    "deferred_only": True,
                    "notes": "Enable VolumetricFog in Buffer Visualization. Requires Volumetric Fog in Post Process Volume.",
                },
            },
            {
                "id": "emission2", "label": "Biolum Emission", "default_on": True,
                "desc": "Bioluminescence isolation AOV",
                "mantra": {
                    # CUSTOM: your bioluminescence shader must export 'biolum'
                    # Replace with your actual VEX export variable name
                    "vm_variable": "biolum", "vm_channel": "biolum_emission",
                    "vm_vextype": "vector", "vm_pfilter": "gaussian",
                    "vm_quantize": "float16", "extra": {}, "custom_var": True,
                },
                "karma": {
                    # Self-emission LPE captures emissive surface contribution
                    "lpe": "C[ES].*", "variable": "", "type": "color",
                    "light_group": "", "custom_var": False,
                },
                "ue5": {
                    "pass_class": "MoviePipelineImagePassBase",
                    "deferred_only": True,
                    "notes": "Enable Emissive in Buffer Visualization. Separate biolum actors onto a stencil layer.",
                },
            },
            {
                "id": "scatter", "label": "Scatter Volume", "default_on": True,
                "desc": "Particle / plankton scatter",
                "mantra": {
                    "vm_variable": "scatter", "vm_channel": "scatter",
                    "vm_vextype": "vector", "vm_pfilter": "gaussian",
                    "vm_quantize": "float16",
                    "extra": {"vm_volumesteprate": 0.5}, "custom_var": False,
                },
                "karma": {
                    "lpe": "CV<RS>.*", "variable": "", "type": "color",
                    "light_group": "", "custom_var": False,
                },
                "ue5": {
                    "pass_class": "MoviePipelineImagePassBase",
                    "deferred_only": True,
                    "notes": "Use a separate Niagara particle layer with CustomDepthStencil for clean scatter isolation.",
                },
            },
        ],
    },

    "scifi": {
        "label": "🌌 Sci-Fi Mode",
        "color_hex": "#bf5fff",
        "naming_template": "{project}_{layer}_scifi_{pass}_v{version}",
        "folder_template": "{root}/{project}/scifi/{layer}/{pass}/",
        "passes": [
            {
                "id": "glow_mask", "label": "Glow Mask", "default_on": True,
                "desc": "Bloom / glow isolation channel",
                "mantra": {
                    # Ce = emissive contribution in Mantra
                    "vm_variable": "Ce", "vm_channel": "glow_mask",
                    "vm_vextype": "vector", "vm_pfilter": "gaussian",
                    "vm_quantize": "float16", "extra": {}, "custom_var": False,
                },
                "karma": {
                    "lpe": "C[ES].*", "variable": "", "type": "color",
                    "light_group": "", "custom_var": False,
                },
                "ue5": {
                    "pass_class": "MoviePipelineImagePassBase",
                    "deferred_only": True,
                    "notes": "Enable Emissive in Buffer Visualization. Drive bloom from this pass in comp.",
                },
            },
            {
                "id": "rimlight", "label": "Rim Light Pass", "default_on": True,
                "desc": "Edge / backlight separation",
                "mantra": {
                    # CUSTOM: requires a 'rimlight' export in your shader
                    # or rename vm_variable to match your light export variable
                    "vm_variable": "rimlight", "vm_channel": "rimlight",
                    "vm_vextype": "vector", "vm_pfilter": "gaussian",
                    "vm_quantize": "float16", "extra": {}, "custom_var": True,
                },
                "karma": {
                    # Generic: all reflected specular — set light_group once named
                    # e.g. set light_group to "rim" when you create a rim light group
                    "lpe": "C<RS>.*", "variable": "", "type": "color",
                    "light_group": "", "custom_var": False,
                },
                "ue5": {
                    "pass_class": "MoviePipelineImagePassBase",
                    "deferred_only": True,
                    "notes": "Isolate rim lights onto Light Channel 1. Render a separate pass with only Channel 1 active.",
                },
            },
            {
                "id": "grad_mask", "label": "Gradient Mask", "default_on": True,
                "desc": "Vertical gradient matte",
                "mantra": {
                    # CUSTOM: float export driven by world-space Y position in shader
                    "vm_variable": "grad_mask", "vm_channel": "grad_mask",
                    "vm_vextype": "float", "vm_pfilter": "gaussian",
                    "vm_quantize": "float16", "extra": {}, "custom_var": True,
                },
                "karma": {
                    "lpe": "", "variable": "grad_mask", "type": "float",
                    "light_group": "", "custom_var": True,
                },
                "ue5": {
                    "pass_class": "MoviePipelineImagePassBase",
                    "deferred_only": True,
                    "notes": "Generate from WorldPosition AOV in comp, or use a CustomDepthStencil gradient material.",
                },
            },
            {
                "id": "holo", "label": "Hologram Pass", "default_on": True,
                "desc": "Scan-line / holographic overlay",
                "mantra": {
                    # CUSTOM: requires a 'holo' export in your hologram shader
                    "vm_variable": "holo", "vm_channel": "holo",
                    "vm_vextype": "vector", "vm_pfilter": "box",
                    "vm_quantize": "float16", "extra": {}, "custom_var": True,
                },
                "karma": {
                    "lpe": "", "variable": "holo", "type": "color",
                    "light_group": "", "custom_var": True,
                },
                "ue5": {
                    "pass_class": "MoviePipelineObjectIdRenderPass",
                    "deferred_only": False,
                    "notes": "Assign hologram actors a unique stencil value. Isolate by stencil in comp from the ObjectID pass.",
                },
            },
        ],
    },

    "painterly": {
        "label": "🎨 Painterly Mode",
        "color_hex": "#ffb347",
        "naming_template": "{project}_{layer}_paint_{pass}_v{version}",
        "folder_template": "{root}/{project}/painterly/{layer}/{pass}/",
        "passes": [
            {
                "id": "toon_ramp", "label": "Toon Ramp Pass", "default_on": True,
                "desc": "Stylized stepped shading gradient",
                "mantra": {
                    # CUSTOM: your toon shader must export a float variable 'toon_ramp'
                    # This should be a 0-1 diffuse ramp value from your material
                    "vm_variable": "toon_ramp", "vm_channel": "toon_ramp",
                    "vm_vextype": "float", "vm_pfilter": "box",
                    "vm_quantize": "float16", "extra": {}, "custom_var": True,
                },
                "karma": {
                    "lpe": "", "variable": "toon_ramp", "type": "float",
                    "light_group": "", "custom_var": True,
                },
                "ue5": {
                    "pass_class": "MoviePipelineImagePassBase",
                    "deferred_only": False,
                    "notes": "Requires a custom post-process material outputting toon ramp to SceneCapture or CustomDepth buffer.",
                },
            },
            {
                "id": "linework", "label": "Linework Pass", "default_on": True,
                "desc": "Edge detection / outline isolation",
                "mantra": {
                    # Uses N (normal) discontinuity — vm_edgesamples controls quality
                    "vm_variable": "N", "vm_channel": "linework",
                    "vm_vextype": "float", "vm_pfilter": "box",
                    "vm_quantize": "float16",
                    "extra": {"vm_edgesamples": 4}, "custom_var": False,
                },
                "karma": {
                    "lpe": "", "variable": "N", "type": "vector",
                    "light_group": "", "custom_var": False,
                },
                "ue5": {
                    "pass_class": "MoviePipelineImagePassBase",
                    "deferred_only": True,
                    "notes": "Use WorldNormal pass + edge detect in comp, or a Toon Outline post-process material.",
                },
            },
            {
                "id": "shad_iso", "label": "Shadow Isolation", "default_on": True,
                "desc": "Shadow matte for painterly comp",
                "mantra": {
                    "vm_variable": "shadow", "vm_channel": "shad_iso",
                    "vm_vextype": "float", "vm_pfilter": "gaussian",
                    "vm_quantize": "float16",
                    "extra": {"vm_shadowtype": 1}, "custom_var": False,
                },
                "karma": {
                    "lpe": "C.*<L.>", "variable": "", "type": "float",
                    "light_group": "", "custom_var": False,
                },
                "ue5": {
                    "pass_class": "MoviePipelineImagePassBase",
                    "deferred_only": True,
                    "notes": "Enable ShadowMask in Buffer Visualization.",
                },
            },
            {
                "id": "color_id", "label": "Color ID Flat", "default_on": True,
                "desc": "Flat color region matte",
                "mantra": {
                    # Op = object identifier — flat per-object colour
                    "vm_variable": "Op", "vm_channel": "color_id",
                    "vm_vextype": "vector", "vm_pfilter": "box",
                    "vm_quantize": "float16", "extra": {}, "custom_var": False,
                },
                "karma": {
                    "lpe": "", "variable": "cryptomatte", "type": "float",
                    "light_group": "", "custom_var": False,
                },
                "ue5": {
                    "pass_class": "MoviePipelineObjectIdRenderPass",
                    "deferred_only": False,
                    "notes": "Built-in ObjectID pass. Set each actor's custom primitive data for unique flat colours.",
                },
            },
        ],
    },
}

# ============================================================
#  UTILITY
# ============================================================

def get_pass_data(pass_id, preset_key=None):
    for p in STANDARD_PASSES:
        if p["id"] == pass_id:
            return p
    if preset_key and preset_key in PRESETS:
        for p in PRESETS[preset_key]["passes"]:
            if p["id"] == pass_id:
                return p
    return None


def build_active_passes(preset_key, standard_states, custom_states):
    active = []
    for p in STANDARD_PASSES:
        if standard_states.get(p["id"], False):
            active.append(p)
    for p in PRESETS[preset_key]["passes"]:
        if custom_states.get(p["id"], True):
            active.append(p)
    return active


def resolve_name(template, project, layer, pass_id, version, pipeline_idx=0):
    frame_token = "$F4" if pipeline_idx < 2 else "{frame_number}"
    return (template
        .replace("{project}", project)
        .replace("{layer}",   layer)
        .replace("{pass}",    pass_id)
        .replace("{version}", str(version).zfill(3))
        .replace("{date}",    datetime.date.today().strftime("%Y_%m_%d"))
        .replace("{frame}",   frame_token))


def resolve_folder(template, root, project, layer, pass_id):
    return (template
        .replace("{root}",    root.rstrip("/"))
        .replace("{project}", project)
        .replace("{layer}",   layer)
        .replace("{pass}",    pass_id))


# ============================================================
#  GENERATOR — Houdini Mantra AOV block
# ============================================================

def _gen_mantra_aov(p, folder, filename):
    m   = p["mantra"]
    pid = p["id"]
    lbl = p["label"]
    full_path = "{}/{}.$F4.exr".format(folder, filename)
    lines = ["", "# ── {} ──────────────────────────────────".format(lbl)]
    if m["custom_var"]:
        lines.append(
            "# ⚠ CUSTOM SHADER EXPORT: vm_variable='{}' — "
            "replace with your actual VEX export name if different".format(m["vm_variable"])
        )
    lines += [
        "aov_{0} = rop.createNode('aov')".format(pid),
        "aov_{0}.parm('vm_variable').set('{1}')".format(pid, m["vm_variable"]),
        "aov_{0}.parm('vm_channel').set('{1}')".format(pid, m["vm_channel"]),
        "aov_{0}.parm('vm_vextype').set('{1}')".format(pid, m["vm_vextype"]),
        "aov_{0}.parm('vm_pfilter').set('{1}')".format(pid, m["vm_pfilter"]),
        "aov_{0}.parm('vm_quantize').set('{1}')".format(pid, m["vm_quantize"]),
        "aov_{0}.parm('vm_filename').set(r'{1}')".format(pid, full_path),
    ]
    for parm, val in m["extra"].items():
        if isinstance(val, str):
            lines.append("aov_{0}.parm('{1}').set('{2}')".format(pid, parm, val))
        else:
            lines.append("aov_{0}.parm('{1}').set({2})".format(pid, parm, val))
    return lines


# ============================================================
#  GENERATOR — Houdini Karma AOV block
# ============================================================

def _gen_karma_aov(p, folder, filename):
    k   = p["karma"]
    pid = p["id"]
    lbl = p["label"]
    full_path = "{}/{}.$F4.exr".format(folder, filename)
    lines = ["", "# ── {} ──────────────────────────────────".format(lbl)]
    if k["custom_var"]:
        lines.append(
            "# ⚠ CUSTOM SHADER EXPORT: variable='{}' — "
            "replace with your actual export name if different".format(k["variable"])
        )
    if k["lpe"]:
        lpe = k["lpe"]
        if k["light_group"]:
            lpe = lpe.replace(".*", "<'{}'>.".format(k["light_group"]))
        else:
            lines.append(
                "# NOTE: Generic LPE — no light group set. "
                "Set light_group in aov_config.py to isolate a specific light."
            )
        lines += [
            "# LPE: {}".format(lpe),
            "aov_{0} = rop.createNode('karmasettings')".format(pid),
            "aov_{0}.parm('ri_aov_{0}_lpe').set('{1}')".format(pid, lpe),
            "aov_{0}.parm('ri_aov_{0}_type').set('{1}')".format(pid, k["type"]),
            "aov_{0}.parm('ri_aov_{0}_name').set('{0}')".format(pid),
            "aov_{0}.parm('ri_aov_{0}_file').set(r'{1}')".format(pid, full_path),
        ]
    else:
        lines += [
            "# Shader variable export: {}".format(k["variable"]),
            "aov_{0} = rop.createNode('karmasettings')".format(pid),
            "aov_{0}.parm('ri_aov_{0}_variable').set('{1}')".format(pid, k["variable"]),
            "aov_{0}.parm('ri_aov_{0}_type').set('{1}')".format(pid, k["type"]),
            "aov_{0}.parm('ri_aov_{0}_name').set('{0}')".format(pid),
            "aov_{0}.parm('ri_aov_{0}_file').set(r'{1}')".format(pid, full_path),
        ]
    return lines


# ============================================================
#  GENERATOR — Full Houdini script
# ============================================================

def generate_houdini_script(pipeline_idx, preset_key, project, layer,
                             version, root, film_mode,
                             standard_states, custom_states):
    renderer   = "mantra" if pipeline_idx == 0 else "karma"
    preset     = PRESETS[preset_key]
    naming     = preset["naming_template"]
    folder_t   = preset["folder_template"]
    active     = build_active_passes(preset_key, standard_states, custom_states)
    colorspace = FILM_COLORSPACE if film_mode else STYL_COLORSPACE

    lines = [
        "# ══ AOV Manager — Houdini {} ══════════════════════════".format(renderer.capitalize()),
        "# Project   : {}".format(project),
        "# Layer     : {}".format(layer),
        "# Preset    : {}".format(preset["label"]),
        "# Version   : v{}".format(str(version).zfill(3)),
        "# Colorspace: {}".format(colorspace),
        "# Passes    : {}".format(len(active)),
        "# Generated : {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")),
        "# ══════════════════════════════════════════════════════",
        "",
        "import hou, os",
        "",
        "# ── Create / replace ROP ─────────────────────────────",
        "out = hou.node('/out')",
        "existing = out.node('{0}_{1}_rop')".format(layer, renderer),
        "if existing: existing.destroy()",
        "rop = out.createNode('{}')".format(renderer),
        "rop.setName('{0}_{1}_rop')".format(layer, renderer),
        "",
        "# ── Beauty output ────────────────────────────────────",
    ]

    beauty_folder = resolve_folder(folder_t, root, project, layer, "beauty")
    beauty_name   = resolve_name(naming, project, layer, "beauty", version, pipeline_idx)

    if renderer == "mantra":
        lines += [
            "rop.parm('vm_picture').set(r'{}/{}.$F4.exr')".format(beauty_folder, beauty_name),
            "rop.parm('vm_colorspace').set('{}')".format(colorspace),
            "rop.parm('vm_numthreads').set(-1)  # use all CPU threads",
        ]
    else:
        lines += [
            "rop.parm('picture').set(r'{}/{}.$F4.exr')".format(beauty_folder, beauty_name),
            "# ↑ Karma: also set colorspace in your Karma Render Settings node → {}".format(colorspace),
        ]

    lines += ["", "# ── AOV Passes ───────────────────────────────────────"]

    for p in active:
        folder   = resolve_folder(folder_t, root, project, layer, p["id"])
        filename = resolve_name(naming, project, layer, p["id"], version, pipeline_idx)
        if renderer == "mantra":
            lines += _gen_mantra_aov(p, folder, filename)
        else:
            lines += _gen_karma_aov(p, folder, filename)

    lines += [
        "",
        "# ── Create output directories ────────────────────────",
    ]
    for p in active:
        folder = resolve_folder(folder_t, root, project, layer, p["id"])
        lines.append("os.makedirs(r'{}', exist_ok=True)".format(folder))

    lines += [
        "",
        "print('AOV Manager: {} ROP built — {} passes active.')".format(
            renderer.capitalize(), len(active)),
    ]
    return "\n".join(lines)


# ============================================================
#  GENERATOR — UE5 Movie Render Queue
# ============================================================

def generate_ue5_config(preset_key, project, layer, version,
                        root, film_mode, standard_states, custom_states):
    preset     = PRESETS[preset_key]
    naming     = preset["naming_template"]
    folder_t   = preset["folder_template"]
    active     = build_active_passes(preset_key, standard_states, custom_states)
    colorspace = FILM_COLORSPACE if film_mode else STYL_COLORSPACE
    out_dir    = resolve_folder(folder_t, root, project, layer, "{pass_name}")

    lines = [
        "; ══ AOV Manager — UE5 Movie Render Queue ═════════════",
        "; Project   : {}".format(project),
        "; Layer     : {}".format(layer),
        "; Preset    : {}".format(preset["label"]),
        "; Version   : v{}".format(str(version).zfill(3)),
        "; Colorspace: {}".format(colorspace),
        "; Passes    : {}".format(len(active)),
        "; Generated : {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")),
        "; ══════════════════════════════════════════════════════",
        "",
        "[MoviePipelineConfig]",
        "OutputDirectory={}".format(out_dir),
        "FileNameFormat={}".format(
            resolve_name(naming, project, layer, "{pass_name}", version, 2)),
        "OutputFormat={}_{}bit".format(OUTPUT_FORMAT, OUTPUT_BITDEPTH),
        "ColorSpace={}".format(colorspace),
        "",
        "[RenderPasses]",
        "; Format: PassID=True  |  MRQ Class  |  Rendering mode requirement",
    ]

    deferred_needed = False
    for p in active:
        u = p["ue5"]
        if u["deferred_only"]:
            deferred_needed = True
        lines.append("{:<42} ; {}  |  {}".format(
            "EnablePass_{}=True".format(p["id"].upper()),
            u["pass_class"],
            "⚠ Deferred only" if u["deferred_only"] else "✓ Any mode",
        ))

    lines += ["", "[PassSetupNotes]",
              "; Read these before rendering — some passes need manual UE5 setup:"]
    for p in active:
        u = p["ue5"]
        if u["notes"]:
            lines.append("; {:<14} {}".format(p["id"].upper() + ":", u["notes"]))

    lines += ["", "[PostProcess]",
              "FilmMode={}".format(str(film_mode).lower()),
              "StylePreset={}".format(preset_key.upper())]

    if deferred_needed:
        lines += [
            "",
            "; ⚠ DEFERRED RENDERING REQUIRED for some passes above.",
            "; In MRQ: Add a 'Deferred Rendering' setting block.",
            "; Ensure r.DeferredShading=1 and r.AllowStaticLighting=1 in your ini.",
        ]

    lines += ["", "; ── Output folders ──────────────────────────────────"]
    for p in active:
        folder = resolve_folder(folder_t, root, project, layer, p["id"])
        lines.append("; {:<16} {}".format(p["label"] + ":", folder))

    lines.append("; ══════════════════════════════════════════════════════")
    return "\n".join(lines)