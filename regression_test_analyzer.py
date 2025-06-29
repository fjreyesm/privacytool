#!/usr/bin/env python3
"""
Analizador especializado de pruebas de regresión para PrivacyTool
Basado en los archivos de regresión encontrados en el proyecto
"""

import subprocess
import json
import re
import os
from datetime import datetime
from typing import Dict, List, Tuple, Any

class RegressionTestAnalyzer:
    """
    Analizador especializado para pruebas de regresión del proyecto PrivacyTool
    """
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'regression_tests': {},
            'hibp_service_tests': {},
            'newsletter_tests': {},
            'performance_metrics': {},
            'security_checks': {},
            'recommendations': []
        }
        
    def analyze_hibp_service_tests(self):
        """Analiza las pruebas del servicio HIBP específicamente"""
        print("🔍 Analizando pruebas del servicio HIBP...")
        
        # Ejecutar pruebas específicas de HIBP
        test_command = "docker compose exec web python manage.py test core.tests.test_hibp_service -v 2"
        result = self.run_command(test_command)
        
        if result:
            hibp_analysis = self.parse_hibp_test_output(result.stdout, result.stderr)
            self.results['hibp_service_tests'] = hibp_analysis
            
            if hibp_analysis['status'] == 'passed':
                print("✅ Pruebas HIBP: PASARON")
            else:
                print("❌ Pruebas HIBP: PROBLEMAS DETECTADOS")
                
        return self.results['hibp_service_tests']
    
    def analyze_regression_tests(self):
        """Analiza las pruebas de regresión específicas"""
        print("🔄 Analizando pruebas de regresión...")
        
        # Ejecutar pruebas de regresión
        test_command = "docker compose exec web python manage.py test core.tests.test_regression -v 2"
        result = self.run_command(test_command)
        
        if result:
            regression_analysis = self.parse_regression_test_output(result.stdout, result.stderr)
            self.results['regression_tests'] = regression_analysis
            
            # Verificar cambios en funcionalidad core
            self.check_core_functionality_regression()
            
        return self.results['regression_tests']
    
    def analyze_newsletter_functionality(self):
        """Analiza la funcionalidad del newsletter para regresiones"""
        print("📧 Analizando funcionalidad del newsletter...")
        
        # Ejecutar pruebas de newsletter
        test_command = "docker compose exec web python manage.py test newsletter.tests -v 2"
        result = self.run_command(test_command)
        
        if result:
            newsletter_analysis = self.parse_newsletter_test_output(result.stdout, result.stderr)
            self.results['newsletter_tests'] = newsletter_analysis
            
            # Verificar configuración de email
            self.check_email_configuration()
            
        return self.results['newsletter_tests']
    
    def check_core_functionality_regression(self):
        """Verifica regresiones en funcionalidad core"""
        print("🧪 Verificando regresiones en funcionalidad core...")
        
        # Lista de verificaciones core
        core_checks = [
            self.check_url_patterns(),
            self.check_model_integrity(),
            self.check_view_responses(),
            self.check_template_rendering()
        ]
        
        regression_issues = []
        for check_result in core_checks:
            if not check_result['passed']:
                regression_issues.append(check_result)
        
        self.results['regression_tests']['core_issues'] = regression_issues
        
        if regression_issues:
            print(f"⚠️ {len(regression_issues)} problemas de regresión detectados")
        else:
            print("✅ No se detectaron regresiones en funcionalidad core")
    
    def check_url_patterns(self) -> Dict[str, Any]:
        """Verifica que los patrones de URL estén funcionando"""
        print("🌐 Verificando patrones de URL...")
        
        try:
            # Verificación alternativa
            test_command = "docker compose exec web python -c \"from django.test import Client; c = Client(); print('URL test:', c.get('/').status_code)\""
            alt_result = self.run_command(test_command)
            
            return {
                'check': 'url_patterns',
                'passed': alt_result and '200' in alt_result.stdout,
                'message': 'Verificación de URLs mediante cliente de prueba'
            }
                
        except Exception as e:
            return {
                'check': 'url_patterns',
                'passed': False,
                'message': f'Error verificando URLs: {str(e)}'
            }
    
    def check_model_integrity(self) -> Dict[str, Any]:
        """Verifica la integridad de los modelos"""
        print("🗄️ Verificando integridad de modelos...")
        
        try:
            # Comando para verificar modelos
            model_command = "docker compose exec web python manage.py check --database default"
            result = self.run_command(model_command)
            
            if result and result.returncode == 0:
                return {
                    'check': 'model_integrity',
                    'passed': True,
                    'message': 'Modelos íntegros'
                }
            else:
                return {
                    'check': 'model_integrity',
                    'passed': False,
                    'message': f'Problemas en modelos: {result.stderr if result else "Error desconocido"}'
                }
                
        except Exception as e:
            return {
                'check': 'model_integrity',
                'passed': False,
                'message': f'Error verificando modelos: {str(e)}'
            }
    
    def check_view_responses(self) -> Dict[str, Any]:
        """Verifica que las vistas respondan correctamente"""
        print("👁️ Verificando respuestas de vistas...")
        
        try:
            # Test básico de vista
            view_command = """docker compose exec web python -c "
from django.test import Client
c = Client()
responses = []
for url in ['/', '/admin/']:
    try:
        resp = c.get(url)
        responses.append((url, resp.status_code))
    except Exception as e:
        responses.append((url, f'Error: {e}'))
print('View responses:', responses)
" """
            
            result = self.run_command(view_command)
            
            if result and 'View responses:' in result.stdout:
                # Parsear respuestas
                success = '200' in result.stdout or '302' in result.stdout
                return {
                    'check': 'view_responses',
                    'passed': success,
                    'message': f'Respuestas de vistas: {result.stdout.strip()}'
                }
            else:
                return {
                    'check': 'view_responses',
                    'passed': False,
                    'message': 'No se pudieron verificar las vistas'
                }
                
        except Exception as e:
            return {
                'check': 'view_responses',
                'passed': False,
                'message': f'Error verificando vistas: {str(e)}'
            }
    
    def check_template_rendering(self) -> Dict[str, Any]:
        """Verifica que las plantillas se rendericen correctamente"""
        print("🎨 Verificando renderizado de plantillas...")
        
        try:
            # Comando para verificar plantillas
            template_command = "docker compose exec web python manage.py check --tag templates"
            result = self.run_command(template_command)
            
            if result and result.returncode == 0:
                return {
                    'check': 'template_rendering',
                    'passed': True,
                    'message': 'Plantillas funcionando correctamente'
                }
            else:
                return {
                    'check': 'template_rendering',
                    'passed': False,
                    'message': f'Problemas en plantillas: {result.stderr if result else "Error desconocido"}'
                }
                
        except Exception as e:
            return {
                'check': 'template_rendering',
                'passed': False,
                'message': f'Error verificando plantillas: {str(e)}'
            }
    
    def check_email_configuration(self):
        """Verifica la configuración de email para newsletter"""
        print("📧 Verificando configuración de email...")
        
        email_check_command = """docker compose exec web python -c "
from django.conf import settings
from django.core.mail import get_connection
try:
    connection = get_connection()
    print('Email backend:', settings.EMAIL_BACKEND)
    print('Email host:', getattr(settings, 'EMAIL_HOST', 'Not configured'))
    print('Email port:', getattr(settings, 'EMAIL_PORT', 'Not configured'))
    print('Email configured: True')
except Exception as e:
    print('Email configuration error:', e)
" """
        
        result = self.run_command(email_check_command)
        
        if result:
            email_config = {
                'configured': 'Email configured: True' in result.stdout,
                'details': result.stdout.strip(),
                'errors': result.stderr.strip() if result.stderr else None
            }
            
            self.results['newsletter_tests']['email_config'] = email_config
    
    def run_performance_regression_tests(self):
        """Ejecuta pruebas de regresión de rendimiento"""
        print("⚡ Ejecutando pruebas de regresión de rendimiento...")
        
        performance_tests = [
            self.test_homepage_load_time(),
            self.test_database_query_performance(),
            self.test_static_files_performance()
        ]
        
        self.results['performance_metrics'] = {
            'tests': performance_tests,
            'overall_status': all(test['passed'] for test in performance_tests)
        }
        
        return self.results['performance_metrics']
    
    def test_homepage_load_time(self) -> Dict[str, Any]:
        """Prueba el tiempo de carga de la página principal"""
        load_time_command = """docker compose exec web python -c "
import time
from django.test import Client
c = Client()
start = time.time()
response = c.get('/')
end = time.time()
load_time = end - start
print(f'Load time: {load_time:.3f}s')
print(f'Status code: {response.status_code}')
" """
        
        result = self.run_command(load_time_command)
        
        if result and 'Load time:' in result.stdout:
            load_time_match = re.search(r'Load time: ([\d.]+)s', result.stdout)
            status_match = re.search(r'Status code: (\d+)', result.stdout)
            
            if load_time_match and status_match:
                load_time = float(load_time_match.group(1))
                status_code = int(status_match.group(1))
                
                return {
                    'test': 'homepage_load_time',
                    'passed': load_time < 2.0 and status_code in [200, 302],
                    'load_time': load_time,
                    'status_code': status_code,
                    'message': f'Página carga en {load_time:.3f}s con código {status_code}'
                }
        
        return {
            'test': 'homepage_load_time',
            'passed': False,
            'message': 'No se pudo medir el tiempo de carga'
        }
    
    def test_database_query_performance(self) -> Dict[str, Any]:
        """Prueba el rendimiento de consultas a la base de datos"""
        query_test_command = """docker compose exec web python -c "
from django.test.utils import override_settings
from django.db import connection
from django.test import Client

with override_settings(DEBUG=True):
    connection.queries_log.clear()
    c = Client()
    response = c.get('/')
    query_count = len(connection.queries)
    print(f'Query count: {query_count}')
    print(f'Status: {response.status_code}')
" """
        
        result = self.run_command(query_test_command)
        
        if result and 'Query count:' in result.stdout:
            query_match = re.search(r'Query count: (\d+)', result.stdout)
            
            if query_match:
                query_count = int(query_match.group(1))
                
                return {
                    'test': 'database_query_performance',
                    'passed': query_count < 50,  # Menos de 50 consultas para la homepage
                    'query_count': query_count,
                    'message': f'Página principal hace {query_count} consultas a la BD'
                }
        
        return {
            'test': 'database_query_performance',
            'passed': False,
            'message': 'No se pudo medir el rendimiento de consultas'
        }
    
    def test_static_files_performance(self) -> Dict[str, Any]:
        """Prueba el rendimiento de archivos estáticos"""
        static_test_command = """docker compose exec web python -c "
from django.conf import settings
from django.contrib.staticfiles import finders
import os

static_root = getattr(settings, 'STATIC_ROOT', None)
static_url = getattr(settings, 'STATIC_URL', None)

print(f'Static URL: {static_url}')
print(f'Static Root: {static_root}')
print(f'Static configured: {bool(static_url)}')

common_files = ['css/main.css', 'js/main.js', 'css/style.css']
found_files = []
for file in common_files:
    if finders.find(file):
        found_files.append(file)

print(f'Found static files: {len(found_files)}')
" """
        
        result = self.run_command(static_test_command)
        
        if result and 'Static configured:' in result.stdout:
            configured = 'Static configured: True' in result.stdout
            
            return {
                'test': 'static_files_performance',
                'passed': configured,
                'message': f'Configuración de archivos estáticos: {"OK" if configured else "Problemas detectados"}',
                'details': result.stdout.strip()
            }
        
        return {
            'test': 'static_files_performance',
            'passed': False,
            'message': 'No se pudo verificar la configuración de archivos estáticos'
        }
    
    def run_command(self, command: str, timeout: int = 30):
        """Ejecuta un comando y retorna el resultado"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result
        except subprocess.TimeoutExpired:
            print(f"⚠️ Comando expiró: {command}")
            return None
        except Exception as e:
            print(f"❌ Error ejecutando comando: {e}")
            return None
    
    def parse_hibp_test_output(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """Parsea la salida de las pruebas HIBP"""
        return {
            'status': 'passed' if 'OK' in stdout and not stderr else 'failed',
            'stdout': stdout[:500],
            'stderr': stderr[:500] if stderr else None,
            'test_count': len(re.findall(r'test_\w+', stdout)),
            'specific_checks': self.extract_hibp_specific_checks(stdout)
        }
    
    def parse_regression_test_output(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """Parsea la salida de las pruebas de regresión"""
        return {
            'status': 'passed' if 'OK' in stdout and not stderr else 'failed',
            'stdout': stdout[:500],
            'stderr': stderr[:500] if stderr else None,
            'regression_checks': self.extract_regression_checks(stdout)
        }
    
    def parse_newsletter_test_output(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """Parsea la salida de las pruebas de newsletter"""
        return {
            'status': 'passed' if 'OK' in stdout and not stderr else 'failed',
            'stdout': stdout[:500],
            'stderr': stderr[:500] if stderr else None,
            'newsletter_checks': self.extract_newsletter_checks(stdout)
        }
    
    def extract_hibp_specific_checks(self, output: str) -> List[str]:
        """Extrae verificaciones específicas de HIBP del output"""
        checks = []
        hibp_patterns = [
            r'test_hibp_\w+',
            r'test_breach_\w+',
            r'test_pwn_\w+'
        ]
        
        for pattern in hibp_patterns:
            matches = re.findall(pattern, output)
            checks.extend(matches)
        
        return checks
    
    def extract_regression_checks(self, output: str) -> List[str]:
        """Extrae verificaciones de regresión del output"""
        checks = []
        regression_patterns = [
            r'test_regression_\w+',
            r'test_functionality_\w+',
            r'test_backward_\w+'
        ]
        
        for pattern in regression_patterns:
            matches = re.findall(pattern, output)
            checks.extend(matches)
        
        return checks
    
    def extract_newsletter_checks(self, output: str) -> List[str]:
        """Extrae verificaciones de newsletter del output"""
        checks = []
        newsletter_patterns = [
            r'test_newsletter_\w+',
            r'test_subscription_\w+',
            r'test_email_\w+'
        ]
        
        for pattern in newsletter_patterns:
            matches = re.findall(pattern, output)
            checks.extend(matches)
        
        return checks
    
    def generate_recommendations(self):
        """Genera recomendaciones basadas en los resultados"""
        recommendations = []
        
        # Analizar resultados y generar recomendaciones
        if not self.results['hibp_service_tests'].get('status') == 'passed':
            recommendations.append({
                'category': 'HIBP Service',
                'priority': 'High',
                'message': 'Revisar funcionalidad del servicio HIBP - pueden haber regresiones',
                'action': 'Ejecutar pruebas específicas de HIBP y verificar conectividad a la API'
            })
        
        if not self.results['newsletter_tests'].get('status') == 'passed':
            recommendations.append({
                'category': 'Newsletter',
                'priority': 'Medium',
                'message': 'Problemas detectados en funcionalidad de newsletter',
                'action': 'Verificar configuración de email y modelos de suscripción'
            })
        
        if not self.results['performance_metrics'].get('overall_status', True):
            recommendations.append({
                'category': 'Performance',
                'priority': 'Medium',
                'message': 'Detectadas regresiones de rendimiento',
                'action': 'Optimizar consultas a base de datos y tiempo de carga'
            })
        
        regression_issues = self.results.get('regression_tests', {}).get('core_issues', [])
        if regression_issues:
            recommendations.append({
                'category': 'Core Functionality',
                'priority': 'High',
                'message': f'{len(regression_issues)} problemas de regresión en funcionalidad core',
                'action': 'Revisar cambios recientes que puedan haber afectado funcionalidad base'
            })
        
        self.results['recommendations'] = recommendations
        return recommendations
    
    def run_full_regression_analysis(self):
        """Ejecuta análisis completo de regresión"""
        print("🔄 INICIANDO ANÁLISIS COMPLETO DE REGRESIÓN")
        print("=" * 50)
        
        # 1. Analizar HIBP
        self.analyze_hibp_service_tests()
        
        # 2. Analizar regresión
        self.analyze_regression_tests()
        
        # 3. Analizar newsletter
        self.analyze_newsletter_functionality()
        
        # 4. Pruebas de rendimiento
        self.run_performance_regression_tests()
        
        # 5. Generar recomendaciones
        self.generate_recommendations()
        
        # 6. Reporte final
        self.generate_regression_report()
        
        return self.results
    
    def generate_regression_report(self):
        """Genera reporte final de análisis de regresión"""
        print("\n📋 REPORTE DE ANÁLISIS DE REGRESIÓN")
        print("=" * 50)
        
        # Resumen de estado
        hibp_status = self.results['hibp_service_tests'].get('status', 'unknown')
        regression_status = self.results['regression_tests'].get('status', 'unknown')
        newsletter_status = self.results['newsletter_tests'].get('status', 'unknown')
        performance_status = 'passed' if self.results['performance_metrics'].get('overall_status', False) else 'issues'
        
        print(f"🔍 Servicio HIBP: {hibp_status}")
        print(f"🔄 Pruebas de regresión: {regression_status}")
        print(f"📧 Newsletter: {newsletter_status}")
        print(f"⚡ Rendimiento: {performance_status}")
        
        # Mostrar recomendaciones
        recommendations = self.results.get('recommendations', [])
        if recommendations:
            print(f"\n💡 RECOMENDACIONES ({len(recommendations)}):")
            for rec in recommendations:
                print(f"  [{rec['priority']}] {rec['category']}: {rec['message']}")
                print(f"    Acción: {rec['action']}")
        else:
            print("\n✅ No se detectaron problemas críticos de regresión")
        
        # Guardar reporte
        report_file = f"regression_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_file, 'w') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Reporte completo guardado en: {report_file}")
        except Exception as e:
            print(f"⚠️ No se pudo guardar el reporte: {e}")

# Función principal
def main():
    analyzer = RegressionTestAnalyzer()
    
    # Verificar argumentos
    import sys
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        
        if test_type == "hibp":
            analyzer.analyze_hibp_service_tests()
        elif test_type == "regression":
            analyzer.analyze_regression_tests()
        elif test_type == "newsletter":
            analyzer.analyze_newsletter_functionality()
        elif test_type == "performance":
            analyzer.run_performance_regression_tests()
        else:
            print("Opciones: hibp, regression, newsletter, performance")
            print("Sin argumentos ejecuta análisis completo")
    else:
        # Ejecutar análisis completo
        analyzer.run_full_regression_analysis()

if __name__ == "__main__":
    main()
