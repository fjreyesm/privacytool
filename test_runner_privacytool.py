#!/usr/bin/env python3
"""
Script de pruebas mejorado para PrivacyTool
Ejecuta pruebas completas de Django con análisis detallado
"""

import subprocess
import sys
import os
import json
from datetime import datetime

class PrivacyToolTestRunner:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'test_details': [],
            'coverage_report': {},
            'errors': []
        }
    
    def run_command(self, command, capture_output=True):
        """Ejecuta comando y captura salida"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=capture_output, 
                text=True,
                timeout=300  # 5 minutos timeout
            )
            return result
        except subprocess.TimeoutExpired:
            return None
        except Exception as e:
            self.results['errors'].append(f"Error ejecutando comando: {str(e)}")
            return None
    
    def check_docker_status(self):
        """Verifica que Docker esté funcionando"""
        print("🐳 Verificando estado de Docker...")
        
        result = self.run_command("docker compose ps")
        if result and result.returncode == 0:
            print("✅ Docker Compose está activo")
            return True
        else:
            print("❌ Docker Compose no está funcionando")
            return False
    
    def run_django_tests(self):
        """Ejecuta las pruebas de Django"""
        print("\n🧪 Ejecutando pruebas de Django...")
        
        # Lista de aplicaciones para probar
        apps_to_test = ['core', 'newsletter']
        
        for app in apps_to_test:
            print(f"\n📋 Probando aplicación: {app}")
            
            # Comando para ejecutar pruebas de la app específica
            test_command = f"docker compose exec web python manage.py test {app} --verbosity=2"
            
            result = self.run_command(test_command)
            
            if result:
                if result.returncode == 0:
                    print(f"✅ Pruebas de {app}: PASARON")
                    # Analizar salida para contar pruebas
                    self.parse_test_output(result.stdout, app, 'passed')
                else:
                    print(f"❌ Pruebas de {app}: FALLARON")
                    print(f"Error: {result.stderr}")
                    self.parse_test_output(result.stderr, app, 'failed')
            else:
                print(f"⚠️ No se pudo ejecutar pruebas para {app}")
                self.results['errors'].append(f"Timeout o error ejecutando pruebas de {app}")
    
    def run_coverage_analysis(self):
        """Ejecuta análisis de cobertura"""
        print("\n📊 Ejecutando análisis de cobertura...")
        
        # Comando para ejecutar cobertura
        coverage_command = "docker compose exec web coverage run --source=. manage.py test"
        result = self.run_command(coverage_command)
        
        if result and result.returncode == 0:
            # Generar reporte de cobertura
            report_command = "docker compose exec web coverage report"
            report_result = self.run_command(report_command)
            
            if report_result:
                print("✅ Reporte de cobertura generado")
                self.results['coverage_report']['text'] = report_result.stdout
                
                # Generar reporte HTML
                html_command = "docker compose exec web coverage html"
                self.run_command(html_command)
                print("📊 Reporte HTML de cobertura generado en htmlcov/")
        else:
            print("❌ Error generando reporte de cobertura")
    
    def parse_test_output(self, output, app, status):
        """Analiza la salida de las pruebas"""
        test_detail = {
            'app': app,
            'status': status,
            'output': output[:500],  # Primeros 500 caracteres
            'timestamp': datetime.now().isoformat()
        }
        
        self.results['test_details'].append(test_detail)
        
        if status == 'passed':
            self.results['tests_passed'] += 1
        else:
            self.results['tests_failed'] += 1
        
        self.results['tests_run'] += 1
    
    def run_specific_tests(self):
        """Ejecuta pruebas específicas conocidas"""
        print("\n🎯 Ejecutando pruebas específicas...")
        
        specific_tests = [
            'core.tests.test_hibp_service',
            'core.tests.test_regression',
            'newsletter.tests'
        ]
        
        for test in specific_tests:
            print(f"\n🧩 Ejecutando: {test}")
            
            test_command = f"docker compose exec web python manage.py test {test} --verbosity=2"
            result = self.run_command(test_command)
            
            if result:
                if result.returncode == 0:
                    print(f"✅ {test}: PASÓ")
                    self.parse_test_output(result.stdout, test, 'passed')
                else:
                    print(f"❌ {test}: FALLÓ")
                    print(f"Detalles: {result.stderr[:200]}...")
                    self.parse_test_output(result.stderr, test, 'failed')
    
    def run_linting_checks(self):
        """Ejecuta verificaciones de código"""
        print("\n🔍 Ejecutando verificaciones de código...")
        
        # Verificar sintaxis de Python
        python_files = [
            'core/',
            'newsletter/',
            'securecheck/'
        ]
        
        for path in python_files:
            print(f"🐍 Verificando sintaxis en {path}...")
            
            # Usar flake8 si está disponible
            flake8_command = f"docker compose exec web flake8 {path} --count --select=E9,F63,F7,F82 --show-source --statistics"
            result = self.run_command(flake8_command)
            
            if result and result.returncode == 0:
                print(f"✅ Sintaxis correcta en {path}")
            elif result:
                print(f"⚠️ Advertencias de sintaxis en {path}")
                print(result.stdout[:300])
    
    def check_security(self):
        """Ejecuta verificaciones de seguridad básicas"""
        print("\n🔒 Ejecutando verificaciones de seguridad...")
        
        # Django security check
        security_command = "docker compose exec web python manage.py check --deploy"
        result = self.run_command(security_command)
        
        if result:
            if result.returncode == 0:
                print("✅ Verificaciones de seguridad de Django: PASARON")
            else:
                print("⚠️ Advertencias de seguridad encontradas:")
                print(result.stdout)
                
            self.results['security_check'] = {
                'status': 'passed' if result.returncode == 0 else 'warnings',
                'output': result.stdout
            }
    
    def generate_report(self):
        """Genera reporte final"""
        print("\n📋 REPORTE FINAL DE PRUEBAS")
        print("=" * 50)
        
        total_tests = self.results['tests_run']
        passed_tests = self.results['tests_passed']
        failed_tests = self.results['tests_failed']
        
        print(f"📊 Total de pruebas ejecutadas: {total_tests}")
        print(f"✅ Pruebas que pasaron: {passed_tests}")
        print(f"❌ Pruebas que fallaron: {failed_tests}")
        
        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
            print(f"📈 Tasa de éxito: {success_rate:.1f}%")
        
        if self.results['errors']:
            print(f"\n⚠️ Errores encontrados ({len(self.results['errors'])}):")
            for error in self.results['errors']:
                print(f"  - {error}")
        
        # Guardar reporte en JSON
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_file, 'w') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Reporte detallado guardado en: {report_file}")
        except Exception as e:
            print(f"⚠️ No se pudo guardar el reporte: {e}")
        
        return self.results
    
    def run_all_tests(self):
        """Ejecuta todas las pruebas en secuencia"""
        print("🚀 INICIANDO SUITE COMPLETA DE PRUEBAS PARA PRIVACYTOOL")
        print("=" * 60)
        
        # 1. Verificar Docker
        if not self.check_docker_status():
            print("❌ Docker no está funcionando. Abortando pruebas.")
            return False
        
        # 2. Ejecutar pruebas por aplicación
        self.run_django_tests()
        
        # 3. Ejecutar pruebas específicas
        self.run_specific_tests()
        
        # 4. Análisis de cobertura
        self.run_coverage_analysis()
        
        # 5. Verificaciones de código
        self.run_linting_checks()
        
        # 6. Verificaciones de seguridad
        self.check_security()
        
        # 7. Generar reporte final
        results = self.generate_report()
        
        # Determinar si las pruebas fueron exitosas en general
        success = results['tests_failed'] == 0 and len(results['errors']) == 0
        
        print(f"\n{'🎉 TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE!' if success else '⚠️ ALGUNAS PRUEBAS NECESITAN ATENCIÓN'}")
        
        return success

def main():
    """Función principal"""
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        runner = PrivacyToolTestRunner()
        
        if test_type == "quick":
            print("🏃‍♂️ Ejecutando pruebas rápidas...")
            runner.check_docker_status()
            runner.run_django_tests()
            runner.generate_report()
        elif test_type == "coverage":
            print("📊 Ejecutando análisis de cobertura...")
            runner.check_docker_status()
            runner.run_coverage_analysis()
        elif test_type == "security":
            print("🔒 Ejecutando verificaciones de seguridad...")
            runner.check_docker_status()
            runner.check_security()
        else:
            print("Opciones disponibles: quick, coverage, security")
            print("Sin argumentos ejecuta todas las pruebas")
    else:
        # Ejecutar suite completa
        runner = PrivacyToolTestRunner()
        runner.run_all_tests()

if __name__ == "__main__":
    main()
