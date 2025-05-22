# Reglas de Seguridad para el Proyecto

## 1. Prevención de Inyección SQL

- **Utilizar siempre SQLAlchemy ORM**: Nunca construir consultas SQL utilizando concatenación de strings.
- **Emplear parámetros en las consultas**: Usar `select(Model).where(Model.column == parameter)` en lugar de interpolación de strings.
- **Validar y sanitizar entradas**: Todos los inputs deben validarse mediante Pydantic.
- **Evitar queries dinámicas**: No generar consultas SQL basadas en inputs no validados.

## 2. Autenticación y Autorización

- **Almacenar contraseñas con hash**: Utilizar bcrypt para el almacenamiento seguro.
- **Implementar JWT con tiempo de expiración corto**: Los tokens no deben durar más de 30 minutos.
- **Verificación en cada endpoint**: Usar los decoradores de dependencias para validar permisos.
- **Separación clara de roles**: Implementar restricciones basadas en roles para todas las acciones.
- **Invalidación de sesiones**: Permitir la revocación de tokens en caso de compromiso.

## 3. Validación de Datos

- **Validar todas las entradas**: Usar modelos Pydantic para validar cada entrada.
- **Limitar tamaños de entrada**: Establecer límites claros para evitar ataques de DOS.
- **Sanitizar URLs**: Validar y sanitizar especialmente las URLs recibidas.
- **Validación del formato de los datos**: Aplicar reglas estrictas para correos, códigos y otros formatos.

## 4. Protección contra Ataques Web Comunes

- **Implementar CORS correctamente**: Restringir los orígenes permitidos.
- **Evitar XSS**: No permitir la renderización de HTML desde entradas de usuario.
- **Defensa contra CSRF**: Implementar tokens anti-CSRF para operaciones sensibles.
- **Encabezados de seguridad HTTP**: Configurar Content-Security-Policy, X-XSS-Protection, etc.

## 5. Gestión de Datos Sensibles

- **No almacenar datos sensibles innecesarios**: Minimizar la información almacenada.
- **Cifrar datos sensibles**: Utilizar algoritmos fuertes para cifrar información sensible.
- **Variables de entorno para secretos**: Nunca incluir secretos en el código.
- **Política de retención de datos**: Eliminar datos que ya no sean necesarios.

## 6. Limitación de Tasa (Rate Limiting)

- **Limitar solicitudes por IP**: Evitar abuso de API.
- **Restricciones más estrictas para endpoints sensibles**: Mayor protección en login/registro.
- **Monitoreo de patrones sospechosos**: Detectar y bloquear comportamientos anómalos.

## 7. Logging y Monitoreo

- **Registrar intentos de autenticación**: Especialmente los fallidos.
- **Auditar cambios sensibles**: Registrar modificaciones a datos importantes.
- **No incluir información sensible en logs**: Nunca registrar contraseñas o tokens.
- **Monitoreo de seguridad activo**: Implementar alertas para comportamientos anómalos.

## 8. Seguridad en Despliegue

- **Actualizaciones regulares**: Mantener todas las dependencias actualizadas.
- **Escaneo de vulnerabilidades**: Usar herramientas como Safety o Snyk.
- **Gestión segura de secretos**: Utilizar servicios como Vault para secretos.
- **HTTPS obligatorio**: Nunca permitir conexiones sin TLS.

## 9. Redirecciones y URLs Cortas

- **Validar todas las URLs antes de redireccionar**: Evitar redirecciones a sitios maliciosos.
- **Limitar dominios permitidos**: Restringir a dominios conocidos y seguros.
- **Escanear URLs contra listas negras**: Verificar contra bases de datos de phishing.
- **Monitorear patrones de abuso**: Detectar intentos de usar el servicio para phishing.

## 10. Manejo de Errores

- **No exponer información sensible en errores**: Usar mensajes genéricos para el cliente.
- **Logging detallado de errores**: Mantener registros detallados solo internamente.
- **Respuestas consistentes**: Mantener tiempos de respuesta similares para evitar ataques de tiempo.

## Implementación Técnica

### Prevención de Inyección SQL

```python
# CORRECTO: Usar ORM
result = await db.execute(select(User).where(User.email == email))

# INCORRECTO: Nunca hacer esto
result = await db.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

### Autenticación Segura

```python
# CORRECTO: Almacenar contraseñas con hash
hashed_password = pwd_context.hash(password)

# CORRECTO: Verificar contraseñas
is_valid = pwd_context.verify(plain_password, hashed_password)
```

### Validación con Pydantic

```python
class URLCreate(BaseModel):
    original_url: HttpUrl  # Validación automática de URLs

    @validator('original_url')
    def validate_url(cls, v):
        # Validación adicional personalizada
        if "malicious-domain.com" in str(v):
            raise ValueError("URL no permitida")
        return v
```

## Referencias

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [SQLAlchemy Security Considerations](https://docs.sqlalchemy.org/en/14/core/engines.html#engine-disposal)
- [JWT Best Practices](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)
