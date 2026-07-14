# hand_to_robot

Bu repo, el hareketini robot uç-efektör hedeflerine eşleyip MuJoCo üzerinde tekrar oynatmak için hazırlanmıştır.

## Proje Yapısı

- `task2_hand_to_robot/`: Task 2 pipeline scriptleri
- `task1_smolvla_lerobot/`: Task 1 çıktıları ve ilgili klasörler
- `report/`: rapor kaynak dosyaları (LaTeX)
- `environment.yml`, `environment_full.yml`: ortam tanımları
- `requirements_lock.txt`: pip paket kilit listesi

## Hızlı Başlangıç

Aşağıdaki adımları repo kök dizininde çalıştırın.

### 1) Repo klonla

```bash
git clone <REPO_URL>
cd hand_to_robot
```

### 2) Conda ortamını kur

Tercih edilen yol:

```bash
conda env create -f environment_full.yml -n hand2robot
conda activate hand2robot
```

Alternatif (gerekirse):

```bash
conda create -n hand2robot python=3.10 -y
conda activate hand2robot
pip install -r requirements_lock.txt
```

### 3) External bağımlılıkları çek

`external/` klasörü repoya dahil değilse yalnızca gereken dependency'leri indir:

```bash
mkdir -p external
git clone --depth 1 https://github.com/google-deepmind/mujoco_menagerie.git external/mujoco_menagerie
git clone --depth 1 https://github.com/Lifelong-Robot-Learning/LIBERO.git external/LIBERO
```

## Task 2: Uçtan Uca Çalıştırma

Örnek giriş videosu: `task2_hand_to_robot/pouring.mp4`

### 1) El landmark çıkar

```bash
python task2_hand_to_robot/extract_hand_landmarks.py \
  --input task2_hand_to_robot/pouring.mp4 \
  --output-dir task2_hand_to_robot/outputs/pouring_run_01_full
```

### 2) Bilek trajesi çıkar

```bash
python task2_hand_to_robot/extract_wrist_trajectory.py \
  --input task2_hand_to_robot/outputs/pouring_run_01_full/landmarks.json \
  --output-dir task2_hand_to_robot/outputs/pouring_run_01_full_wrist_v2
```

### 3) Robot hedeflerine eşle

```bash
python task2_hand_to_robot/map_wrist_to_vx300s_targets.py \
  --input task2_hand_to_robot/outputs/pouring_run_01_full_wrist_v2/wrist_trajectory.json \
  --output-dir task2_hand_to_robot/outputs/pouring_run_01_full_targets_v2
```

### 4) MuJoCo replay + video kaydı

```bash
python task2_hand_to_robot/replay_vx300s_targets.py \
  --input task2_hand_to_robot/outputs/pouring_run_01_full_targets_v2/vx300s_targets.json \
  --scene external/mujoco_menagerie/trossen_vx300s/scene.xml \
  --headless \
  --playback-speed 0.85 \
  --record-video task2_hand_to_robot/outputs/pouring_run_01_full_targets_v2/vx300s_replay.mp4
```

### 5) Referans + replay videoyu yan yana birleştir

```bash
python task2_hand_to_robot/combine_side_by_side.py \
  --left task2_hand_to_robot/pouring.mp4 \
  --right task2_hand_to_robot/outputs/pouring_run_01_full_targets_v2/vx300s_replay.mp4 \
  --output task2_hand_to_robot/outputs/pouring_run_01_full_targets_v2/pouring_side_by_side.mp4
```

## Beklenen Çıktılar

Başarılı çalıştırmadan sonra aşağıdakiler oluşur:

- `task2_hand_to_robot/outputs/pouring_run_01_full/landmarks.json`
- `task2_hand_to_robot/outputs/pouring_run_01_full_wrist_v2/wrist_trajectory.json`
- `task2_hand_to_robot/outputs/pouring_run_01_full_targets_v2/vx300s_targets.json`
- `task2_hand_to_robot/outputs/pouring_run_01_full_targets_v2/vx300s_replay.mp4`
- `task2_hand_to_robot/outputs/pouring_run_01_full_targets_v2/pouring_side_by_side.mp4`

## Notlar

- GPU zorunlu değildir; bu pipeline CPU ile de çalışır.
- MuJoCo sahne yolu farklıysa `--scene` parametresi ile doğru XML yolunu verin.
