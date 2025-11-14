#!/usr/bin/env python3
"""
Setup script for Frontier AI Projects
Installs and configures all components of the Frontier AI suite.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported. Please use Python 3.8 or higher.")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_system_requirements():
    """Check system requirements."""
    print("🖥️ Checking system requirements...")
    
    # Check OS
    os_name = platform.system()
    print(f"   OS: {os_name}")
    
    # Check available memory
    try:
        import psutil
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        print(f"   RAM: {memory_gb:.1f} GB")
        if memory_gb < 8:
            print("   ⚠️  Warning: Less than 8GB RAM detected. Some features may not work optimally.")
    except ImportError:
        print("   ℹ️  psutil not available, skipping memory check")
    
    # Check CUDA availability
    try:
        import torch
        if torch.cuda.is_available():
            print(f"   GPU: CUDA {torch.version.cuda} available")
            print(f"   GPU Count: {torch.cuda.device_count()}")
        else:
            print("   GPU: CUDA not available, will use CPU")
    except ImportError:
        print("   ℹ️  PyTorch not installed yet, will check after installation")
    
    return True

def install_base_dependencies():
    """Install base dependencies."""
    print("📦 Installing base dependencies...")
    
    base_packages = [
        "torch>=2.0.0",
        "torchvision>=0.15.0",
        "torchaudio>=2.0.0",
        "transformers>=4.30.0",
        "accelerate>=0.20.0",
        "datasets>=2.12.0",
        "tokenizers>=0.13.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "tqdm>=4.64.0",
        "pyyaml>=6.0",
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "pillow>=9.0.0",
        "psutil>=5.9.0"
    ]
    
    for package in base_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            return False
    
    return True

def install_optional_dependencies():
    """Install optional dependencies for advanced features."""
    print("🔧 Installing optional dependencies...")
    
    optional_packages = [
        "deepspeed>=0.9.0",
        "flash-attn>=2.0.0",
        "xformers>=0.0.20",
        "wandb>=0.15.0",
        "tensorboard>=2.10.0",
        "jupyter>=1.0.0",
        "ipywidgets>=8.0.0",
        "plotly>=5.0.0",
        "streamlit>=1.20.0"
    ]
    
    for package in optional_packages:
        run_command(f"pip install {package}", f"Installing {package} (optional)")
    
    return True

def install_brandkit():
    """Install the brandkit package."""
    print("🎨 Installing TruthGPT BrandKit...")
    
    brandkit_path = Path(__file__).parent / "TruthGPT" / "brandkit"
    if brandkit_path.exists():
        return run_command(f"pip install -e {brandkit_path}", "Installing BrandKit")
    else:
        print("⚠️  BrandKit directory not found, skipping installation")
        return True

def install_training_suite():
    """Install the training suite."""
    print("🚀 Installing Frontier Model Training Suite...")
    
    training_path = Path(__file__).parent / "TruthGPT" / "Frontier-Model-run"
    if training_path.exists():
        return run_command(f"pip install -e {training_path}", "Installing Training Suite")
    else:
        print("⚠️  Training suite directory not found, skipping installation")
        return True

def create_directories():
    """Create necessary directories."""
    print("📁 Creating directories...")
    
    directories = [
        "output",
        "cache",
        "logs",
        "checkpoints",
        "data",
        "models",
        "results"
    ]
    
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"   ✅ Created {dir_name}/")
    
    return True

def create_config_files():
    """Create default configuration files."""
    print("⚙️ Creating configuration files...")
    
    # Create .env file
    env_content = """# Frontier AI Configuration
CUDA_VISIBLE_DEVICES=0
WANDB_PROJECT=frontier-ai
WANDB_ENTITY=your-entity
TENSORBOARD_LOG_DIR=./logs
OUTPUT_DIR=./output
CACHE_DIR=./cache
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    print("   ✅ Created .env")
    
    # Create .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyTorch
*.pth
*.pt

# Jupyter Notebook
.ipynb_checkpoints

# Environment
.env
.venv
env/
venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
output/
cache/
logs/
checkpoints/
models/
results/
*.log
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    print("   ✅ Created .gitignore")
    
    return True

def run_tests():
    """Run basic tests to verify installation."""
    print("🧪 Running installation tests...")
    
    tests = [
        ("python -c 'import torch; print(f\"PyTorch: {torch.__version__}\")'", "PyTorch import"),
        ("python -c 'import transformers; print(f\"Transformers: {transformers.__version__}\")'", "Transformers import"),
        ("python -c 'import numpy; print(f\"NumPy: {numpy.__version__}\")'", "NumPy import"),
        ("python -c 'import pandas; print(f\"Pandas: {pandas.__version__}\")'", "Pandas import"),
    ]
    
    for command, description in tests:
        if not run_command(command, description):
            print(f"⚠️  {description} test failed, but installation may still work")
    
    return True

def print_usage_instructions():
    """Print usage instructions."""
    print("\n" + "="*60)
    print("🎉 Installation completed successfully!")
    print("="*60)
    print()
    print("📚 Quick Start:")
    print("   1. Run brand analysis demo:")
    print("      python demo_brand_analyzer.py")
    print()
    print("   2. Run training demo:")
    print("      python demo_training.py")
    print()
    print("   3. Start training:")
    print("      cd TruthGPT/Frontier-Model-run")
    print("      python scripts/run_training.py")
    print()
    print("📖 Documentation:")
    print("   • Main README: README.md")
    print("   • BrandKit: TruthGPT/brandkit/README.md")
    print("   • Training: TruthGPT/Frontier-Model-run/README.md")
    print()
    print("🔧 Configuration:")
    print("   • Edit .env for environment variables")
    print("   • Modify config files in scripts/ directory")
    print()
    print("🆘 Support:")
    print("   • Check logs in logs/ directory")
    print("   • Review error messages above")
    print("   • Consult documentation for troubleshooting")
    print()

def main():
    """Main setup function."""
    print("🚀 Frontier AI Projects Setup")
    print("="*50)
    print()
    
    # Check requirements
    if not check_python_version():
        sys.exit(1)
    
    if not check_system_requirements():
        print("⚠️  System requirements check failed, but continuing...")
    
    # Install dependencies
    if not install_base_dependencies():
        print("❌ Base dependencies installation failed")
        sys.exit(1)
    
    install_optional_dependencies()
    
    # Install project packages
    install_brandkit()
    install_training_suite()
    
    # Setup project structure
    create_directories()
    create_config_files()
    
    # Run tests
    run_tests()
    
    # Print instructions
    print_usage_instructions()

if __name__ == "__main__":
    main()

