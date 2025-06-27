#!/usr/bin/env python3
"""
Docker Configuration Diagnostic & Fix Script
===========================================
Diagnostica y corrige problemas comunes de configuración Docker
"""

import subprocess
import os
import sys
import time
import json

def run_command(command, capture_output=True):
    """Ejecuta un comando y retorna el resultado"""
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        else:
            result = subprocess.run(command, shell=True)
            return result.returncode == 0, "", ""
    except Exception as e:
        return False, "", str(e)

def check_docker_status():
    """Verifica el estado de Docker"""
    print("🔍 VERIFICANDO ESTADO DE DOCKER")
    print("=" * 50)
    
    # Check if Docker is running
    success, stdout, stderr = run_command("docker --version")
    if not success:
        print("❌ Docker no está instalado o no está en PATH")
        return False
    
    print(f"✅ Docker versión: {stdout.strip()}")
    
    # Check if Docker daemon is running
    success, stdout, stderr = run_command("docker info")
    if not success:
        print("❌ Docker daemon no está ejecutándose")
        print("💡 Intenta iniciar Docker Desktop")
        return False
    
    print("✅ Docker daemon ejecutándose")
    return True

def check_compose_file():
    """Verifica la configuración del docker-compose"""
    print("\n🔍 VERIFICANDO ARCHIVO COMPOSE")
    print("=" * 50)
    
    if not os.path.exists("compose.yml"):
        print("❌ No se encuentra compose.yml")
        return False
    
    print("✅ compose.yml encontrado")
    
    # Validate compose file
    success, stdout, stderr = run_command("docker compose config")
    if not success:
        print(f"❌ Error en compose.yml: {stderr}")
        return False
    
    print("✅ compose.yml válido")
    return True

def check_env_files():
    """Verifica los archivos de environment"""
    print("\n🔍 VERIFICANDO ARCHIVOS .ENV")
    print("=" * 50)
    
    if not os.path.exists(".env"):
        print("❌ Archivo .env no encontrado")
        print("💡 Copia .env.example a .env")
        return False
    
    print("✅ .env encontrado")
    
    # Check required variables
    required_vars = ['POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD']
    
    with open('.env', 'r') as f:
        env_content = f.read()
    
    missing_vars = []
    for var in required_vars:
        if var not in env_content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variables faltantes: {', '.join(missing_vars)}")
        return False
    
    print("✅ Variables de entorno configuradas")
    return True

def stop_and_cleanup():
    """Detiene y limpia containers existentes"""
    print("\n🧹 LIMPIANDO CONTAINERS EXISTENTES")
    print("=" * 50)
    
    # Stop containers
    success, stdout, stderr = run_command("docker compose down")
    if success:
        print("✅ Containers detenidos")
    else:
        print("⚠️ No había containers ejecutándose")
    
    # Remove volumes if needed (uncomment if you want to reset DB)
    # success, stdout, stderr = run_command("docker compose down -v")
    
    # Prune dangling images
    run_command("docker image prune -f")
    print("✅ Limpieza completada")

def rebuild_containers():
    """Reconstruye los containers"""
    print("\n🔨 RECONSTRUYENDO CONTAINERS")
    print("=" * 50)
    
    # Build without cache
    success, stdout, stderr = run_command("docker compose build --no-cache", capture_output=False)
    if not success:
        print("❌ Error construyendo containers")
        return False
    
    print("✅ Containers reconstruidos")
    return True

def start_services():
    """Inicia los servicios"""
    print("\n🚀 INICIANDO SERVICIOS")
    print("=" * 50)
    
    success, stdout, stderr = run_command("docker compose up -d", capture_output=False)
    if not success:
        print("❌ Error iniciando servicios")
        return False
    
    print("✅ Servicios iniciados")
    
    # Wait for services to be ready
    print("⏳ Esperando que los servicios estén listos...")
    time.sleep(15)
    
    return True

def test_services():
    """Prueba que los servicios estén funcionando"""
    print("\n🧪 PROBANDO SERVICIOS")
    print("=" * 50)
    
    # Check container status
    success, stdout, stderr = run_command("docker compose ps")
    if success:
        print("📋 Estado de containers:")
        print(stdout)
    
    # Test database connection
    success, stdout, stderr = run_command("docker compose exec -T web python manage.py check --database default")
    if success:
        print("✅ Conexión a base de datos OK")
    else:
        print(f"❌ Error conexión DB: {stderr}")
        return False
    
    # Test basic Django functionality
    success, stdout, stderr = run_command("docker compose exec -T web python manage.py check")
    if success:
        print("✅ Django system check OK")
    else:
        print(f"❌ Django system check falló: {stderr}")
        return False
    
    return True

def main():
    """Función principal de diagnóstico y corrección"""
    print("🔧 DIAGNÓSTICO Y CORRECCIÓN DOCKER")
    print("=" * 60)
    print("Este script diagnosticará y corregirá problemas comunes")
    print("=" * 60)
    
    # Step 1: Check Docker
    if not check_docker_status():
        print("\n❌ FALLO CRÍTICO: Docker no disponible")
        print("Por favor instala Docker Desktop y asegúrate que esté ejecutándose")
        sys.exit(1)
    
    # Step 2: Check compose file
    if not check_compose_file():
        print("\n❌ FALLO CRÍTICO: Problema con compose.yml")
        sys.exit(1)
    
    # Step 3: Check environment
    if not check_env_files():
        print("\n❌ FALLO CRÍTICO: Problema con variables de entorno")
        sys.exit(1)
    
    # Step 4: Clean and rebuild
    print("\n" + "=" * 60)
    response = input("¿Quieres limpiar y reconstruir los containers? (y/N): ")
    if response.lower() in ['y', 'yes', 's', 'si']:
        stop_and_cleanup()
        
        if not rebuild_containers():
            print("\n❌ FALLO: No se pudieron reconstruir los containers")
            sys.exit(1)
        
        if not start_services():
            print("\n❌ FALLO: No se pudieron iniciar los servicios")
            sys.exit(1)
    
    # Step 5: Test services
    if not test_services():
        print("\n❌ FALLO: Los servicios no están funcionando correctamente")
        print("\n💡 SUGERENCIAS:")
        print("1. Verifica que Docker Desktop esté ejecutándose")
        print("2. Revisa los logs: docker compose logs")
        print("3. Verifica el archivo .env")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ DIAGNÓSTICO COMPLETADO EXITOSAMENTE")
    print("🚀 Todos los servicios están funcionando correctamente")
    print("=" * 60)
    
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Ejecuta: docker compose exec web python quick_regression_check.py")
    print("2. Verifica la aplicación en: http://localhost:8000")
    print("3. Ejecuta los tests: python test_regression_simple.ps1")

if __name__ == "__main__":
    main()
