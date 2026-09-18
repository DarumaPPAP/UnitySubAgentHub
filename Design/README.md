# UnitySubAgentHub design records

`Design/` contains the architecture contract and decision records for the SubAgent registry. The canonical Hub index is `Registry/subagents.yaml`; each specialist's identity and lifecycle contract is in `SubAgents/<id>/manifest.yaml`; shared shapes are in `Schemas/`.

UnityAgent remains the only Control Plane. Hub design records do not imply that a specialist is installed, eligible, or executable. Specialist-specific behavior and acceptance rules remain in the contracts linked by each manifest.

Legacy MyUnityMCP designs and control-plane proposals remain under `Legacy/MyUnityMCP-1.1.1/Design/` as migration references only. Do not change the published legacy tag.
