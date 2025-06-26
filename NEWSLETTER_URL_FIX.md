# 🔧 Newsletter URL Fix Needed

## Problem Found
The newsletter templates are referencing `'core:home'` but the actual URL name is `'core:index'`.

## Templates to Fix
1. `templates/newsletter/confirmation_success.html` - Line 103 and 169
2. `templates/newsletter/unsubscribe_confirm.html` (likely)
3. Other newsletter templates (check for `{% url 'core:home' %}`)

## Quick Fix Needed
Replace all instances of:
```django
{% url 'core:home' %}
```

With:
```django
{% url 'core:index' %}
```

## Test Status
- ✅ Email command works (no templates)
- ❌ Web subscription fails (templates error)
- ❌ Confirmation emails fail (template error)

## Quick Test
```bash
# This should work (no templates)
docker compose exec web python manage.py test_email --email test@example.com

# This will fail until templates are fixed
# http://127.0.0.1:8000/newsletter/
```

## Need to Update
1. Find all newsletter templates with 'core:home'
2. Replace with 'core:index'
3. Test subscription flow
4. Re-run regression tests