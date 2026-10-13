# P7 Unity CI foundation

P9 adds Windows/Linux Editor discovery and platform entrypoints. See
[the current Japanese execution guide](../../ci/README.md). Compatibility now
records BLOCKED_NOT_RUN artifacts in its host job and skips the Editor job when
UNITY_LICENSE_READY is not true; an enabled Editor job retains strict nonzero
failure/blocked exits. The following P7 implementation record otherwise remains
historical; its 27-test count describes that stage.

This inventory prepares execution; it does not add verified Editor versions or
current render-pipeline evidence to the product support matrix. `ci/unity-matrix.yaml`
is JSON-compatible YAML and is the source of fixture selection.

The canonical full suite targets the preserved `ci/unity-projects/artist-e2e`
project on its existing exact Editor `6000.6.0f1`, with its existing package pins.
The baseline package's Editor tests lack a test asmdef. The runner exposes those
existing test sources through a generated test assembly in the disposable project
copy, retaining source hashes in evidence and leaving committed package/project
assets unchanged. If a package test asmdef exists, manifest `testables` exposes it
without copying sources. Full means all discovered EditMode tests, not connected
transport or visual acceptance.
The minimal `versions/6000.6` fixture imports the Artist package and checks its
version/pipeline rejection boundary. No unsupported 2022.3 fixture is made current.
The Unity 6.3 minimal fixture pins `6000.3.12f1` / `fca03ac9b0d5`, grounded in
Unity-Technologies/Graphics commit `2d2e78cc9d6254bc6e7c9c5552cea053508e86cb`,
`Templates/com.unity.template-hd/ProjectSettings/ProjectVersion.txt` on the
`6000.3/staging` branch. The source is linked in matrix provenance. This fixture
only imports the Artist package (declared Unity minimum 6000.0) and existing test
framework pin. It excludes the canonical experimental Pipeline dependency, whose
availability on 6.3 has not been observed. No 6.3 transport/support observation is
inferred from this prepared minimal fixture.

Built-in, URP and HDRP each have a committed nonempty scene, stable fixture GUIDs,
an Editor test assembly, scene-content assertions and native settings tests.
Scenes are copied from the existing canonical reference camera/mesh/light fixture.
Built-in checks fog settings; URP configures an asset with renderer data and Bloom;
HDRP configures an asset, linear color space and native Fog.meanFreePath. These are
scene/API and actual camera readback smoke tests. The render test uses a concrete
unlit geometry material, a 128x128 RenderTexture, native SRP StandardRequest (or
Built-in Camera.Render), ReadPixels and a spatial-variation assertion. It retains
`pipeline-smoke.png` and measured device/version/pixel variation in
`graphics-device.json`; PASS requires both artifacts and non-Null device metadata.
These tests do not establish artistic quality, full Artist lifecycle acceptance or
connected CLI/Pipeline transport. Their actual rendering remains unobserved here.
The fixtures require their first real import/compile run, including validation of
SRP asset initialization on the selected exact package version.

The source manifest retains existing `com.unity.test-framework: 1.3.9` and
`com.unity.pipeline: 0.6.0-exp.1` pins. New fixtures reference Artist at
`file:../../../../../Packages/com.darumappap.artist-subagent` from their Packages
folder. Structural validation expects the parent migration to preserve that package
and the preserved canonical project; it reports the missing canonical path before integration.

No exact SRP package pin exists in the baseline repository. Access to the official
registry was blocked by the cloud proxy (HTTP 403), so no resolved package version
is claimed here. At runtime, the pipeline fixture resolver queries
`https://packages.unity.com/<package>` and chooses the highest stable `17.x.y`
whose published `unity` minimum is the **exact requested Editor stream**, with
`unityRelease` no newer than that Editor patch. It rejects missing metadata,
prerelease packages, other streams and unsupported patch constraints. Selection
metadata, the concrete requested manifest and the Editor-generated package lock
are uploaded. This policy is conservative and does not establish compatibility
until import and the nonempty test suite pass. Follow-up evidence may pin a
successfully observed exact package; registry changes are always visible in each run.

The canary queries the official Unity Editor archive API, paginates releases,
selects the numerically newest Unity 6 prerelease in a stream newer than the
canonical stream, and requires a Linux x86_64 TAR_XZ from a Unity download host.
It records the exact version, changeset and download URL. It runs scheduled/manual
with `continue-on-error`; it is not a required product support check. This follows
the upstream loop's separation of full/minimal/canary jobs but implements our own
three pipeline fixtures and evidence gate.

## Runner setup and replay

All workflows default to `ubuntu-latest`, producing `BLOCKED_NOT_RUN` for missing
licensed Editor prerequisites. Provision an already licensed runner, set repository
variable `UNITY_CI_RUNNER` to a JSON runner-label array, and set `UNITY_EDITOR_ROOT`
to the directory containing `<exact-version>/Editor/Unity`. Alternatively set
`UNITY_EDITOR` to a direct executable; its `-version` output must match exactly.
Set `UNITY_LICENSE_READY=true` only after licensing the runner. No license tokens,
serial numbers, email/password activation or activation logs enter this pipeline.
Pipeline smoke additionally requires `UNITY_GRAPHICS_READY=true`, a working display
server (for example a prestarted Xvfb DISPLAY), supported graphics drivers and a
real hardware or supported software graphics device. Its command omits
`-nographics`; minimal/full import tests retain that flag. The variable authorizes
an attempt only: the test measures SystemInfo.graphicsDeviceType, fails with a
machine-readable unavailable marker for Null devices, and the runner normalizes
that outcome to BLOCKED_NOT_RUN. Native SRP asset/resource or shader problems on a
present device remain observed test failures, not successful smoke evidence.
For canary, `UNITY_ALLOW_EDITOR_DOWNLOAD=true` allows direct official Editor
extraction when that version is unavailable; no GameCI image is required. The
runner must have Linux Editor dependencies, disk space and a valid license capable
of running the directly downloaded Editor. The downloader rejects archive path
traversal with Python 3.12's `data` extraction filter.

Run from the repository root after the parent layout migration:

```sh
python ci/verify/validate_unity_fixtures.py
python -m unittest discover -s ci/verify -p 'test_unity_ci.py' -v
python ci/verify/unity_ci.py --fixture canonical-full --output /tmp/unity-canonical
python ci/verify/unity_ci.py --fixture minimal-6000.3 --output /tmp/unity-minimal-63
python ci/verify/unity_ci.py --fixture minimal-6000.6 --output /tmp/unity-minimal
python ci/verify/unity_ci.py --fixture builtin-smoke --output /tmp/unity-builtin
python ci/verify/unity_ci.py --fixture urp-smoke --output /tmp/unity-urp
python ci/verify/unity_ci.py --fixture hdrp-smoke --output /tmp/unity-hdrp
python ci/verify/unity_ci.py --fixture minimal-6000.6 --canary --output /tmp/unity-canary
```

The compatibility workflow always creates its host job on every PR and detects
related changes inside that job. Unrelated changes get a `NOT_APPLICABLE` Editor
summary; this is not observed Editor PASS. Pipeline smoke is scheduled/manual.
Only the stable host foundation job is suitable as an unconditional required check;
Editor checks require a provisioned runner. Canary stays nonblocking.

Replay preflight is read-only. It rejects output directories inside, equal to, or
above any configured fixture or local package before creating directories or
removing old artifact files. Fixture/package/output roots and hashed files cannot
be symlinks or escape the repository. The runner allocates a uniquely named owned
temporary project under the accepted output directory; it cleans only that
allocation. An unrelated preexisting `output/project` is preserved even on blocked
runs. The disposable project copies only Assets, ProjectSettings, manifest and
package lock; source caches and unrelated project-root content are excluded.
Invalid or overlapping paths exit with a diagnostic before producing artifacts,
because writing evidence to a rejected path would itself mutate protected input.

Evidence includes deterministic SHA-256 input inventories and aggregate digest
before and after execution. The inventory uses repository-relative paths and
covers the matrix, fixture Assets/ProjectSettings/manifest/lock, and local package
source/assets/meta/JSON. Generated cache directories are excluded. Commit identity
comes from a validated GITHUB_SHA or measured git HEAD. Source changes, deletion,
or symlinks introduced during execution revoke PASS and produce an explicit FAIL
with the before/after inventories. Existing output hashes remain separately
recorded as artifact hashes. Host regressions prove source/scene/meta/JSON changes
alter the digest, caches do not, unsafe roots reject before writes, an unowned
project survives blocked/successful replay, and mid-run input mutation rejects an
otherwise passing synthetic host test run.

Every Editor execution emits evidence with run ID/attempt, requested/observed
version, exact packages, status, reason and artifact hashes. Separate Editor stdout/stderr streams, Editor log and test results
are uploaded even on failure; blocked runs retain labeled stream diagnostics; blocked runs have a diagnostic log and
`observation: not_observed`. Exit codes are 0=observed PASS, 1=observed failure,
2=blocked. PASS requires a matching exact Editor, successful process, nonempty
Editor log, resolved package lock, and a passing NUnit test-run whose total/passed
counts equal all actual test cases. Zero, skipped, failed, inconclusive and stale
results cannot become PASS. Version/import smoke does not upgrade historical
visual/transport evidence into current evidence.

## Validation performed in cloud

The 27 host resolver/evidence/fixture tests pass. Fake-Editor state transitions
use synthetic artifacts strictly as host test data; they are not Editor observations. The workflows parse as YAML. The local
blocked runner path produces requested version/packages, a diagnostic log, run ID
and `BLOCKED_NOT_RUN` evidence. Unity Editor/license, actual SRP package resolution,
all Editor suites, native SRP resource initialization and visual rendering remain
**BLOCKED_NOT_RUN / not_observed**. Required next observation is a licensed runner
execution of each fixture, retaining the uploaded concrete package locks and logs.
