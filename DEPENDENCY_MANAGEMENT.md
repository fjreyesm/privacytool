# SISTEMA DE GESTIÓN DE DEPENDENCIAS
=====================================

## ¿Por qué se corrupen las dependencias?

Cuando implementas nuevas funcionalidades (como el newsletter), es común que:
1. Se instalen nuevas librerías sin actualizar `requirements.txt`
2. Se modifiquen variables `.env` sin documentar los cambios
3. Los containers se reconstruyan sin las dependencias completas
4. Se pierdan configuraciones que funcionaban anteriormente

## Sistema de Verificación Automática

He creado un sistema de 4 scripts que **PREVIENEN** que las dependencias se corrompan:

### 1. 🔧 `fix_docker_config.py` - Diagnóstico Docker
**Cuándo usar**: Cuando Docker no funciona o hay problemas de containers

```bash
python fix_docker_config.py
```

**Qué hace**:
- ✅ Verifica Docker esté funcionando
- ✅ Valida `compose.yml` y `.env`
- 🧹 Limpia containers corruptos
- 🔨 Reconstruye desde cero
- 🧪 Prueba conectividad

### 2. 📦 `check_dependencies.py` - Verificador de Dependencias
**Cuándo usar**: Antes y después de agregar nuevas funcionalidades

```bash
# Dentro del container
docker compose exec web python check_dependencies.py
```

**Qué hace**:
- ✅ Verifica todos los módulos críticos estén instalados
- ✅ Confirma que Pillow está disponible (requerido para ImageField)
- ✅ Valida que `requirements.txt` esté completo
- 💾 Genera backup automático de dependencias actuales

### 3. ⚙️ `check_env_config.py` - Verificador de Configuración
**Cuándo usar**: Cuando hay problemas de configuración o faltan variables

```bash
python check_env_config.py
```

**Qué hace**:
- ✅ Verifica variables críticas, importantes y opcionales
- 📝 Genera template `.env.missing` con lo que falta
- 💡 Sugiere configuraciones apropiadas
- 🔐 Ayuda a generar SECRET_KEY segura

### 4. ✅ `quick_regression_check.py` - Tests Rápidos
**Cuándo usar**: Para verificar que todo funciona después de cambios

```bash
docker compose exec web python quick_regression_check.py
```

## Workflow para Mantener Dependencias

### ANTES de Implementar Nueva Funcionalidad:

```bash
# 1. Verificar estado actual
python check_dependencies.py
python check_env_config.py

# 2. Hacer backup
docker compose exec web pip freeze > requirements_backup_$(date +%Y%m%d).txt

# 3. Implementar funcionalidad...
```

### DESPUÉS de Implementar Nueva Funcionalidad:

```bash
# 1. Actualizar requirements.txt con TODAS las dependencias
docker compose exec web pip freeze > requirements_new.txt

# 2. Revisar y mergear manualmente a requirements.txt
# IMPORTANTE: No reemplazar, sino MERGEAR manteniendo lo existente

# 3. Verificar que todo esté completo
python check_dependencies.py

# 4. Reconstruir containers con dependencias completas
docker compose build --no-cache
docker compose up -d

# 5. Ejecutar tests de verificación
.\test_regression_simple.ps1
```

## Estructura Actual de Dependencias

### Core Dependencies (NUNCA ELIMINAR):
```
Django==4.2.16
django-htmx==1.17.2
django-csp==3.8
django-ratelimit==4.1.0
python-dotenv==1.0.0
psycopg2-binary==2.9.9
requests==2.31.0
```

### Image Processing (CRÍTICO para BlogPost y Tool):
```
Pillow==10.4.0
```

### Newsletter Dependencies:
```
django-allauth==0.61.1
bleach==6.1.0
```

## Variables .env Críticas

### NUNCA ELIMINAR (proyecto no funciona sin estas):
```
SECRET_KEY=
DEBUG=
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
```

### IMPORTANTES (funcionalidad limitada sin estas):
```
SITE_URL=
SITE_DOMAIN=
ALLOWED_HOSTS=
EMAIL_BACKEND=
DEFAULT_FROM_EMAIL=
```

## Comandos de Emergencia

### Si todo está roto:
```bash
# 1. Full reset
python fix_docker_config.py
# Responder 'y' para reconstruir

# 2. Verificar dependencias
docker compose exec web python check_dependencies.py

# 3. Si faltan dependencias, instalar:
docker compose exec web pip install Pillow==10.4.0
docker compose exec web pip install bleach==6.1.0

# 4. Verificar funcionalidad
.\test_regression_simple.ps1
```

### Si solo faltan dependencias:
```bash
# Ver qué falta
docker compose exec web python check_dependencies.py

# Instalar lo que falte (ejemplo):
docker compose exec web pip install Pillow==10.4.0

# Actualizar requirements.txt
docker compose exec web pip freeze > requirements_current.txt
# Mergear manualmente con requirements.txt
```

## Buenas Prácticas

### ✅ HACER:
1. **Siempre verificar antes y después** de cambios
2. **Hacer backup** de requirements antes de cambios
3. **Mergear dependencies**, no reemplazar
4. **Documentar variables .env** nuevas
5. **Ejecutar tests** después de cambios

### ❌ NO HACER:
1. Reemplazar `requirements.txt` completamente
2. Eliminar variables `.env` sin verificar
3. Hacer `pip freeze > requirements.txt` sin revisar
4. Ignorar errores de dependencias
5. Reconstruir containers sin verificar dependencias

## Problema Actual - SOLUCIONADO

El error actual:
```
core.BlogPost.featured_image: (fields.E210) Cannot use ImageField because Pillow is not installed.
```

**Causa**: `Pillow` no estaba en `requirements.txt`
**Solución**: Ya agregado a `requirements.txt` actualizado

## Próximos Pasos para TI

1. **Ejecutar fix completo**:
```bash
python fix_docker_config.py
# Responder 'y' para reconstruir
```

2. **Verificar todo funciona**:
```bash
.\test_regression_simple.ps1
```

3. **En futuras implementaciones**, usar este workflow para **PREVENIR** corrupciones.

Este sistema asegura que **NUNCA MÁS** pierdas dependencias que funcionaban antes.
