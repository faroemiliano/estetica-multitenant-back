# Multitenancy de Agenda Bel

## Modelo de acceso

- `users` representa una identidad global (Google/email).
- `memberships` define el rol y el acceso de esa identidad en cada estetica.
- El JWT queda ligado a una sola estetica mediante `estetica_id` y `slug`.
- En cada request autenticado el backend vuelve a consultar la membresia activa; no confia en el rol incluido en el JWT.
- `clientes` guarda un perfil distinto para cada par usuario-estetica.

Las columnas legacy `users.estetica_id` y `users.role` se conservan durante la transicion para no romper los datos actuales. No se usan para autorizar requests nuevos.

## Migracion segura de Aura

1. Hacer un backup de la base de datos.
2. Configurar `DATABASE_URL` con la misma base usada por la aplicacion.
3. Ejecutar `alembic upgrade head` una sola vez antes de desplegar el codigo nuevo.
4. Desplegar el backend.

La migracion crea una membresia por cada usuario existente usando su `estetica_id` y `role` actuales. No elimina usuarios, clientes, servicios ni turnos.

No iniciar el backend nuevo contra la base existente sin ejecutar primero la migracion: el arranque ya no modifica tablas automaticamente.

## Contrato de login para el frontend

`POST /google-login` ahora requiere el tenant explicito:

```json
{
  "credential": "TOKEN_DE_GOOGLE",
  "slug": "aura"
}
```

La respuesta incluye `slug`, `estetica_id` y el rol de esa persona dentro de esa estetica.

## Alta de una estetica

Definir una clave larga y aleatoria en `PROVISIONING_KEY`. El endpoint de operacion es:

```text
POST /admin/esteticas/provision
X-Provisioning-Key: <clave>
```

El body contiene la configuracion de la estetica y, como minimo, `nombre`, `slug` y `admin_email`. La operacion crea la estetica y una membresia de administrador de forma atomica. Si el administrador ya usa Agenda Bel, se reutiliza su identidad global.

Este endpoint no debe exponerse directamente en un panel para administradores de esteticas; la clave es exclusiva del operador de la plataforma.
