#!/usr/bin/env python3
"""
Dependency Checker Script
========================
Verifica que todas las dependencias necesarias estén instaladas y actualizadas
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path

def get_installed_packages():
    """Obtiene la lista de paquetes instalados"""
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                              capture_output=True, text=True)
        installed = {}
        for line in result.stdout.split('\n')[2:]:  # Skip header
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    installed[parts[0].lower()] = parts[1]
        return installed
    except Exception as e:
        print(f"Error obteniendo paquetes instalados: {e}")
        return {}

def check_critical_imports():
    """Verifica imports críticos para el proyecto"""
    critical_modules = {
        'django': 'Django framework',
        'PIL': 'Pillow (requerido para ImageField)',
        'psycopg2': 'PostgreSQL adapter',
        'requests': 'HTTP library',
        'dotenv': 'Environment variables'
    }
    
    print("🔍 VERIFICANDO IMPORTS CRÍTICOS")
    print("=" * 50)
    
    missing = []
    for module, description in critical_modules.items():
        try:
            importlib.import_module(module)
            print(f"✅ {module} - {description}")
        except ImportError:
            print(f"❌ {module} - {description} - FALTANTE!")
            missing.append(module)
    
    return missing

def check_django_dependencies():
    """Verifica dependencias específicas de Django"""
    print("\n🔍 VERIFICANDO DEPENDENCIAS DJANGO")
    print("=" * 50)
    
    try:
        # Setup Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'securecheck.settings')
        import django
        django.setup()
        
        from django.core.management import execute_from_command_line
        
        # Check for ImageField dependencies
        try:
            from PIL import Image
            print("✅ Pillow instalado - ImageField funcionará")
        except ImportError:
            print("❌ Pillow FALTANTE - ImageField fallará")
            return False
        
        # Check models can be imported
        try:
            from core.models import BlogPost, Tool
            from newsletter.models import Subscriber
            print("✅ Modelos importados correctamente")
        except Exception as e:
            print(f"❌ Error importando modelos: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error configurando Django: {e}")
        return False

def check_requirements_file():
    """Verifica el archivo requirements.txt"""
    print("\n🔍 VERIFICANDO REQUIREMENTS.TXT")
    print("=" * 50)
    
    req_file = Path('requirements.txt')
    if not req_file.exists():
        print("❌ requirements.txt no encontrado")
        return False
    
    with open(req_file) as f:
        requirements = f.read()
    
    # Dependencias críticas que DEBEN estar
    critical_deps = [
        'Django',
        'Pillow',  # CRÍTICO para ImageField
        'psycopg2-binary',
        'requests',
        'python-dotenv'
    ]
    
    missing_deps = []
    for dep in critical_deps:
        if dep.lower() not in requirements.lower():
            missing_deps.append(dep)
            print(f"❌ {dep} - FALTANTE en requirements.txt")
        else:
            print(f"✅ {dep} - Presente en requirements.txt")
    
    return len(missing_deps) == 0

def generate_requirements_backup():
    """Genera un backup de requirements actuales"""
    print("\n💾 GENERANDO BACKUP DE REQUIREMENTS")
    print("=" * 50)
    
    try:
        # Generar pip freeze
        result = subprocess.run([sys.executable, '-m', 'pip', 'freeze'], 
                              capture_output=True, text=True)
        
        backup_file = f"requirements_backup_{os.getcwd().split(os.sep)[-1]}.txt"
        with open(backup_file, 'w') as f:
            f.write("# Backup generado automáticamente\n")
            f.write("# Contiene todas las dependencias instaladas\n\n")
            f.write(result.stdout)
        
        print(f"✅ Backup guardado en: {backup_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error generando backup: {e}")
        return False

def suggest_fixes():
    """Sugiere correcciones para problemas encontrados"""
    print("\n🔧 SUGERENCIAS DE CORRECCIÓN")
    print("=" * 50)
    
    print("Para SOLUCIONAR los problemas de dependencias:")
    print()
    print("1. 📦 INSTALAR DEPENDENCIAS FALTANTES:")
    print("   docker compose exec web pip install Pillow==10.4.0")
    print("   docker compose exec web pip install bleach==6.1.0")
    print()
    print("2. 📝 ACTUALIZAR requirements.txt:")
    print("   docker compose exec web pip freeze > requirements_new.txt")
    print("   # Luego revisar y actualizar requirements.txt")
    print()
    print("3. 🔄 RECONSTRUIR CONTAINER:")
    print("   docker compose build --no-cache")
    print("   docker compose up -d")
    print()
    print("4. ✅ VERIFICAR FUNCIONALIDAD:")
    print("   docker compose exec web python manage.py check")
    print("   docker compose exec web python quick_regression_check.py")

def main():
    """Función principal"""
    print("🔍 VERIFICADOR DE DEPENDENCIAS PRIVACYTOOL")
    print("=" * 60)
    print("Verificando que todas las dependencias estén correctas")
    print("=" * 60)
    
    # Verificar imports críticos
    missing_imports = check_critical_imports()
    
    # Verificar Django
    django_ok = check_django_dependencies()
    
    # Verificar requirements.txt
    requirements_ok = check_requirements_file()
    
    # Generar backup
    backup_ok = generate_requirements_backup()
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 60)
    
    if missing_imports:
        print(f"❌ Módulos faltantes: {', '.join(missing_imports)}")
    else:
        print("✅ Todos los módulos críticos disponibles")
    
    if django_ok:
        print("✅ Django configurado correctamente")
    else:
        print("❌ Problemas con configuración Django")
    
    if requirements_ok:
        print("✅ requirements.txt completo")
    else:
        print("❌ requirements.txt incompleto")
    
    # Determinar estado general
    if missing_imports or not django_ok or not requirements_ok:
        print("\n❌ ACCIÓN REQUERIDA: Dependencias incompletas")
        suggest_fixes()
        sys.exit(1)
    else:
        print("\n✅ TODAS LAS DEPENDENCIAS CORRECTAS")
        print("🚀 El proyecto está listo para funcionar")
        sys.exit(0)

if __name__ == "__main__":
    main()
