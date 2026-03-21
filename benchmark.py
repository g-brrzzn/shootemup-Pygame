import pygame
import time
import platform
import os
import subprocess
from datetime import datetime
from random import randint

from constants.global_var import config
from classes.particles.Spark import SparkSystem
from constants.ShaderManager import ShaderManager
from constants import moderngl_utils


def get_cpu_name():
    try:
        if platform.system() == "Windows":
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"HARDWARE\DESCRIPTION\System\CentralProcessor\0",
            )
            name = winreg.QueryValueEx(key, "ProcessorNameString")[0]
            return name.strip()
        elif platform.system() == "Linux":
            output = subprocess.check_output(["cat", "/proc/cpuinfo"]).decode()
            for line in output.split("\n"):
                if "model name" in line:
                    return line.split(":")[1].strip()
        elif platform.system() == "Darwin":
            return subprocess.check_output(
                ["sysctl", "-n", "machdep.cpu.brand_string"], text=True
            ).strip()
    except Exception:
        pass
    return platform.processor() or "Unknown CPU"


def get_gpu_name():
    try:
        if platform.system() == "Windows":
            output = subprocess.check_output(
                ["wmic", "path", "win32_VideoController", "get", "name"], text=True
            )
            lines = [
                line.strip()
                for line in output.split("\n")
                if line.strip() and "Name" not in line
            ]
            if not lines:
                return "Unknown GPU"

            for line in lines:
                upper_line = line.upper()
                if "NVIDIA" in upper_line or "RTX" in upper_line or "GTX" in upper_line:
                    return line
                if "RADEON RX" in upper_line or (
                    "RADEON" in upper_line and "GRAPHICS" not in upper_line
                ):
                    return line
            return lines[0]

        elif platform.system() == "Linux":
            output = subprocess.check_output(
                "lspci -vnn | grep VGA", shell=True, text=True
            )
            return output.strip()

        elif platform.system() == "Darwin":
            output = (
                subprocess.check_output(
                    "system_profiler SPDisplaysDataType | grep Chipset",
                    shell=True,
                    text=True,
                )
                .strip()
                .split(": ")[1]
            )
            return output

    except Exception:
        pass
    return "Unknown GPU"


class Benchmark:
    def __init__(self, mode):
        self.mode = mode
        pygame.init()

        display_flags = pygame.DOUBLEBUF

        if self.mode in ["GL_RAW", "GL_SHADER"]:
            display_flags |= pygame.OPENGL
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
            pygame.display.gl_set_attribute(
                pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE
            )
            self.display = pygame.display.set_mode(
                config.window_size, display_flags, vsync=False
            )

            if self.mode == "GL_SHADER":
                self.shader_manager = ShaderManager(
                    config.INTERNAL_RESOLUTION, config.window_size
                )
                self.render_surface = self.shader_manager.get_draw_surface()
            elif self.mode == "GL_RAW":
                self.shader_manager = None
                self.texture_handler = moderngl_utils.TextureHandler(10)
                self.raw_gl_surface = moderngl_utils.GLSurface(
                    config.INTERNAL_RESOLUTION, config.window_size, self.texture_handler
                )
                self.render_surface = self.raw_gl_surface.surface
        else:
            self.display = pygame.display.set_mode(
                config.window_size, display_flags, vsync=False
            )
            self.shader_manager = None
            self.render_surface = pygame.Surface(
                config.INTERNAL_RESOLUTION, pygame.SRCALPHA
            )

        pygame.display.set_caption(f"Shoot'em Up Engine - Benchmark [{self.mode}]")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Courier New", 24, bold=True)

        self.spark_system = SparkSystem(max_particles=15000)
        self.results = []

        self.phases = [
            {"name": "Warmup (Low Load)", "target": 500, "duration": 5},
            {"name": "Mid Load", "target": 2000, "duration": 5},
            {"name": "Heavy Load", "target": 5000, "duration": 5},
            {"name": "Bullet Hell Chaos", "target": 10000, "duration": 5},
        ]

    def spawn_sparks(self, target_count):
        center_x = config.INTERNAL_RESOLUTION[0] // 2
        center_y = config.INTERNAL_RESOLUTION[1] // 2

        while self.spark_system.active_count < target_count:
            self.spark_system.emit(
                pos=(center_x, center_y),
                angle=randint(0, 360),
                speed=randint(5, 15),
                color=(255, 200, 50),
                scale=1.5,
                fixed_decay=1,
            )

    def run_phase(self, phase):
        phase_name = phase["name"]
        target = phase["target"]
        duration = phase["duration"]

        print(f"Running {phase_name} ({target} particles)...")

        start_time = time.time()
        frames_rendered = 0

        self.spark_system.active_count = 0

        while time.time() - start_time < duration:
            dt = 1.0
            self.spawn_sparks(target)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None

            self.render_surface.fill((15, 25, 27, 255))

            self.spark_system.update(dt)
            self.spark_system.draw(self.render_surface)

            elapsed = time.time() - start_time
            fps = self.clock.get_fps()

            ui_text = [
                f"MODE: {self.mode}",
                f"PHASE: {phase_name}",
                f"PARTICLES: {self.spark_system.active_count}",
                f"FPS: {int(fps)} (UNLOCKED)",
                f"TIME: {elapsed:.1f} / {duration}s",
            ]

            for i, text in enumerate(ui_text):
                surf = self.font.render(text, True, (255, 255, 255))
                self.render_surface.blit(surf, (10, 10 + (i * 30)))

            if self.mode == "GL_SHADER":
                self.shader_manager.draw()
            elif self.mode == "GL_RAW":
                self.texture_handler.clear_memory()
                self.raw_gl_surface.draw()
            else:
                scaled = pygame.transform.scale(
                    self.render_surface, self.display.get_size()
                )
                self.display.blit(scaled, (0, 0))

            pygame.display.flip()
            self.clock.tick(0)
            frames_rendered += 1

        avg_fps = frames_rendered / duration
        return {"phase": phase_name, "particles": target, "avg_fps": avg_fps}

    def calculate_score(self):
        total_score = 0
        for res in self.results:
            phase_score = (res["avg_fps"] * res["particles"]) / 100
            total_score += phase_score
        return int(total_score)

    def save_report(self, final_score):
        cpu_info = get_cpu_name()
        gpu_info = get_gpu_name()
        os_info = f"{platform.system()} {platform.release()}"
        python_version = platform.python_version()
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        target_score_note = "Target for 60FPS Bullet Hell: ~1500"

        report = [
            f"\n[{date_str}] - MODE: {self.mode}",
            f"OS: {os_info}",
            f"CPU: {cpu_info}",
            f"GPU: {gpu_info}",
            f"Python: {python_version} | Pygame: {pygame.version.ver}",
            "-" * 60,
        ]

        for res in self.results:
            report.append(
                f" - {res['phase']:<20}: {res['particles']} particles -> {res['avg_fps']:.1f} FPS"
            )

        report.append("-" * 60)
        report.append(f"FINAL SCORE: {final_score} ({target_score_note})")
        report.append("=" * 60)

        report_str = "\n".join(report)

        with open("benchmark_results.txt", "a") as f:
            f.write(report_str + "\n")

        return report_str

    def run(self):
        for phase in self.phases:
            result = self.run_phase(phase)
            if result is None:
                return
            self.results.append(result)

        final_score = self.calculate_score()
        report_str = self.save_report(final_score)

        while True:
            self.render_surface.fill((15, 25, 27, 255))
            y_offset = 50

            header = self.font.render(
                f"BENCHMARK COMPLETE [{self.mode}] - SAVED", True, (0, 255, 150)
            )
            self.render_surface.blit(header, (50, 20))

            for line in report_str.split("\n"):
                if line.startswith("-") or line.startswith("="):
                    continue
                surf = self.font.render(line, True, (200, 200, 200))
                self.render_surface.blit(surf, (50, y_offset))
                y_offset += 25

            if self.mode == "GL_SHADER":
                self.shader_manager.draw()
            elif self.mode == "GL_RAW":
                self.texture_handler.clear_memory()
                self.raw_gl_surface.draw()
            else:
                scaled = pygame.transform.scale(
                    self.render_surface, self.display.get_size()
                )
                self.display.blit(scaled, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    pygame.quit()
                    return

            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    print("========================================")
    print("  SHOOT'EM UP ENGINE - BENCHMARK SETUP  ")
    print("========================================")
    print("Select Render Mode:")
    print(" [1] Pygame 2D (No OpenGL, CPU Scaling)")
    print(" [2] ModernGL RAW (Hardware Scaling, No Shaders)")
    print(" [3] ModernGL SHADER (Game Mode, CRT Shaders)")

    choice = ""
    while choice not in ["1", "2", "3"]:
        choice = input("\nEnter choice (1-3): ").strip()

    mode_map = {"1": "PYGAME_2D", "2": "GL_RAW", "3": "GL_SHADER"}
    selected_mode = mode_map[choice]

    print(f"\nStarting benchmark with mode: {selected_mode}...")
    bench = Benchmark(mode=selected_mode)
    bench.run()
