import json
import importlib.util
from parser import parse_code, execute_ast
import sys
import os

# --- Handle absolute path for modules ---
if getattr(sys, 'frozen', False):
    current_dir = os.path.dirname(sys.executable)
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))

modules_dir = os.path.join(current_dir, "modules")
if modules_dir not in sys.path:
    sys.path.insert(0, modules_dir)

def run_file(filename):
    filename = filename.strip()
    if not filename.endswith(".scapl"):
        filename += ".scapl"

    try:
        with open(filename, "r", encoding="utf-8") as f:
            code = f.read()
        ast = parse_code(code)
        # On transmet modules_dir pour le .exe
        execute_ast(ast, modules_dir=modules_dir)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")

    try:
        input("\nPress Enter to exit...")
    except KeyboardInterrupt:
        pass

def modules(q=str()):
    q = q.strip()
    if q == "ls":
        print(f"\n--- Available modules in '{modules_dir}' ---")
        if os.path.exists(modules_dir):
            files = [
                f[:-3]
                for f in os.listdir(modules_dir)
                if f.endswith(".py") and not f.startswith("__")
            ]
            if files:
                for module_name in files:
                    print(f"  • {module_name}")
            else:
                print("  (No modules found)")
        else:
            print("  (The 'modules' directory does not exist)")
        print("-" * 40)

    elif q.startswith("h"):
        parts = q.split(maxsplit=1)
        if len(parts) > 1:
            topic = parts[1].strip()
            file_name = os.path.join(modules_dir, f"{topic}.txt")
            try:
                with open(file_name, "r", encoding="utf-8") as f:
                    print(f.read())
            except FileNotFoundError:
                print(f"Error: Help file '{topic}.txt' not found.")
        else:
            print("Error: Specify a topic (e.g., module h utils)")

    elif q.startswith("aI") or q == "config":
        parts = q.split()  
        param_path = os.path.join(current_dir, "SCAPL_param.json")
        
        params = {"auto_load_modules": []}
        if os.path.exists(param_path):
            try:
                with open(param_path, "r", encoding="utf-8") as f:
                    params = json.load(f)
            except Exception:
                pass

        if len(parts) >= 3:
            action = parts[1].lower()
            mod_name = parts[2].strip()

            if action == "add":
                if mod_name not in params["auto_load_modules"]:
                    params["auto_load_modules"].append(mod_name)
                    with open(param_path, "w", encoding="utf-8") as f:
                        json.dump(params, f, indent=4)
                    print(f"Module '{mod_name}' added to auto-loaded modules.")
                else:
                    print(f"Module '{mod_name}' is already in the list.")
            
            elif action == "del":
                if mod_name in params["auto_load_modules"]:
                    params["auto_load_modules"].remove(mod_name)
                    with open(param_path, "w", encoding="utf-8") as f:
                        json.dump(params, f, indent=4)
                    print(f"Module '{mod_name}' removed from auto-loaded modules.")
                else:
                    print(f"Module '{mod_name}' was not found in the list.")
            else:
                print("Error: Unknown action. Use 'module aI add <name>' or 'module aI del <name>'.")
        else:
            print(f"Auto-loaded modules (auto_load_modules): {params.get('auto_load_modules', [])}")

def help_cmd(q=str()):
    q = q.strip().lower()
    if not q:
        print("\n--- SCAPL IDLE - General Help ---")
        print(" • run <filename>   : Execute a .scapl script")
        print(" • module ls        : List available modules")
        print(" • module h <topic> : Read a module's help")
        print(" • module aI        : Manage auto-loaded modules")
        print(" • help             : Show this general help")
        print(" • help <command>   : Show help for a specific IDLE command/function")
        print(" • exit / quit      : Exit the IDLE")
        print("-" * 40)
    else:
        if q == "run":
            print("\n--- IDLE Help: run ---")
            print("Command: run <filename>")
            print("Description: Executes a script in .scapl format.")
            print("-" * 40)
        elif q == "module":
            print("\n--- IDLE Help: module ---")
            print("Associated commands:")
            print("  • module ls        -> Lists available modules")
            print("  • module h <name>  -> Displays a module's help (.txt file)")
            print("  • module aI        -> Manages auto-loaded modules")
            print("-" * 40)
        elif q in {"exit", "quit"}:
            print("\n--- IDLE Help: exit / quit ---")
            print("Command: exit or quit")
            print("Description: Exits the SCAPL IDLE environment.")
            print("-" * 40)
        else:
            print(f"Error: No IDLE help found for '{q}'. (For module help, use 'module h <modulename>').")

def repl():
    print("SCAPL IDLE – Type 'exit' to quit")
    global_vars = {}     
    global_modules = {}  

    param_path = os.path.join(current_dir, "SCAPL_param.json")
    if os.path.exists(param_path):
        try:
            with open(param_path, "r", encoding="utf-8") as f:
                params = json.load(f)
                auto_mods = params.get("auto_load_modules", [])
                for mod_name in auto_mods:
                    py_file = os.path.join(modules_dir, f"{mod_name}.py")
                    if os.path.exists(py_file):
                        spec = importlib.util.spec_from_file_location(mod_name, py_file)
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)
                        global_modules[mod_name] = mod
                        print(f"[Auto-loaded module: {mod_name}]")
        except Exception as e:
            print(f"Error loading SCAPL_param.json: {e}")

    while True:
        try:
            line = input(">>> ")
            if line.strip().lower() in {"exit", "quit"}:
                break
            if not line.strip():
                continue
            if line.strip().lower().startswith("run "):
                run_file(line[4:].strip())
                continue  
            if line.strip().lower().startswith("module "):
                modules(line[7:])
                continue 
            if line.strip().lower().startswith("help"):
                help_cmd(line[4:].strip())
                continue
            
            ast = parse_code(line)
            execute_ast(ast, global_vars, global_modules, modules_dir=modules_dir)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        repl()