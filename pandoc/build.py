#!/usr/bin/env python3
"""
Windows-friendly Pandoc build script for Route B
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors with proper encoding handling"""
    print(f"{description}...")
    try:
        # Use system default encoding and handle errors gracefully
        result = subprocess.run(cmd, shell=True, check=True, 
                              capture_output=True, text=True, 
                              encoding='utf-8', errors='replace')
        if result.stdout.strip():
            print(result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {description} failed")
        print(f"Command: {cmd}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return False
    except UnicodeDecodeError as e:
        print(f"Encoding error in {description}: {e}")
        # Try again with different encoding
        try:
            result = subprocess.run(cmd, shell=True, check=True, 
                                  capture_output=True, text=True, 
                                  encoding='gbk', errors='replace')
            if result.stdout.strip():
                print(result.stdout.strip())
            return True
        except:
            print("Failed with both UTF-8 and GBK encoding")
            return False

def run_command_simple(cmd, description):
    """Run command without capturing output to avoid encoding issues"""
    print(f"{description}...")
    try:
        # Just run the command and let it output directly to console
        result = subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {description} failed with return code {e.returncode}")
        return False

def main():
    print("Starting Pandoc Build Route B...")
    
    # Change to project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    # Step 1: Generate file list
    if not run_command("python3 pandoc/tools/nav_to_list.py", "Step 1: Generating file list"):
        return 1
    
    # Step 2: Preprocess files
    print("Step 2: Preprocessing files...")
    
    # Clean and recreate tmp directory
    tmp_dir = Path("pandoc/tmp")
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True)
    
    # Read file list
    try:
        with open("pandoc/files.txt", 'r', encoding='utf-8') as f:
            files = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("Error: pandoc/files.txt not found")
        return 1
    
    # Process each file
    for filepath in files:
        print(f"Processing file: {filepath}")
        
        # Create directory structure in tmp
        tmp_filepath = tmp_dir / filepath
        tmp_filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Preprocess file
        cmd = f'python3 pandoc/tools/preprocess_admonition.py < "{filepath}" > "{tmp_filepath}"'
        if not run_command(cmd, f"Preprocessing {filepath}"):
            return 1
    
    # Step 3: Generate PDF - use simple command to avoid encoding issues
    tmp_files = [f'"pandoc/tmp/{f}"' for f in files]
    files_str = " ".join(tmp_files)
    
    pdf_cmd = f'pandoc {files_str} --defaults pandoc/defaults-pdf.yaml -o pandoc/book.pdf'
    if not run_command_simple(pdf_cmd, "Step 3: Generating PDF"):
        print("Check if pandoc and xelatex are installed and in PATH")
        print("This might take several minutes for the first run...")
        return 1
    
    # Step 4: Generate LaTeX source
    tex_cmd = f'pandoc {files_str} --defaults pandoc/defaults-pdf.yaml -o pandoc/book.tex'
    if not run_command_simple(tex_cmd, "Step 4: Generating LaTeX source"):
        return 1
    
    print("\nDone! Output files:")
    print("- pandoc/book.pdf")
    print("- pandoc/book.tex")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())