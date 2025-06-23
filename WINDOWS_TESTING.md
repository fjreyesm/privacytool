# 🖥️ REGRESSION TESTING - WINDOWS INSTRUCTIONS

## ✅ COMANDOS PARA WINDOWS POWERSHELL

### PASO 1: Descargar cambios
```powershell
git pull origin main
```

### PASO 2: Verificar Docker
```powershell
docker compose ps
# Si no está ejecutándose:
docker compose up -d
```

### PASO 3: Análisis rápido (RECOMENDADO)
```powershell
# Dentro del container Django - más confiable
docker compose exec web python quick_regression_check.py
```

### PASO 4: Suite completa (PowerShell)
```powershell
# Ejecutar script de PowerShell
.\test_regression.ps1

# Solo tests críticos (más rápido)
.\test_regression.ps1 -SkipOptional

# Con salida detallada
.\test_regression.ps1 -Verbose
```

### PASO 5: Tests específicos
```powershell
# Solo tests de regresión
docker compose exec web python manage.py test core.tests.test_regression -v 2

# Solo verificar Django
docker compose exec web python manage.py check

# Solo verificar migraciones
docker compose exec web python manage.py showmigrations
```

## 🎯 WORKFLOW RECOMENDADO PARA WINDOWS

### Análisis inicial (PRIMERA VEZ):
```powershell
# 1. Descargar todo
git pull origin main

# 2. Iniciar Docker
docker compose up -d

# 3. Análisis rápido
docker compose exec web python quick_regression_check.py

# 4. Si todo está bien, ejecutar suite completa
.\test_regression.ps1
```

### Antes de nuevos cambios:
```powershell
# Verificación rápida
docker compose exec web python quick_regression_check.py
```

### Después de cambios:
```powershell
# 1. Hacer commit
git add .
git commit -m "Mi nueva funcionalidad"

# 2. Verificar regresión
.\test_regression.ps1

# 3. Si pasa, hacer push
git push origin main
```

## 🚨 TROUBLESHOOTING WINDOWS

### Error: "no se reconoce como cmdlet"
```powershell
# Usar .\ antes del script
.\test_regression.ps1

# O usar la ruta completa
C:\tu\ruta\test_regression.ps1
```

### Error: "script no firmado"
```powershell
# Cambiar política de ejecución (temporal)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Luego ejecutar
.\test_regression.ps1

# Revertir política (opcional)
Set-ExecutionPolicy -ExecutionPolicy Default -Scope CurrentUser
```

### Error: "ModuleNotFoundError: No module named 'django'"
```powershell
# NUNCA ejecutar scripts Python fuera del container
# USAR SIEMPRE:
docker compose exec web python script.py

# NO USAR:
python script.py
```

### Docker no responde
```powershell
# Reiniciar servicios
docker compose down
docker compose up -d

# Verificar logs
docker compose logs web
```

## 📊 OUTPUTS ESPERADOS

### ✅ Quick Check Success:
```
🔍 QUICK REGRESSION ANALYSIS
========================================
1. Testing basic imports...
   ✅ All imports work
2. Testing URL resolution...
   ✅ Verification page: /verification/
   ✅ Newsletter page: /newsletter/
...
✅ NO CRITICAL ISSUES FOUND!
🚀 Safe to proceed with development
```

### ✅ PowerShell Suite Success:
```
🚀 STARTING REGRESSION TESTING PIPELINE
========================================
[INFO] Step 1: Environment Check
[SUCCESS] Docker services are running
...
✅ ALL CRITICAL TESTS PASSED - SAFE TO PROCEED
```

### ❌ Failure Example:
```
❌ FOUND 3 ISSUES:
   1. URL error newsletter:subscribe: NoReverseMatch
   2. Template base.html: TemplateDoesNotExist
   3. Form validation: {'email': ['This field is required']}

🔧 RECOMMENDED FIXES:
1. Run: python manage.py migrate
2. Check URLs in urls.py files
3. Verify template files exist
```

## 🎯 COMANDOS ESPECÍFICOS PARA WINDOWS

### Ejecutar tests individuales:
```powershell
# Newsletter tests
docker compose exec web python manage.py test newsletter -v 2

# Core tests
docker compose exec web python manage.py test core -v 2

# Solo models
docker compose exec web python manage.py test newsletter.tests.SubscriberModelTest

# Solo forms
docker compose exec web python manage.py test newsletter.tests.SubscribeFormTest
```

### Debug específico:
```powershell
# Ver logs de Docker
docker compose logs web --tail 50

# Entrar al container
docker compose exec web bash

# Shell de Django
docker compose exec web python manage.py shell

# Ver URLs disponibles
docker compose exec web python manage.py show_urls
```

### Limpiar cache:
```powershell
# Limpiar containers
docker compose down
docker system prune

# Reconstruir
docker compose up -d --build
```

## 🎉 RESULTADO FINAL

Siguiendo estos pasos tendrás:
- ✅ Tests de regresión funcionando en Windows
- 🛡️ Protección contra cambios que rompan funcionalidades
- 🚀 Confianza para hacer deployments
- 📊 Reportes claros de qué funciona y qué no

---

## 🚀 PRÓXIMO PASO

**Ejecuta ahora:**
```powershell
git pull origin main
docker compose up -d
docker compose exec web python quick_regression_check.py
```

¡Y cuéntame qué resultado obtienes! 🎯
