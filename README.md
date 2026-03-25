# 👾 Shoot 'em Up - Pygame Engine

> A fully custom, object-oriented vertical Shoot 'em Up built from scratch in Python. It features modular state management, advanced particle physics, dynamic enemy wave generation, and a complete retro arcade aesthetic.

## 📖 About

This project goes beyond a simple game script. It was developed to serve as a robust **2D game engine foundation** using pure Pygame. The architecture relies on strict Object-Oriented principles, separating rendering logic, asset management, and game states.

---

## 📸 Gameplay & Visuals

<https://github.com/user-attachments/assets/f3a289c4-248d-4a58-97a9-7048cefac95f>

![Menu Screenshot](https://github.com/user-attachments/assets/9fcf35c6-c23c-4212-9f83-d8f610e50c7a)

## ✨ Key Features & Engine Mechanics

The codebase is highly modularized, containing several advanced mechanics built from scratch:

- **Custom State Machine:** Seamless transitions between `Menu`, `Game`, `Pause`, `Options`, and `GameOver` without overlapping logic.
- **Particle Physics System:** Independent modules for environmental effects (`Fall` for rain/stars), combat impacts (`Spark`), and multi-layered CRT-style `Explosion` generators.
- **Dynamic Wave Manager:** The `FormationManager` autonomously handles enemy spawn patterns (V-Shape, Diagonal, Circle Clusters) based on the escalating level difficulty.
- **Asset Manager:** A centralized cache for sprites, sounds, and `.ttf` fonts, including real-time mathematical generation of neon glow surfaces.
- **Entity Scaling:** Automatic internal resolution handling and full-screen toggling.

---

## 🎮 Controls

The game features standard arcade controls, plus hidden developer keys used for testing game balance:

| Action              | Keyboard                            | Controller              |
| :------------------ | :---------------------------------- | :---------------------- |
| **Move**            | `W` `A` `S` `D` or `Arrow Keys`     | `Left Stick` or `D-Pad` |
| **Shoot**           | `Space`                             | `Right Trigger`         |
| **Menu Navigation** | `Up` / `Down` and `Enter` / `Space` | `D-Pad` and `A`         |
| **Pause / Back**    | `ESC`                               | `Start` / `B`           |

---

## 🛠 Tech Stack

- **Language:** Python 3
- **Graphics & Audio Library:** Pygame 2.5.2
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
