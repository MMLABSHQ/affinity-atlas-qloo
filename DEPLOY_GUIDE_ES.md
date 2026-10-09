# PERSONA B — Affinity Atlas 0.5 — Despliegue paso a paso (Render)

**Estado:** paquete de preparación, **NO desplegado**. No publica ninguna clave.

## Qué ya está probado

- Versión 0.4: Qloo real + Qwen local, `Review status: validated` en Ubuntu.
- Versión 0.5: 32 pruebas locales sin tráfico a Qloo ni a proveedores LLM.
- No hemos probado aún Qloo ni el proveedor LLM remoto desde Render.

## Antes de empezar: dos credenciales nuevas

1. **Regenerar/rotar tu clave de Qloo.** La clave antigua apareció en mensajes de chat; NO subirla a GitHub, a un ZIP público, a capturas, ni a ningún despliegue.
2. Crear credenciales **separadas** para el modelo remoto. Por ejemplo, con OpenRouter (https://openrouter.ai/). Obtener su API key y elegir un modelo de chat disponible (revisar el catálogo actual y la licencia, el sufijo `:free` y sus límites). También puede utilizarse otro proveedor compatible con `/v1/chat/completions` si es HTTPS.

**Ollama local no se traslada automáticamente a Render**: `localhost` en Render es el servidor remoto, no tu ordenador.

## Publicar código

- Utiliza una carpeta NUEVA para versión 0.5 (no reescribas 0.4).
- Asegúrate de que `.gitignore` excluya archivos `.env`, claves y logs.
- Crear un repositorio público nuevo en GitHub, GitLab o Bitbucket y subir los archivos de 0.5, **sin claves**.
- El archivo `LICENSE` ya está incluido; confirmar derechos y atribuciones.

## Render (servicio gratuito de prueba)

- Registrarse en https://dashboard.render.com/ e iniciar **New → Blueprint**.
- Conectar el repositorio con el archivo `render.yaml`.
- El Blueprint crea un servicio web Python gratuito en la región Frankfurt con URL `https://...onrender.com`.
- En el primer asistente completar las variables marcadas `sync: false`:
  - `QLOO_API_KEY`: **clave nueva y rotada** de Qloo, introducida en Render (nunca en GitHub).
  - `ATLAS_LLM_MODEL`: identificador de modelo remoto disponible, comprobado en ese proveedor.
  - `ATLAS_LLM_API_KEY`: clave nueva del proveedor de IA.
- `ATLAS_LLM_URL` viene predefinida a `https://openrouter.ai/api/v1/chat/completions`. Si se utiliza otro proveedor, editar esta variable **solo** en configuración privada de Render, usando un endpoint HTTPS compatible.
- Verificar el despliegue público abriendo la URL en modo incógnito; `/health` debe devolver `"ok":true`, `"llm_configured":true` y `"server_key_configured":true` sin revelar ninguna clave.
- Probar en el sitio público: Nils Frahm + Madrid + objetivo educativo. Debe indicar `Bounded LLM reviewer · active` y `Review status: validated`, además de 3 propuestas reales. Si sale `fallback`, corregir el modelo remoto antes de enviar al jurado.
- Probar un segundo objetivo, a ser posible cine. Comprobar que cambia la selección.

## Protecciones incluidas (no equivalen a seguridad de producción)

- Las claves solo se leen en variables de entorno del servidor; la demo pública ignora una clave que envíe el navegador.
- No se escriben claves a disco ni al frontend; las peticiones al LLM contienen objetivo, ciudad, artista y nombres de entidades, pero **NO la clave Qloo**.
- Solo se sirve en una interfaz de red externa cuando `ATLAS_PUBLIC_DEMO=1`.
- El arranque público exige Qloo y LLM remoto por HTTPS con claves configuradas.
- Máximo 20 ejecuciones admitidas por hora y 60 por día, por instancia/proceso, más máximo 2 simultáneas; devuelve HTTP 429 cuando se supera.
- **IMPORTANTE: estos límites se reinician cuando Render suspende/reinicia el servicio**, y no son un presupuesto financiero garantizado. Imprescindible imponer límites adicionales desde Qloo/proveedor LLM, vigilar cuotas, y cerrar la demo si hay abuso.
- El plan gratuito de Render se duerme tras 15 min de inactividad, puede tardar ~1 min en reactivarse, y tiene límites de horas/banda. Conviene probarlo en el periodo de evaluación.

## Condición para declarar el hito cumplido

Solo `PUBLIC_DEPLOYMENT = PASS` cuando se cumplan conjuntamente: (1) URL HTTPS pública accesible en incógnito, (2) Qloo real en producción, (3) LLM remoto validado (`Review status: validated`), (4) clave Qloo rotada y privada, (5) repositorio público con licencia e instrucciones, (6) demo gratis y disponible durante la evaluación.

## Fuentes oficiales

- Reglas de Qloo: https://qloo.devpost.com/rules
- Render Blueprint: https://render.com/docs/blueprint-spec
- Render Free: https://render.com/docs/free
- OpenRouter API chat: https://openrouter.ai/docs/api/api-reference/chat/send-chat-completion-request
- OpenRouter precios y cuota Free: https://openrouter.ai/pricing
