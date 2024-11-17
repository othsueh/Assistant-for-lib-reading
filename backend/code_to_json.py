import os
import ast
import json
import yaml
import argparse

def should_ignore_path(path):
    """
    Check if the path should be ignored
    """
    ignore_patterns = [
        '__pycache__',
        '.git',
        '.idea',
        '.vscode',
        'dist',
        '.ipynb_checkpoints',
        '.pytest_cache',
        'venv',
        'env'
    ]
    return any(pattern in path for pattern in ignore_patterns)

def is_valid_file(file_path):
    """
    Check if file is a valid python or yaml file and not empty
    """
    if not (file_path.endswith('.py') or file_path.endswith(('.yml', '.yaml'))):
        return False
        
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            if not content:  # Check if file is empty
                return False
            
            # Validate based on file type
            if file_path.endswith('.py'):
                ast.parse(content)  # Check if valid Python
            else:  # YAML file
                yaml.safe_load(content)  # Check if valid YAML
            return True
    except:
        return False

def parse_yaml_to_json(file_path):
    """
    Parse a YAML file into JSON format
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = yaml.safe_load(file)
            
        rel_path = os.path.relpath(file_path)
        
        # Create JSON structure for YAML file
        yaml_structure = {
            "file_name": rel_path,
            "type": "yaml",
            "content": content
        }
        
        return yaml_structure
    except Exception as e:
        print(f"Error parsing YAML file {file_path}: {str(e)}")
        return None

def parse_code_to_json(file_path):
    """
    Parse a Python file into JSON format
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            code = file.read()
            
        tree = ast.parse(code)
        rel_path = os.path.relpath(file_path)
        
        # Parse imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(ast.unparse(node))
                
        # Parse classes and functions
        classes = []
        other_functions = []
        
        for node in tree.body:
            # Handle classes
            if isinstance(node, ast.ClassDef):
                class_info = {
                    "name": node.name,
                    "decorators": [ast.unparse(d) for d in node.decorator_list],
                    "inherits": [ast.unparse(base) for base in node.bases],
                    "methods": []
                }
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_info = {
                            "name": item.name,
                            "decorators": [ast.unparse(d) for d in item.decorator_list],
                            "body": ast.unparse(item.body)
                        }
                        class_info["methods"].append(method_info)
                
                classes.append(class_info)
                
            # Handle standalone functions
            elif isinstance(node, ast.FunctionDef):
                function_info = {
                    "name": node.name,
                    "decorators": [ast.unparse(d) for d in node.decorator_list],
                    "body": ast.unparse(node.body)
                }
                other_functions.append(function_info)
        
        # Create JSON structure for Python file
        json_structure = {
            "file_name": rel_path,
            "type": "python",
            "imports": imports,
            "classes": classes,
            "other_functions": other_functions
        }
        
        return json_structure
    
    except Exception as e:
        print(f"Error parsing Python file {file_path}: {str(e)}")
        return None

def process_directory(root_path):
    """
    Recursively process a directory and its subdirectories
    Returns a dictionary with layer structure
    """
    result = {
        "directory": os.path.basename(root_path),
        "path": root_path,
        "files": [],
        "subdirs": []
    }
    
    try:
        # Iterate through directory
        for item in os.listdir(root_path):
            full_path = os.path.join(root_path, item)
            
            # Skip ignored paths
            if should_ignore_path(full_path):
                continue
                
            # If it's a directory, process recursively
            if os.path.isdir(full_path):
                subdir_result = process_directory(full_path)
                if subdir_result["files"] or subdir_result["subdirs"]:
                    result["subdirs"].append(subdir_result)
                    
            # If it's a file, process if valid
            elif os.path.isfile(full_path) and is_valid_file(full_path):
                if full_path.endswith('.py'):
                    json_structure = parse_code_to_json(full_path)
                else:  # YAML file
                    json_structure = parse_yaml_to_json(full_path)
                    
                if json_structure:
                    result["files"].append(json_structure)
        
        return result
        
    except Exception as e:
        print(f"Error processing directory {root_path}: {str(e)}")
        return result

def save_to_json(data, output_path):
    """
    Save the processed data to a JSON file
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved to {output_path}")
    except Exception as e:
        print(f"Error saving JSON: {str(e)}")

def print_statistics(data):
    """
    Print statistics about processed files
    """
    def count_files_by_type(data):
        python_count = 0
        yaml_count = 0
        
        for file in data["files"]:
            if file["type"] == "python":
                python_count += 1
            elif file["type"] == "yaml":
                yaml_count += 1
                
        for subdir in data["subdirs"]:
            p_count, y_count = count_files_by_type(subdir)
            python_count += p_count
            yaml_count += y_count
            
        return python_count, yaml_count
    
    python_files, yaml_files = count_files_by_type(data)
    print(f"Processed {python_files} Python files and {yaml_files} YAML files")


if __name__ == "__main__":
    
    # Create argument parser
    parser = argparse.ArgumentParser(description='Process directory structure to JSON')
    parser.add_argument('root_directory', type=str, help='Root directory path to process')
    parser.add_argument('--output', type=str, default='project_structure.json',
                      help='Output JSON file path (default: project_structure.json)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Process directory
    result = process_directory(args.root_directory)
    
    # Save the result
    save_to_json(result, args.output)
    
    # Print statistics
    print_statistics(result)