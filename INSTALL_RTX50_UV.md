# Installing BEHAVIOR-1K v3.9.3 on an RTX 50-series GPU with uv (no conda)

This is a fork of [StanfordVL/BEHAVIOR-1K](https://github.com/StanfordVL/BEHAVIOR-1K) at
tag `v3.9.3-post2`. The upstream installer assumes conda and, as of late October 2026, does
not finish on a fresh clone at all. This branch fixes that and documents the install that
works on an RTX 5090 in a plain Python virtual environment.

You do not need conda. You do not need a CUDA toolkit or `nvcc` (only the optional
`--primitives` extra needs one). Nothing is installed system-wide.

## Verified on

| | |
|---|---|
| OS | Ubuntu 24.04.5 |
| GPU | RTX 5090, 32 GB |
| NVIDIA driver | 580.178.04 |
| RAM | 62 GB |
| Python | 3.11.18, `uv venv` (uv 0.13.6 in `~/.local/bin`) |
| Isaac Sim | 5.1.0, Omniverse Kit 107.3.1 (installed by `setup.sh` from pypi.nvidia.com) |
| BEHAVIOR-1K | v3.9.3 / tag `v3.9.3-post2` |
| Date | 2026-10-31 |

The install was done once by hand, then repeated from a clean clone into a clean venv,
following only the steps below, to confirm this guide is complete: `setup.sh` ran through
with no manual fixes, `import omnigibson` worked, and the smoke test rendered the apartment.
The exact package versions of the first install are in
[`constraints/behavior-v3.9.3-uv-5090.txt`](constraints/behavior-v3.9.3-uv-5090.txt).

## Before you start

**Driver.** Use a 580.x driver. On this machine the 595.xx series crashed Isaac Sim 5.1 on
the RTX 5090, so don't take a driver upgrade while you need the simulator. Check with
`nvidia-smi`. RTX 50-series cards are `sm_120`, which needs CUDA 12.8 builds of PyTorch;
`setup.sh` installs those by default (`--cuda-version 12.8`).

**Disk.** The environment is about 19 GB (11 GB of that is Isaac Sim) and the datasets are
about 37 GB, so keep 60 GB free.

**uv.** If you don't have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh    # installs into ~/.local/bin
```

**Licenses.** The install accepts two agreements, which is what the `--accept-...` flags
below mean. Read them before using the flags:

- the [NVIDIA Isaac Sim EULA](https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-software-license-agreement), for Isaac Sim itself;
- the BEHAVIOR Data Bundle EULA, printed in full by `./setup.sh --omnigibson --bddl --dataset`
  when you leave the flags off. The important term: **the dataset is for non-commercial
  academic research only**, and you may only use it from within OmniGibson.

## Install

Run these one at a time and read the output of each before moving on.

**1. Clone this fork and this branch.**

```bash
git clone -b v3.9.3-uv-5090 https://github.com/felixzheng02/BEHAVIOR-1K.git
cd BEHAVIOR-1K
```

**2. Create the virtual environment.**

```bash
uv venv -p 3.11 --seed .venv
source .venv/bin/activate
```

Python must be exactly 3.11: `setup.sh` checks and stops otherwise, and the Isaac Sim
wheels are `cp311` only. `--seed` matters because `setup.sh` calls `python -m pip`, which
needs a real pip inside the venv.

**3. Add the build tools `setup.sh` expects.**

```bash
uv pip install "setuptools>=71,<81" wheel
```

OmniGibson is installed in editable mode with `--no-build-isolation`, so setuptools has to
already be in the environment. The `<81` bound is the same one upstream uses for its conda
environment.

**4. Run the installer.**

```bash
./setup.sh --omnigibson --bddl --dataset --confirm-no-conda \
           --accept-nvidia-eula --accept-dataset-tos
```

What it does, in order: PyTorch 2.7.0 for CUDA 12.8, NumPy 1.26, BDDL (editable),
OmniGibson (editable), the 26 Isaac Sim 5.1 wheels (11 GB once unpacked, downloaded with
`curl` from pypi.nvidia.com), two cleanup steps for packages Isaac Sim bundles at the wrong
version, then the three dataset downloads (about 37 GB into `datasets/`).

`--confirm-no-conda` only skips the "you are not in a conda environment" prompt; it does not
change what gets installed. Don't pass `--new-env`, which is the conda path and needs conda.

Almost all of the time is download. On this machine, at about 120 MB/s and with pip's cache
already warm, everything except the datasets took under 3 minutes; on an ordinary connection
budget an hour, plus however long 37 GB of datasets takes.

**5. Check it works.**

```bash
python scripts/smoke_test_stretch.py stretch_rgb.png
```

This loads the `Rs_int` apartment with the Stretch robot, steps the simulator 30 times and
writes a 512x512 RGB frame. A first run takes about 3 minutes, most of it compiling shaders;
once that cache is warm the same run takes about 45 seconds.

It worked if the command exits 0 and `stretch_rgb.png` shows the inside of an apartment.
Don't look for the script's own `[smoke]` lines in the terminal: OmniGibson routes Python's
stdout into the Kit log, whose path is printed near the top of the output. To read them:

```bash
grep smoke OmniGibson/appdata/local/logs/Kit/OmniGibson/3.9/kit_*.log
```

```
[smoke] robot=Robot action_dim=13
[smoke] 30 steps in 1.3s
[smoke] obs stretch/stretch:eyes:Camera:0/rgb: (512, 512, 4)
[smoke] saved rgb to stretch_rgb.png: True
[smoke] DONE
```

On a machine with no display, set `OMNIGIBSON_HEADLESS=1` (the smoke test already does) so
the simulator doesn't look for an X server.

## Messages you can ignore

- **`isaacsim-kernel 5.1.0.0 requires websockets==12.0, but you have websockets 17.4`**, at
  the end of the pip output. `setup.sh` upgrades websockets on purpose, after Isaac Sim
  downgrades it. Nothing in OmniGibson needs the old version.
- **Pillow 11.3.0 installed, while OmniGibson asks for `pillow~=11.0.0`.** Isaac Sim pulls the
  newer Pillow in after OmniGibson is installed. Image saving and loading work; leave it
  alone. Re-running `setup.sh` later reverses the pair (Pillow 11.0.0, and then
  `isaacsim-kernel` is the one complaining, along with `click` and `psutil`). Both states
  have been tested here and the simulator runs in both; don't chase these.
- **Hundreds of `DEPRECATED: get/setDofFrictionProperties` lines** while a scene loads. These
  come from Isaac Sim's physics layer.
- **`WARNING: bundled packaging copy not found, skipping packaging conflict fix: ...`** on a
  second run of `setup.sh`. The directory was already removed the first time.

## If the simulator won't start

### `Failed to create change watch ... errno=28/No space left on device`

This is not about disk space. Isaac Sim asks the kernel to watch every directory of every
extension, around 14,000 of them, and Linux caps inotify watches per user at 65,536 by
default. An editor with this repo open can hold almost all of them: on this machine Cursor
held 64,811, because the workspace contains the 19 GB `.venv` and 37 GB of `datasets`.

OmniGibson usually survives a few thousand failed watches, but one startup here aborted just
after `app ready` with:

```
terminate called after throwing an instance of 'std::system_error'
  what():  Invalid argument
```

and ran normally on the next attempt, so treat it as a resource problem rather than a broken
install. Check the limit and how much of it is in use:

```bash
cat /proc/sys/fs/inotify/max_user_watches     # the limit, 65536 by default
find /proc/*/fdinfo -type f 2>/dev/null | xargs -r grep -c '^inotify wd' 2>/dev/null |
  awk -F: '{s+=$2} END {print s+0}'          # how many are in use
```

Two ways out. Exclude the heavy directories from your editor's file watcher
(`files.watcherExclude` in VS Code or Cursor: `**/.venv/**`, `**/datasets/**`), or raise the
kernel limit, which is the one step in this guide that needs root:

```bash
sudo sysctl -w fs.inotify.max_user_watches=524288                                   # now
echo fs.inotify.max_user_watches=524288 | sudo tee /etc/sysctl.d/99-inotify.conf    # and after reboot
```

### Python segfaults at the end of a script

`og.shutdown()` was not called. Put it in a `finally` block, as the smoke test does.

### `ModuleNotFoundError: No module named 'warp'`, or a lerobot/Python version error

You are on upstream v3.9.3 rather than this branch. See the next section.

## What this fork changes

Four things in upstream v3.9.3 stop a fresh install. Each is fixed in
[`OmniGibson/setup.py`](OmniGibson/setup.py) and [`setup.sh`](setup.sh) on this branch, so
you don't have to do anything by hand. They are described here in case you hit them on
another copy of the repo, or want to send them upstream.

### 1. The lerobot dependency pointed at a branch that moved

Upstream asks for `lerobot[dataset] @ git+https://github.com/wensi-ai/lerobot@release/b1k`.
That branch was force-pushed on 2026-10-30, from commit `436812bd` to `bcbfa2e`, which is
upstream lerobot `main` and targets Isaac Sim 6: it needs Python 3.12 or newer and NumPy 2.
Since `setup.sh` requires Python 3.11, pip refuses it:

```
ERROR: Package 'lerobot' requires a different Python: 3.11.18 not in '>=3.12'
```

**Fix:** pin the commit `436812bd8ee39b768c645c248c91f1330834e687`, which is also the head of
the snapshot branch `release/b1k-challenge-2026` and still declares
`requires-python >= 3.11` and `numpy < 2`. This breaks the conda install too, not just this
one; the underlying problem is depending on a branch name instead of a commit.

### 2. `warp` was only in the `primitives` extra

`omnigibson/utils/usd_utils.py` has `import warp as wp` at the top of the file, and
`import omnigibson` reaches it through `omnigibson.controllers`. But `warp-lang==1.12.0` was
listed only under the optional `primitives` extra, so the documented core install could not
import OmniGibson at all:

```
File ".../omnigibson/utils/usd_utils.py", line 10, in <module>
    import warp as wp
ModuleNotFoundError: No module named 'warp'
```

**Fix:** move `warp-lang==1.12.0` into `install_requires`. It ships prebuilt kernels, so this
adds no CUDA toolkit requirement.

### 3. pyarrow silently installs a NumPy 2 build

`lerobot[dataset]` depends on `datasets`, which depends on pyarrow with no upper bound, so
pip installs pyarrow 26. pyarrow 22 and later declare no NumPy dependency at all, so pip has
nothing to weigh against the `numpy<2` pin this project needs, and installs a wheel built for
the NumPy 2 ABI. The result is an environment that pip considers consistent but that breaks
when pyarrow is used.

**Fix:** pin `pyarrow<22`. 21.0.0 is the last release that works with NumPy 1.26.

### 4. The Isaac Sim `packaging` cleanup only ran under conda

Isaac Sim bundles its own copy of `packaging` at a version that conflicts with the one it
requires, so `setup.sh` deletes the bundled copy. It built that path from `$CONDA_PREFIX`,
which is empty in a venv, so the step was skipped with no message at all. The workaround was
to run the installer as `CONDA_PREFIX=$VIRTUAL_ENV ./setup.sh ...`.

**Fix:** ask Python where site-packages is
(`sysconfig.get_path('purelib')`), which is correct under conda and under a venv, and print a
warning instead of skipping silently. You should see `Fixing packaging conflict...` in the
output of a first install.

### Also changed

- `--dev` installed pre-commit with `conda install`, which cannot work without conda. It now
  falls back to `pip install pre-commit`.
- `./setup.sh --help` now shows the no-conda invocation.
- Added `scripts/smoke_test_stretch.py` (step 5) and
  `constraints/behavior-v3.9.3-uv-5090.txt`.

## Reproducing the exact environment

`constraints/behavior-v3.9.3-uv-5090.txt` is `uv pip freeze` from the working install, minus
the entries pip cannot accept as constraints (the editable `bddl3` and `OmniGibson`, the
Isaac Sim wheel URLs, and the lerobot git reference — those are pinned by `setup.sh` and
`OmniGibson/setup.py` anyway). `setup.sh` does not read it. Use it to find out what changed
when a later install behaves differently:

```bash
uv pip freeze | diff constraints/behavior-v3.9.3-uv-5090.txt -
```

## What is not covered here

- **`--primitives`** (motion planning, cuRobo) is not installed. `setup.sh` requires `nvcc`
  reporting CUDA 12.8 on `PATH` before it will even start, and refuses otherwise. A per-user
  CUDA 12.8 toolkit (NVIDIA's runfile in toolkit-only mode, into something like
  `~/cuda-12.8`) is enough; never install the apt `cuda` metapackage, which will upgrade your
  driver.
- **`--joylo`, `--eval`, `--asset-pipeline`** were not tried on this setup.
- **System libraries.** Isaac Sim needs `libEGL`/`libGL`, which were already present on this
  machine. If rendering fails with a missing `libEGL.so.1` or `libGL.so.1`, install
  `libegl1 libgl1` with apt. Along with the inotify limit above, that is the only thing here
  that touches the system rather than your home directory.
- **Graphical mode.** Only headless rendering was tested.

## Writing your first script

The things that are easy to get wrong in v3.9.3, all visible in
`scripts/smoke_test_stretch.py`:

- An environment is always a **set of parallel environments**, even when there is one.
  `env.robots` is `list[list[Robot]]`, so the first robot is `env.robots[0][0]`, and `step()`
  and `reset()` return **lists** of observations, one per environment. `step()` does accept a
  flat `(action_dim,)` tensor when there is a single environment.
- Pick a robot with `"model": "stretch"`. The `"type"` key is deprecated.
- Camera resolution defaults to 64x64. Set it with
  `"sensor_config": {"VisionSensor": {"sensor_kwargs": {"image_height": 512, "image_width": 512}}}`.
- Set `OMNIGIBSON_HEADLESS=1` and `OMNI_KIT_ACCEPT_EULA=YES` before importing OmniGibson.
- Always call `og.shutdown()` in a `finally` block. If an exception skips it, Python segfaults
  on the way out and hides the real error.
- `OMNIGIBSON_DATA_PATH` overrides where the datasets are read from; it defaults to
  `datasets/` at the top of the repo. Two installs can share one copy of the data.

## Staying in sync with upstream

```bash
git remote add upstream https://github.com/StanfordVL/BEHAVIOR-1K.git
git fetch upstream --tags
```

The four fixes above are small and touch only `setup.sh` and `OmniGibson/setup.py`, so a
rebase onto a later upstream tag should be cheap. Check first whether upstream has pinned
lerobot by commit and moved `warp-lang`; if it has, drop those parts.
