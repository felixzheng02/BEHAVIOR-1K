<h1 align="center">BEHAVIOR-1K</h1>

![BEHAVIOR-1K](./docs/assets/readme_splash_logo.png)

**BEHAVIOR-1K** is a comprehensive simulation benchmark for testing embodied AI agents on 1,000 everyday household activities. This monolithic repository provides everything needed to train and evaluate agents on human-centered tasks like cleaning, cooking, and organizing — activities selected from real human time-use surveys and preference studies.

***Check out our [main website](https://behavior.stanford.edu/) for more details!***

# 🛠️ Installation

BEHAVIOR-1K provides an installation script that handles all dependencies and components. The script supports modular installation, allowing you to install only the components you need.

Please check out [Installation Guide](https://behavior.stanford.edu/getting_started/installation.html) for more details!

## 🧩 This fork: RTX 50-series, uv venv, no conda

This fork of v3.9.3 (`v3.9.3-uv-5090`, from tag `v3.9.3-post2`) makes a fresh clone install
without manual patching on an RTX 5090, in a plain Python 3.11 virtual environment, with no
conda and no CUDA toolkit. Verified on Ubuntu 24.04 with driver 580.178.04.

```bash
git clone -b v3.9.3-uv-5090 https://github.com/felixzheng02/BEHAVIOR-1K.git
cd BEHAVIOR-1K
uv venv -p 3.11 --seed .venv && source .venv/bin/activate
uv pip install "setuptools>=71,<81" wheel
./setup.sh --omnigibson --bddl --dataset --confirm-no-conda \
           --accept-nvidia-eula --accept-dataset-tos
python scripts/smoke_test_stretch.py stretch_rgb.png    # should save a picture of an apartment
```

The two `--accept-*` flags accept the NVIDIA Isaac Sim EULA and the BEHAVIOR Data Bundle
EULA, which limits the dataset to non-commercial academic research. Leave them off to read
both agreements first.

**Read [INSTALL_RTX50_UV.md](INSTALL_RTX50_UV.md) for the full guide**: what the four upstream
install failures are and how this fork fixes them, which warnings are harmless, and the
v3.9.3 API gotchas worth knowing before writing your first script.

## 📄 Citation

```bibtex
@article{li2024behavior1k,
    title   = {BEHAVIOR-1K: A Human-Centered, Embodied AI Benchmark with 1,000 Everyday Activities and Realistic Simulation},
    author  = {Chengshu Li and Ruohan Zhang and Josiah Wong and Cem Gokmen and Sanjana Srivastava and Roberto Martín-Martín and Chen Wang and Gabrael Levine and Wensi Ai and Benjamin Martinez and Hang Yin and Michael Lingelbach and Minjune Hwang and Ayano Hiranaka and Sujay Garlanka and Arman Aydin and Sharon Lee and Jiankai Sun and Mona Anvari and Manasi Sharma and Dhruva Bansal and Samuel Hunter and Kyu-Young Kim and Alan Lou and Caleb R Matthews and Ivan Villa-Renteria and Jerry Huayang Tang and Claire Tang and Fei Xia and Yunzhu Li and Silvio Savarese and Hyowon Gweon and C. Karen Liu and Jiajun Wu and Li Fei-Fei},
    journal = {arXiv preprint arXiv:2403.09227},
    year    = {2024}
}
```
