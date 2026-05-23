# Plan de Arquitectura - Alejandría

## Resumen Ejecutivo

Documento unificado para la transformación arquitectónica de Alejandría, diseñado para un único stakeholder con enfoque práctico y directo.

---

## 🎯 Estado Actual

### **Arquitectura Monolítica**
- **Código**: ~15,000 líneas interconectadas
- **Tecnología**: Python 3.11, FastAPI, PostgreSQL 16 + pgvector
- **Despliegue**: Docker Compose con GPU
- **Base de datos**: PostgreSQL IONOS (autoritativa)

### **Limitaciones Identificadas**
- Complejidad cognitiva alta
- Bloqueos entre módulos
- Escalabilidad todo-o-nada
- Innovación lenta por miedo a romper funcionalidad

---

## 🏗️ Propuesta de Transformación

### **Objetivo Principal**
Dividir el monolito en **microservicios especializados** para mejorar mantenibilidad, escalabilidad y desarrollo independiente.

### **Servicios Propuestos (9 técnicos + 1 contenido)**

#### **Core Services**
1. **alejandria-storage**: Almacenamiento y persistencia
2. **alejandria-search**: Búsqueda textual, semántica e híbrida  
3. **alejandria-embeddings**: Generación y gestión de embeddings
4. **alejandria-knowledge**: Grafo de conocimiento y entidades
5. **alejandria-ingestion**: Pipeline de procesamiento de documentos

#### **Application Services**
6. **alejandria-chat**: Interfaz conversacional con RAG
7. **alejandria-gateway**: API Gateway con routing y seguridad
8. **alejandria-mcp**: Servidor MCP para Claude Code
9. **alejandria-core**: Biblioteca compartida con modelos y contratos

#### **Content Services**
10. **alejandria-content**: Gestión de productos de contenido (prods/)

**Nota Importante**: El directorio `prods/` contiene los productos generados (Formas T, dossiers, artículos, discursos) y será gestionado por el repositorio `alejandria-content`. Una vez implementados los microservicios, el control de git del directorio raíz cederá a cada repositorio independiente.

#### **Application Services**
11. **alejandria-wordpress**: Plugin y tema para WordPress
12. **alejandria-web**: Aplicación web principal (React/Next.js)
13. **alejandria-mobile**: Aplicaciones móviles (iOS/Android)
14. **alejandria-admin**: Panel de administración

---

## 🌐 Integración de Productos Aplicativos

### **Arquitectura de 3 Capas**
1. **Core Services**: Backend técnico (storage, search, embeddings, etc.)
2. **API Gateway**: Punto central con routing y seguridad
3. **Application Layer**: Frontend y productos aplicativos

### **Integración WordPress Específica**
- **Bloques Gutenberg**: Búsqueda semántica, perfiles de entidades
- **Widget interactivo**: Chat RAG integrado
- **Sincronización automática**: Formas T, dossiers, artículos
- **SEO optimizado**: URLs semánticas y structured data

### **Backend for Frontend (BFF)**
- **APIs optimizadas**: Por tipo de aplicación
- **Caching inteligente**: Multi-nivel para rendimiento
- **Personalización**: Experiencias adaptadas por usuario

---

## 📋 Specs Driven Design (SDD)

### **Repositorio Centralizado**
- **Templates estandarizados**: Service spec, API spec, data model spec
- **Validación automática**: Herramientas que verifican completitud
- **Generación de código**: Tests y mocks desde especificaciones
- **Traceabilidad**: Cada línea de código vinculada a requerimientos

### **Proceso SDD**
1. **Especificación**: Definir requerimientos detallados
2. **Validación**: Verificar consistencia y completitud
3. **Implementación**: Desarrollo guiado por specs
4. **Verificación**: Tests automáticos y cumplimiento

### **Herramientas SDD**
- **Spec Validator**: Verifica calidad de especificaciones
- **Test Generator**: Crea tests desde specs automáticamente
- **Mock Generator**: Genera mocks para desarrollo
- **Doc Generator**: Crea documentación desde specs

---

## 📋 Plan de Implementación

### **Fase 1: Foundation (Semanas 1-2)**
- Crear repositorios con estructura básica
- Extraer modelos compartidos a `alejandria-core`
- Configurar CI/CD para cada repositorio
- Definir contratos de API entre servicios

### **Fase 2: Core Services (Semanas 3-6)**
- Migrar `alejandria-storage` con Postgres + pgvector
- Implementar `alejandria-embeddings` con GPU optimization
- Separar `alejandria-search` con indexación independiente
- Extraer `alejandria-knowledge` con graph algorithms
- Implementar `alejandria-core` con modelos compartidos

### **Fase 3: Business Logic (Semanas 7-8)**
- Mover `alejandria-ingestion` con async processing
- Separar `alejandria-chat` con streaming capabilities
- Implementar `alejandria-gateway` con routing inteligente
- Adaptar `alejandria-mcp` con tool discovery
- Crear templates y herramientas SDD

### **Fase 4: Application Layer (Semanas 9-10)**
- Implementar `alejandria-wordpress` con plugin y tema
- Desarrollar `alejandria-web` con React/Next.js
- Crear `alejandria-mobile` para iOS/Android
- Construir `alejandria-admin` para administración
- Integrar productos aplicativos con core services

### **Fase 5: Integration & Testing (Semanas 11-12)**
- Configurar comunicación entre servicios
- Implementar monitoring distribuido
- Testing end-to-end completo
- Performance testing y optimización

---

## 🔧 Consideraciones Técnicas

### **Comunicación Entre Servicios**
- **Síncrona**: HTTP/REST con circuit breaker
- **Asíncrona**: Message queues (RabbitMQ) para procesamiento pesado
- **Eventos**: DocumentIngested, ChunkCreated, EntityExtracted

### **Base de Datos por Servicio**
- **storage**: Postgres + pgvector
- **search**: Postgres (índices FTS)
- **knowledge**: Postgres (grafo)
- **chat**: Postgres (conversaciones)

### **Despliegue**
- **Kubernetes**: Para producción con Helm charts
- **Docker Compose**: Para desarrollo local
- **GitOps**: ArgoCD/Flux para deployment automático

---

## � Estructura de Directorios Post-Transformación

### **Directorio Raíz (Control Git Principal)**
```
alejandria/
├── README.md                     # Overview del proyecto
├── pyproject.toml               # Dependencias y scripts
├── docker/                      # Configuración Docker
├── scripts/                      # Scripts de utilidad
└── docs/                         # Documentación
```

### **Repositorios Independientes**
```
alejandria-core/                 # Modelos compartidos
alejandria-storage/               # Servicio de almacenamiento
alejandria-search/                # Servicio de búsqueda
alejandria-embeddings/            # Servicio de embeddings
alejandria-knowledge/             # Servicio de grafo
alejandria-ingestion/             # Servicio de ingestión
alejandria-chat/                  # Servicio de chat
alejandria-gateway/               # API Gateway
alejandria-mcp/                   # Servidor MCP
alejandria-wordpress/             # Plugin WordPress
alejandria-web/                   # Aplicación web
alejandria-mobile/                # Apps móviles
alejandria-admin/                 # Panel admin
alejandria-content/                # Productos de contenido (prods/)
```

### **Control de Git**
- **Raíz**: Solo contiene metadata y documentación general
- **Repositorios**: Cada uno con su propio control de versiones
- **Submodules**: Raíz incluye submodules a cada repositorio
- **Release Management**: Coordinación de releases entre repos

---

## �📊 Beneficios Esperados

### **Desarrollo**
- **Equipos independientes**: Cada servicio dueño de su dominio
- **Despliegue autónomo**: Sin bloqueos entre equipos
- **Tecnología específica**: Cada servicio puede usar su stack óptimo
- **Escalabilidad independiente**: Recursos por servicio según necesidad

### **Operaciones**
- **Aislamiento de fallos**: Un servicio caído no afecta a otros
- **Escalabilidad granular**: Escalar solo lo necesario
- **Mantenimiento simplificado**: Menos código por repositorio
- **Testing más fácil**: Unidades más pequeñas y enfocadas

### **Negocio**
- **Time-to-market menor**: Cambios más rápidos y seguros
- **Innovación**: Facilidad para experimentar con nuevos servicios
- **Resiliencia**: Sistema más robusto y tolerante a fallos
- **Costos optimizados**: Recursos utilizados eficientemente

---

## 🛠️ Herramientas Necesarias

### **Desarrollo**
- **GitHub Actions**: CI/CD para cada repositorio
- **Docker**: Contenerización de servicios
- **Kubernetes**: Orquestación en producción
- **Helm**: Templates de deployment

### **Monitoreo**
- **Prometheus**: Métricas de todos los servicios
- **Grafana**: Dashboards de visualización
- **Jaeger**: Distributed tracing
- **Loki**: Agregación de logs

### **Comunicación**
- **RabbitMQ**: Message broker para eventos asíncronos
- **Istio**: Service mesh para comunicación segura
- **Consul**: Service discovery y configuración

---

## ⚠️ Riesgos y Mitigación

### **Complejidad Operacional**
- **Riesgo**: Gestión de múltiples servicios más compleja
- **Mitigación**: Automatización exhaustiva, monitoring centralizado

### **Latencia de Red**
- **Riesgo**: Comunicación entre servicios agrega latencia
- **Mitigación**: Caching inteligente, optimización de llamadas

### **Consistencia de Datos**
- **Riesgo**: Dificultad mantener consistencia entre servicios
- **Mitigación**: Event-driven architecture, saga patterns

### **Curva de Aprendizaje**
- **Riesgo**: Equipo necesita aprender nueva arquitectura
- **Mitigación**: Documentación exhaustiva, training gradual

---

## 📈 Métricas de Éxito

### **Técnicas**
- **Response time P95**: <200ms (actual: 400-600ms)
- **System availability**: 99.99% (actual: 99.5%)
- **Deployment frequency**: >10/week (actual: 1-2/week)
- **MTTR**: <30min (actual: 4-6 hours)

### **Negocio**
- **Features per sprint**: +150%
- **Bug resolution time**: -70%
- **Developer satisfaction**: +40%
- **Time to market**: -60%

---

## 📋 Checklist de Implementación

### **Preparación**
- [ ] Definir contratos de API entre servicios
- [ ] Crear estructura de repositorios
- [ ] Configurar CI/CD para cada repo
- [ ] Establecer patrones de comunicación

### **Implementación**
- [ ] Extraer `alejandria-core`
- [ ] Migrar `alejandria-storage`
- [ ] Implementar `alejandria-embeddings`
- [ ] Separar `alejandria-search`
- [ ] Extraer `alejandria-knowledge`
- [ ] Mover `alejandria-ingestion`
- [ ] Separar `alejandria-chat`
- [ ] Implementar `alejandria-gateway`
- [ ] Adaptar `alejandria-mcp`

### **Validación**
- [ ] Testing end-to-end completo
- [ ] Performance testing
- [ ] Security testing
- [ ] Documentation actualizada
- [ ] Training del equipo

---

## 🎯 Próximos Pasos

1. **Aprobación**: Revisar y aprobar esta propuesta
2. **Plan detallado**: Timeline con dependencias y recursos
3. **PoC inicial**: Implementar un servicio como prueba
4. **Migración gradual**: Ejecutar por fases
5. **Monitoreo continuo**: Métricas y ajustes durante proceso

---

## 🔄 Actualización Continua

Este documento será actualizado durante la implementación para:
- Registrar decisiones tomadas
- Documentar lecciones aprendidas
- Ajustar timeline y recursos
- Actualizar métricas y KPIs

---

*Documento creado: Mayo 2026*
*Próxima revisión: Semanal durante implementación*
*Responsable: Único Stakeholder*
