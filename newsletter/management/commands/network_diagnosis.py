from django.core.management.base import BaseCommand
import socket
import smtplib
import ssl
from django.conf import settings

class Command(BaseCommand):
    help = 'Diagnóstica problemas de conectividad de red para SMTP'

    def add_arguments(self, parser):
        parser.add_argument('--test-smtp', action='store_true', help='Probar conexión SMTP completa')
        parser.add_argument('--test-dns', action='store_true', help='Probar resolución DNS')
        parser.add_argument('--test-socket', action='store_true', help='Probar conexión socket')

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.HTTP_INFO('=' * 60)
        )
        self.stdout.write(
            self.style.HTTP_INFO('🌐 DIAGNÓSTICO DE RED - NEWSLETTER PRIVACYTOOL')
        )
        self.stdout.write(
            self.style.HTTP_INFO('=' * 60)
        )

        # Obtener configuración de email
        email_host = getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com')
        email_port = getattr(settings, 'EMAIL_PORT', 587)
        email_user = getattr(settings, 'EMAIL_HOST_USER', '')
        email_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
        use_tls = getattr(settings, 'EMAIL_USE_TLS', False)
        use_ssl = getattr(settings, 'EMAIL_USE_SSL', False)

        self.stdout.write(f"\n📋 CONFIGURACIÓN ACTUAL:")
        self.stdout.write(f"   Host: {email_host}")
        self.stdout.write(f"   Puerto: {email_port}")
        self.stdout.write(f"   Usuario: {email_user}")
        self.stdout.write(f"   TLS: {use_tls}")
        self.stdout.write(f"   SSL: {use_ssl}")

        # Test 1: Resolución DNS
        self.test_dns_resolution(email_host)
        
        # Test 2: Conectividad básica
        self.test_socket_connection(email_host, email_port)
        
        # Test 3: Conexión SMTP (si se solicita)
        if options.get('test_smtp') or not any([options.get('test_dns'), options.get('test_socket')]):
            self.test_smtp_connection(email_host, email_port, email_user, email_password, use_tls, use_ssl)

        # Test 4: Probar puertos alternativos
        self.test_alternative_ports(email_host)

    def test_dns_resolution(self, host):
        """Probar resolución DNS"""
        self.stdout.write(f"\n🔍 PRUEBA 1: Resolución DNS para {host}")
        
        try:
            ip_address = socket.gethostbyname(host)
            self.stdout.write(
                self.style.SUCCESS(f"   ✅ DNS OK: {host} → {ip_address}")
            )
            return True
        except socket.gaierror as e:
            self.stdout.write(
                self.style.ERROR(f"   ❌ Error DNS: {e}")
            )
            self.stdout.write("   💡 Posibles soluciones:")
            self.stdout.write("      - Verificar conexión a internet")
            self.stdout.write("      - Configurar DNS en Docker (8.8.8.8, 1.1.1.1)")
            return False

    def test_socket_connection(self, host, port):
        """Probar conexión socket básica"""
        self.stdout.write(f"\n🔌 PRUEBA 2: Conexión socket a {host}:{port}")
        
        try:
            sock = socket.create_connection((host, port), timeout=10)
            sock.close()
            self.stdout.write(
                self.style.SUCCESS(f"   ✅ Socket OK: Conectado a {host}:{port}")
            )
            return True
        except socket.timeout:
            self.stdout.write(
                self.style.ERROR(f"   ❌ Timeout: No se pudo conectar a {host}:{port}")
            )
            self.stdout.write("   💡 Posibles causas:")
            self.stdout.write("      - Firewall bloqueando el puerto")
            self.stdout.write("      - Red corporativa con restricciones")
            self.stdout.write("      - Proxy corporativo")
            return False
        except socket.error as e:
            self.stdout.write(
                self.style.ERROR(f"   ❌ Error socket: {e}")
            )
            return False

    def test_smtp_connection(self, host, port, user, password, use_tls, use_ssl):
        """Probar conexión SMTP completa"""
        self.stdout.write(f"\n📧 PRUEBA 3: Conexión SMTP completa")
        
        try:
            if use_ssl:
                # Conexión SSL directa (puerto 465)
                context = ssl.create_default_context()
                server = smtplib.SMTP_SSL(host, port, context=context, timeout=30)
                self.stdout.write("   🔒 Usando SSL directo")
            else:
                # Conexión normal (puerto 587)
                server = smtplib.SMTP(host, port, timeout=30)
                self.stdout.write("   📡 Conexión SMTP establecida")
                
                if use_tls:
                    server.starttls()
                    self.stdout.write("   🔒 TLS activado")

            # Intentar autenticación si hay credenciales
            if user and password:
                server.login(user, password)
                self.stdout.write(
                    self.style.SUCCESS("   ✅ Autenticación exitosa")
                )
            else:
                self.stdout.write(
                    self.style.WARNING("   ⚠️ Sin credenciales para probar autenticación")
                )

            server.quit()
            self.stdout.write(
                self.style.SUCCESS("   ✅ Conexión SMTP completamente funcional")
            )
            return True

        except smtplib.SMTPAuthenticationError as e:
            self.stdout.write(
                self.style.ERROR(f"   ❌ Error de autenticación: {e}")
            )
            self.stdout.write("   💡 Verificar:")
            self.stdout.write("      - App Password de Google correcto")
            self.stdout.write("      - Autenticación de 2 pasos habilitada")
            return False
            
        except smtplib.SMTPException as e:
            self.stdout.write(
                self.style.ERROR(f"   ❌ Error SMTP: {e}")
            )
            return False
            
        except socket.error as e:
            self.stdout.write(
                self.style.ERROR(f"   ❌ Error de conexión: {e}")
            )
            self.stdout.write("   💡 El problema es de conectividad de red")
            return False

    def test_alternative_ports(self, host):
        """Probar puertos alternativos"""
        self.stdout.write(f"\n🔍 PRUEBA 4: Probando puertos alternativos")
        
        ports_to_test = [587, 465, 25, 2587]
        working_ports = []
        
        for port in ports_to_test:
            try:
                sock = socket.create_connection((host, port), timeout=5)
                sock.close()
                working_ports.append(port)
                self.stdout.write(
                    self.style.SUCCESS(f"   ✅ Puerto {port}: Accesible")
                )
            except:
                self.stdout.write(f"   ❌ Puerto {port}: Bloqueado/No accesible")

        if working_ports:
            self.stdout.write(f"\n📊 PUERTOS DISPONIBLES: {working_ports}")
            
            if 587 not in working_ports and 465 in working_ports:
                self.stdout.write(
                    self.style.WARNING("\n💡 RECOMENDACIÓN:")
                )
                self.stdout.write("   El puerto 587 está bloqueado pero 465 funciona.")
                self.stdout.write("   Cambia tu configuración en .env:")
                self.stdout.write("   EMAIL_PORT=465")
                self.stdout.write("   EMAIL_USE_TLS=False")
                self.stdout.write("   EMAIL_USE_SSL=True")
                
        else:
            self.stdout.write(
                self.style.ERROR("\n❌ Ningún puerto SMTP está accesible")
            )
            self.stdout.write("   Esto indica un problema serio de conectividad:")
            self.stdout.write("   - Firewall corporativo muy restrictivo")
            self.stdout.write("   - Red corporativa bloqueando SMTP")
            self.stdout.write("   - Problema de configuración de Docker")

        # Resumen final
        self.stdout.write(
            self.style.HTTP_INFO('\n📋 RESUMEN Y RECOMENDACIONES:')
        )
        
        if 587 in working_ports:
            self.stdout.write("   ✅ Tu configuración actual debería funcionar")
        elif 465 in working_ports:
            self.stdout.write("   ⚠️ Cambiar a puerto 465 con SSL")
        else:
            self.stdout.write("   ❌ Problema serio de conectividad de red")
            self.stdout.write("   🔧 Soluciones sugeridas:")
            self.stdout.write("      1. Verificar firewall de Windows")
            self.stdout.write("      2. Probar desde una red diferente")
            self.stdout.write("      3. Contactar administrador de red")
            self.stdout.write("      4. Usar hotspot móvil como prueba")
