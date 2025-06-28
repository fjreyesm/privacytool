#!/usr/bin/env python3
"""
Environment Configuration Checker
=================================
Verifica que el archivo .env tenga todas las variables necesarias
"""

import os
from pathlib import Path

def check_env_file():
    """Verifica el archivo .env"""
    print("🔍 VERIFICANDO CONFIGURACIÓN .ENV")
    print("=" * 50)
    
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ Archivo .env no encontrado")
        return False, {}
    
    # Leer variables actuales
    env_vars = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    print(f"✅ Archivo .env encontrado con {len(env_vars)} variables")
    return True, env_vars

def check_required_variables(env_vars):
    """Verifica variables requeridas"""
    print("\n🔍 VERIFICANDO VARIABLES REQUERIDAS")
    print("=" * 50)
    
    # Variables CRÍTICAS (el proyecto no funciona sin estas)
    critical_vars = {
        'SECRET_KEY': 'Clave secreta de Django',
        'DEBUG': 'Modo debug (True/False)',
        'POSTGRES_DB': 'Nombre base de datos',
        'POSTGRES_USER': 'Usuario base de datos',
        'POSTGRES_PASSWORD': 'Password base de datos'
    }
    
    # Variables IMPORTANTES (funcionalidad limitada sin estas)
    important_vars = {
        'SITE_URL': 'URL del sitio',
        'SITE_DOMAIN': 'Dominio del sitio',
        'ALLOWED_HOSTS': 'Hosts permitidos',
        'EMAIL_BACKEND': 'Backend de email',
        'DEFAULT_FROM_EMAIL': 'Email por defecto'
    }
    
    # Variables OPCIONALES (mejoran funcionalidad)
    optional_vars = {
        'HIBP_API_KEY': 'API key de Have I Been Pwned',
        'EMAIL_HOST': 'Servidor SMTP',
        'EMAIL_HOST_USER': 'Usuario SMTP',
        'EMAIL_HOST_PASSWORD': 'Password SMTP',
        'NEWSLETTER_FROM_EMAIL': 'Email para newsletter'
    }
    
    missing_critical = []
    missing_important = []
    missing_optional = []
    
    # Verificar críticas
    print("🔴 VARIABLES CRÍTICAS:")
    for var, desc in critical_vars.items():
        if var in env_vars and env_vars[var]:
            print(f"   ✅ {var} - {desc}")
        else:
            print(f"   ❌ {var} - {desc} - FALTANTE!")
            missing_critical.append(var)
    
    # Verificar importantes
    print("\n🟡 VARIABLES IMPORTANTES:")
    for var, desc in important_vars.items():
        if var in env_vars and env_vars[var]:
            print(f"   ✅ {var} - {desc}")
        else:
            print(f"   ⚠️ {var} - {desc} - Recomendado")
            missing_important.append(var)
    
    # Verificar opcionales
    print("\n🟢 VARIABLES OPCIONALES:")
    for var, desc in optional_vars.items():
        if var in env_vars and env_vars[var]:
            print(f"   ✅ {var} - {desc}")
        else:
            print(f"   ℹ️ {var} - {desc} - Opcional")
            missing_optional.append(var)
    
    return missing_critical, missing_important, missing_optional

def generate_env_template(missing_critical, missing_important, missing_optional):
    """Genera template con variables faltantes"""
    print("\n📝 GENERANDO TEMPLATE .ENV")
    print("=" * 50)
    
    template_content = """# ===== VARIABLES FALTANTES DETECTADAS =====
# Copia estas líneas a tu .env y configúralas apropiadamente

"""
    
    if missing_critical:
        template_content += "# 🔴 CRÍTICAS (REQUERIDAS):\n"
        templates = {
            'SECRET_KEY': 'tu-clave-secreta-super-segura-aqui-cambiar-en-produccion',
            'DEBUG': 'True',
            'POSTGRES_DB': 'privacytool',
            'POSTGRES_USER': 'postgres',
            'POSTGRES_PASSWORD': 'password123'
        }
        for var in missing_critical:
            template_content += f"{var}={templates.get(var, 'CAMBIAR_ESTO')}\n"
        template_content += "\n"
    
    if missing_important:
        template_content += "# 🟡 IMPORTANTES (RECOMENDADAS):\n"
        templates = {
            'SITE_URL': 'http://127.0.0.1:8000',
            'SITE_DOMAIN': '127.0.0.1:8000',
            'ALLOWED_HOSTS': 'localhost,127.0.0.1',
            'EMAIL_BACKEND': 'django.core.mail.backends.console.EmailBackend',
            'DEFAULT_FROM_EMAIL': 'PrivacyTool <noreply@localhost>'
        }
        for var in missing_important:
            template_content += f"{var}={templates.get(var, 'CONFIGURAR_ESTO')}\n"
        template_content += "\n"
    
    if missing_optional:
        template_content += "# 🟢 OPCIONALES (MEJORAN FUNCIONALIDAD):\n"
        templates = {
            'HIBP_API_KEY': 'tu-api-key-hibp-opcional',
            'EMAIL_HOST': 'smtp.gmail.com',
            'EMAIL_HOST_USER': 'tu-email@gmail.com',
            'EMAIL_HOST_PASSWORD': 'tu-app-password',
            'NEWSLETTER_FROM_EMAIL': 'PrivacyTool Newsletter <newsletter@localhost>'
        }
        for var in missing_optional:
            template_content += f"# {var}={templates.get(var, 'OPCIONAL')}\n"
    
    # Guardar template
    with open('.env.missing', 'w') as f:
        f.write(template_content)
    
    print("✅ Template guardado en: .env.missing")
    print("💡 Copia las variables necesarias a tu .env")

def suggest_env_fixes():
    """Sugiere correcciones para el .env"""
    print("\n🔧 SUGERENCIAS PARA .ENV")
    print("=" * 50)
    
    print("Para SOLUCIONAR problemas de configuración:")
    print()
    print("1. 📋 USAR TEMPLATE GENERADO:")
    print("   - Revisa el archivo .env.missing")
    print("   - Copia las variables que necesites a .env")
    print("   - Configura los valores apropiados")
    print()
    print("2. 🔐 GENERAR SECRET_KEY SEGURA:")
    print("   python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\"")
    print()
    print("3. 📧 CONFIGURAR EMAIL (DESARROLLO):")
    print("   EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend")
    print()
    print("4. 📧 CONFIGURAR EMAIL (PRODUCCIÓN):")
    print("   - Gmail: EMAIL_HOST=smtp.gmail.com, PORT=587")
    print("   - Brevo: EMAIL_HOST=smtp-relay.brevo.com, PORT=587")
    print()
    print("5. 🔄 REINICIAR CONTAINERS:")
    print("   docker compose down && docker compose up -d")

def main():
    """Función principal"""
    print("🔍 VERIFICADOR DE CONFIGURACIÓN .ENV")
    print("=" * 60)
    print("Verificando configuración de variables de entorno")
    print("=" * 60)
    
    # Verificar archivo .env
    env_exists, env_vars = check_env_file()
    
    if not env_exists:
        print("\n❌ ARCHIVO .ENV NO ENCONTRADO")
        print("💡 Copia .env.example a .env y configúralo")
        return False
    
    # Verificar variables
    missing_critical, missing_important, missing_optional = check_required_variables(env_vars)
    
    # Generar template si hay faltantes
    if missing_critical or missing_important or missing_optional:
        generate_env_template(missing_critical, missing_important, missing_optional)
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE CONFIGURACIÓN")
    print("=" * 60)
    
    if missing_critical:
        print(f"❌ Variables críticas faltantes: {len(missing_critical)}")
        print("🚨 El proyecto NO funcionará sin estas variables")
    else:
        print("✅ Todas las variables críticas presentes")
    
    if missing_important:
        print(f"⚠️ Variables importantes faltantes: {len(missing_important)}")
        print("🔧 Funcionalidad limitada sin estas variables")
    else:
        print("✅ Variables importantes configuradas")
    
    if missing_optional:
        print(f"ℹ️ Variables opcionales disponibles: {len(missing_optional)}")
    
    # Determinar estado
    if missing_critical:
        print("\n❌ ACCIÓN REQUERIDA: Configurar variables críticas")
        suggest_env_fixes()
        return False
    else:
        print("\n✅ CONFIGURACIÓN MÍNIMA CORRECTA")
        print("🚀 El proyecto puede funcionar")
        if missing_important:
            print("💡 Considera configurar variables importantes para mejor funcionamiento")
        return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
