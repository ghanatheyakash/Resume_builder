#!/usr/bin/env python3
"""
Setup script for Llama 3.2 8B integration with the resume builder.
This script helps install and configure Ollama with Llama 3.2 8B.
"""

import subprocess
import sys
import requests
import time
from pathlib import Path


def check_ollama_installed() -> bool:
    """Check if Ollama is installed on the system."""
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Ollama is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ollama is installed but not working properly")
            return False
    except FileNotFoundError:
        print("❌ Ollama is not installed")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False


def install_ollama():
    """Install Ollama on the system."""
    print("📦 Installing Ollama...")
    
    system = sys.platform.lower()
    
    if system.startswith('darwin'):  # macOS
        print("🍎 Installing Ollama on macOS...")
        try:
            subprocess.run(['curl', '-fsSL', 'https://ollama.ai/install.sh'], 
                          shell=True, check=True)
            print("✅ Ollama installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing Ollama: {e}")
            return False
    
    elif system.startswith('linux'):  # Linux
        print("🐧 Installing Ollama on Linux...")
        try:
            subprocess.run(['curl', '-fsSL', 'https://ollama.ai/install.sh'], 
                          shell=True, check=True)
            print("✅ Ollama installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing Ollama: {e}")
            return False
    
    elif system.startswith('win'):  # Windows
        print("🪟 Installing Ollama on Windows...")
        print("Please download and install Ollama from: https://ollama.ai/download")
        print("After installation, restart your terminal and run this script again.")
        return False
    
    else:
        print(f"❌ Unsupported operating system: {system}")
        return False


def check_ollama_running() -> bool:
    """Check if Ollama service is running."""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            print("✅ Ollama service is running")
            return True
        else:
            print("❌ Ollama service is not responding properly")
            return False
    except requests.exceptions.RequestException:
        print("❌ Ollama service is not running")
        return False


def start_ollama_service():
    """Start the Ollama service."""
    print("🚀 Starting Ollama service...")
    try:
        # Start Ollama in the background
        subprocess.Popen(['ollama', 'serve'], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        
        # Wait for service to start
        print("⏳ Waiting for Ollama service to start...")
        for i in range(30):  # Wait up to 30 seconds
            if check_ollama_running():
                print("✅ Ollama service started successfully!")
                return True
            time.sleep(1)
        
        print("❌ Ollama service failed to start within 30 seconds")
        return False
        
    except Exception as e:
        print(f"❌ Error starting Ollama service: {e}")
        return False


def check_llama_model() -> bool:
    """Check if Llama 3.2 8B model is available."""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=10)
        if response.status_code == 200:
            models = response.json().get("models", [])
            for model in models:
                model_name = model.get("name", "")
                if "llama3.2" in model_name and "8b" in model_name:
                    print(f"✅ Llama 3.2 8B model is available: {model_name}")
                    return True
            
            print("❌ Llama 3.2 8B model not found")
            return False
        else:
            print("❌ Cannot connect to Ollama API")
            return False
    except Exception as e:
        print(f"❌ Error checking Llama model: {e}")
        return False


def download_llama_model():
    """Download Llama 3.2 8B model."""
    print("📥 Downloading Llama 3.2 8B model...")
    print("This may take several minutes depending on your internet connection...")
    
    try:
        # Start the download
        process = subprocess.Popen(['ollama', 'pull', 'llama3.2:8b'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE, 
                                 text=True)
        
        # Monitor the download progress
        while True:
            if process.stdout is None:
                break
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        # Check if download was successful
        if process.returncode == 0:
            print("✅ Llama 3.2 8B model downloaded successfully!")
            return True
        else:
            print("❌ Failed to download Llama 3.2 8B model")
            return False
            
    except Exception as e:
        print(f"❌ Error downloading Llama model: {e}")
        return False


def test_llama_integration():
    """Test the Llama integration with the resume builder."""
    print("🧪 Testing Llama integration...")
    
    try:
        from generator import test_llama_connection, call_llama_api
        
        # Test connection
        if not test_llama_connection():
            print("❌ Llama connection test failed")
            return False
        
        # Test simple generation
        test_prompt = "Generate a simple JSON object with name and email fields."
        response = call_llama_api(test_prompt)
        
        if response:
            print("✅ Llama integration test successful!")
            print(f"Sample response: {response[:100]}...")
            return True
        else:
            print("❌ Llama generation test failed")
            return False
            
    except ImportError:
        print("❌ Cannot import generator module")
        return False
    except Exception as e:
        print(f"❌ Error testing Llama integration: {e}")
        return False


def main():
    """Main setup function."""
    print("🤖 Llama 3.2 8B Setup for Resume Builder")
    print("=" * 50)
    
    # Step 1: Check if Ollama is installed
    if not check_ollama_installed():
        print("\n📦 Step 1: Installing Ollama...")
        if not install_ollama():
            print("❌ Failed to install Ollama. Please install manually from https://ollama.ai")
            return False
    else:
        print("\n✅ Step 1: Ollama is already installed")
    
    # Step 2: Check if Ollama service is running
    if not check_ollama_running():
        print("\n🚀 Step 2: Starting Ollama service...")
        if not start_ollama_service():
            print("❌ Failed to start Ollama service")
            print("Please start it manually with: ollama serve")
            return False
    else:
        print("\n✅ Step 2: Ollama service is running")
    
    # Step 3: Check if Llama model is available
    if not check_llama_model():
        print("\n📥 Step 3: Downloading Llama 3.2 8B model...")
        if not download_llama_model():
            print("❌ Failed to download Llama model")
            return False
    else:
        print("\n✅ Step 3: Llama 3.2 8B model is available")
    
    # Step 4: Test integration
    print("\n🧪 Step 4: Testing integration...")
    if not test_llama_integration():
        print("❌ Integration test failed")
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("You can now use the resume builder with Llama 3.2 8B!")
    print("\nUsage examples:")
    print("  python main.py --template harvard")
    print("  python resume_from_jobs.py --urls 'your_job_urls' --template enhancv")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 