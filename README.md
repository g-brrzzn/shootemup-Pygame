# 👾 Shoot 'em Up - Pygame Engine

> A fully custom, object-oriented vertical Shoot 'em Up built from scratch in Python. It features modular state management, advanced particle physics, dynamic enemy wave generation, and a complete retro arcade aesthetic.

## 📖 About

This project goes beyond a simple game script. It was developed to serve as a robust **2D game engine foundation** using pure Pygame. The architecture relies on strict Object-Oriented principles, separating rendering logic, asset management, and game states.

---

## 📸 Gameplay & Visuals



https://github.com/user-attachments/assets/ae3f7d06-dc9a-4dbd-92b2-d3bb4390f4d4


![Menu Screenshot](https://github.com/user-attachments/assets/9fcf35c6-c23c-4212-9f83-d8f610e50c7a)

## ✨ Key Features & Engine Mechanics

The codebase is highly modularized, containing several advanced mechanics built from scratch:

- **Custom State Machine:** Seamless transitions between `Menu`, `Game`, `Pause`, `Options`, `LevelUp`, `ModMenu`, and `GameOver` without overlapping logic.
- **Advanced Combat & Arsenal:** A dynamic weapon system featuring primary/secondary fires, auto-targeting drones, ultimate fusions (e.g., Bombardment, Storm Wall), and a reactive Parry/Overdrive mechanic.
- **Particle Physics System:** Independent modules for environmental effects (`Fall` for rain/stars, `LightRays`), combat impacts (`Spark`), and multi-layered CRT-style `Explosion` generators.
- **Dynamic Wave Manager:** The `FormationManager` autonomously handles enemy spawn patterns, combo spawns, and smooth sub-wave pacing based on the escalating level difficulty.
- **Developer Tools & Cheats:** A built-in, hidden `ModMenu` for real-time debugging, featuring God Mode, infinite ricochets, instant level-ups, and a visual hitbox toggle.
- **Asset Manager:** A centralized cache for sprites, sounds, and `.ttf` fonts, including real-time mathematical generation of neon glow surfaces.
- **Entity Scaling & Collision:** Automatic internal resolution handling, full-screen toggling, and a dedicated `CollisionManager` for clean, precise hit detection.

---

## 🎮 Controls

The game features responsive standard arcade controls, alongside dedicated developer keys for testing the game balance and accessing the new cheat/debug panels:

| Action                | Keyboard                            | Controller              |
| :-------------------- | :---------------------------------- | :---------------------- |
| **Move**              | `W` `A` `S` `D` or `Arrow Keys`     | `Left Stick` or `D-Pad` |
| **Shoot**             | `Space`                             | `A`, `B` or `Triggers`  |
| **Parry / Absorb**    | `Left Shift` or `F`                 | `X`, `Y` or `LT`        |
| **Menu Navigation**   | `Up` / `Down` and `Enter`           | `D-Pad` and `A`         |
| **Pause / Back**      | `ESC`                               | `Start` / `B`           |
| **Mod Menu (Cheats)** | `Backspace`                         | `Select`                |

---

## 🛠 Tech Stack

- **Language:** Python 3
- **Graphics & Audio Library:** Pygame-ce 2.5.7 and ModernGL 5.12.0
- **Data & AI:** Numpy, Gymnasium, and Stable-Baselines3 (PPO)
- **Architecture Pattern:** Object-Oriented Programming (OOP) / State Pattern

---

## ⚙️ Installation & Run

1. **Clone the repository:**

   ```console
   git clone https://github.com/g-brrzzn/shootemup-Pygame
   cd shootemup-Pygame
   ```

1. **Install the requirements:**

   ```console
   python -m pip install -r requirements.txt
   ```

1. **Launch the game:**

   ```console
   python Game.py
   ```

---

## 🤝 Contributing (Beginner Friendly)

This project is highly modular, making it very easy to add new features without breaking everything else.
Feel free to fork the project, experiment, and submit a Pull Request. I will be happy to review it, help with the code, and merge your ideas into the main game!
