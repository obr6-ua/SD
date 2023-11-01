import subprocess
from colorama import Fore, Style

def build_docker_image(image_name, dockerfile_path):
    try:
        print(f"{Fore.GREEN}Building {image_name} image...{Style.RESET_ALL}")
        subprocess.run(f"docker build -t {image_name} -f {dockerfile_path} .", shell=True, check=True)
        print(f"{Fore.GREEN}{image_name} image built successfully!{Style.RESET_ALL}")
    except subprocess.CalledProcessError:
        print(f"{Fore.RED}Failed to build {image_name} image.{Style.RESET_ALL}")

image_data = [
    ("clima", "Clima.DockerFile"),
    ("engine", "Engine.DockerFile"),
    ("registry", "Registry.DockerFile"),
    ("drone", "Drone.DockerFile")
]

for image_name, dockerfile_path in image_data:
    build_docker_image(image_name, dockerfile_path)