#!/usr/bin/env python3
"""
Complete Email RAG System Startup Script
Runs both backend API and Streamlit frontend
"""

import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path

class SystemRunner:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.running = True
        
    def start_backend(self):
        """Start the FastAPI backend"""
        print("🚀 Starting Email RAG Backend...")
        print("📁 Backend directory:", os.getcwd())
        print("🌐 Backend will be available at: http://localhost:8001")
        print()
        
        try:
            self.backend_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", "ingestion_api.main:app",
                "--host", "0.0.0.0",
                "--port", "8001",
                "--reload"
            ])
            print(f"✅ Backend started with PID: {self.backend_process.pid}")
        except Exception as e:
            print(f"❌ Error starting backend: {e}")
            return False
        return True
    
    def start_frontend(self):
        """Start the Streamlit frontend"""
        # Wait a bit for backend to start
        time.sleep(3)
        
        frontend_dir = Path(__file__).parent / "frontend"
        os.chdir(frontend_dir)
        
        print("🚀 Starting Email RAG Frontend...")
        print("📁 Frontend directory:", os.getcwd())
        print("🌐 Frontend will be available at: http://localhost:8501")
        print()
        
        try:
            self.frontend_process = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", "app.py",
                "--server.port", "8501",
                "--server.address", "0.0.0.0",
                "--server.headless", "true"
            ])
            print(f"✅ Frontend started with PID: {self.frontend_process.pid}")
        except Exception as e:
            print(f"❌ Error starting frontend: {e}")
            return False
        return True
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n🛑 Shutting down Email RAG System...")
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Clean up processes"""
        if self.backend_process:
            print("🛑 Stopping backend...")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
        
        if self.frontend_process:
            print("🛑 Stopping frontend...")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
        
        print("✅ System shutdown complete")
    
    def run(self):
        """Run the complete system"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("=" * 60)
        print("📧 Email RAG System - Complete Startup")
        print("=" * 60)
        print()
        
        # Start backend
        if not self.start_backend():
            print("❌ Failed to start backend. Exiting.")
            return
        
        # Start frontend in a separate thread
        frontend_thread = threading.Thread(target=self.start_frontend)
        frontend_thread.daemon = True
        frontend_thread.start()
        
        print()
        print("=" * 60)
        print("🎉 Email RAG System is running!")
        print("=" * 60)
        print("🌐 Backend API: http://localhost:8001")
        print("🌐 Frontend UI: http://localhost:8501")
        print("📚 API Docs: http://localhost:8001/docs")
        print()
        print("Press Ctrl+C to stop the system")
        print("=" * 60)
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
                
                # Check if processes are still running
                if self.backend_process and self.backend_process.poll() is not None:
                    print("❌ Backend process died unexpectedly")
                    break
                
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("❌ Frontend process died unexpectedly")
                    break
                    
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

def main():
    """Main entry point"""
    runner = SystemRunner()
    runner.run()

if __name__ == "__main__":
    main() 