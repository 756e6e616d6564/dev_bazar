# dev_bazar

Sistema de punto de venta (POS) desarrollado con Django y React para pequeños negocios.

## Características

- 🛒 Sistema de ventas con interfaz amigable
- 📦 Gestión de productos y categorías
- 📊 Dashboard con reportes y estadísticas
- 👥 Control de usuarios y permisos
- 📱 Interfaz responsiva para cualquier dispositivo
- 📇 Soporte para lector de códigos de barras

## Tecnologías

- **Backend**: Django, Django REST Framework
- **Frontend**: React, React-Bootstrap
- **Base de datos**: SQLite (desarrollo), PostgreSQL (producción)
- **Contenedores**: Docker, Docker Compose

## Instalación

### Requisitos

- Python 3.8+
- Node.js 14+
- npm o yarn

### Configuración del entorno

1. Clonar el repositorio:

```bash
git clone https://github.com/tu-usuario/dev_bazar.git
cd dev_bazar
```

2. Crear y activar entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias de Python:

```bash
cd dev_django
pip install -r requirements.txt
```

4. Instalar dependencias de Node.js:

```bash
cd frontend
npm install
```

### Configuración inicial

1. Aplicar migraciones:

```bash
cd dev_django
python manage.py migrate
```

2. Crear datos iniciales:

```bash
python manage.py seed_db
```

3. Compilar frontend:

```bash
cd frontend
npm run build
```

### Ejecutar en desarrollo

1. Iniciar servidor Django:

```bash
cd dev_django
python manage.py runserver
```

2. En otra terminal, iniciar frontend en modo desarrollo:

```bash
cd dev_django/frontend
npm run dev
```

3. Acceder a http://localhost:8000

### Credenciales de prueba

- **Administrador**: usuario: `admin`, contraseña: `admin123`
- **Vendedor**: usuario: `vendedor`, contraseña: `vendedor123`

## Despliegue con Docker

1. Construir y levantar los contenedores:

```bash
docker-compose up -d --build
```

2. Acceder a http://localhost:8000

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo LICENSE para más detalles.