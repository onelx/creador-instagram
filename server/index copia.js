const express = require('express')
const cors = require('cors')
const Anthropic = require('@anthropic-ai/sdk')

const app = express()
const PORT = 3001

app.use(cors())
app.use(express.json({ limit: '20mb' }))

const client = new Anthropic.default({ apiKey: process.env.ANTHROPIC_API_KEY })

// ── Utilidad: scrape básico de una URL ───────────────────────────────────────
async function scrapeUrl(url) {
  const res = await fetch(url, {
    headers: { 'User-Agent': 'Mozilla/5.0 (compatible; BrandingBot/1.0)' },
    signal: AbortSignal.timeout(15000),
  })
  const html = await res.text()
  // Extrae texto limpio (sin tags, scripts ni estilos)
  const clean = html
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s{2,}/g, ' ')
    .trim()
    .slice(0, 8000)
  return { text: clean, url: res.url }
}

// ── Endpoint: POST /api/branding ─────────────────────────────────────────────
app.post('/api/branding', async (req, res) => {
  const { url } = req.body
  if (!url) return res.status(400).json({ error: 'URL requerida' })

  try {
    const { text, url: finalUrl } = await scrapeUrl(url)

    const prompt = `Eres un experto en branding y diseño de identidad de marca.
Analiza el siguiente contenido de la web "${finalUrl}" y genera un branding brief completo y detallado.

CONTENIDO DEL SITIO:
${text}

Responde ÚNICAMENTE con un JSON válido con esta estructura exacta (sin markdown, sin texto adicional):
{
  "nombre": "nombre oficial de la marca",
  "tagline": "slogan o tagline principal",
  "descripcion": "descripción clara de qué hace y para quién (2-3 oraciones)",
  "mision": "declaración de misión (1-2 oraciones)",
  "vision": "declaración de visión a futuro (1-2 oraciones)",
  "valores": ["valor1", "valor2", "valor3", "valor4", "valor5"],
  "propuesta_valor": "qué hace única a esta marca, su ventaja diferencial clara",
  "publico_objetivo": "descripción detallada del cliente ideal (perfil demográfico y psicográfico)",
  "personalidad": ["adjetivo1", "adjetivo2", "adjetivo3", "adjetivo4"],
  "tono_de_voz": "cómo habla la marca: describir el estilo comunicativo con ejemplos de palabras o frases que usaría",
  "paleta_colores": [
    { "nombre": "Color Primario", "hex": "#XXXXXX", "uso": "uso principal" },
    { "nombre": "Color Secundario", "hex": "#XXXXXX", "uso": "uso secundario" },
    { "nombre": "Acento", "hex": "#XXXXXX", "uso": "llamadas a la acción" },
    { "nombre": "Neutro", "hex": "#XXXXXX", "uso": "fondos y texto" }
  ],
  "tipografia": {
    "principal": "nombre de fuente para títulos y su estilo",
    "secundaria": "nombre de fuente para cuerpo de texto",
    "estilo": "descripción del estilo tipográfico general"
  },
  "estilo_visual": "descripción detallada del estilo visual: fotografía, ilustración, iconografía, patrones",
  "palabras_clave": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5", "keyword6"],
  "diferenciadores": ["diferenciador1", "diferenciador2", "diferenciador3"],
  "recomendaciones": [
    "recomendación estratégica 1 para fortalecer la identidad de marca",
    "recomendación estratégica 2",
    "recomendación estratégica 3"
  ]
}`

    const message = await client.messages.create({
      model: 'claude-opus-4-6',
      max_tokens: 2048,
      messages: [{ role: 'user', content: prompt }],
    })

    const raw = message.content[0].text.trim()
    // Extrae JSON aunque Claude agregue algo extra
    const jsonMatch = raw.match(/\{[\s\S]*\}/)
    if (!jsonMatch) throw new Error('Respuesta sin JSON válido')
    const brief = JSON.parse(jsonMatch[0])

    res.json({ ok: true, brief, url: finalUrl })
  } catch (err) {
    console.error(err)
    res.status(500).json({ error: err.message || 'Error generando el brief' })
  }
})

// ── Endpoint: POST /api/json-prompt ─────────────────────────────────────────
app.post('/api/json-prompt', async (req, res) => {
  const { imageBase64, mediaType } = req.body
  if (!imageBase64 || !mediaType) {
    return res.status(400).json({ error: 'Se requiere imageBase64 y mediaType' })
  }

  const systemPrompt = `You are a specialist in analyzing reference images and generating structured JSON prompts for Gemini Nano Banana Pro.

When the user shares a reference image, analyze it in detail and output a ready-to-use JSON prompt that will reproduce the essence of that image as closely as possible.

Follow this JSON structure exactly:

{
  "style": {
    "primary": "photorealistic | cinematic | documentary | illustration | etc.",
    "rendering_quality": "hyperrealistic | detailed | high-resolution",
    "mood": "describe the overall mood/atmosphere"
  },
  "lighting": {
    "type": "natural | studio | dramatic | soft ambient | golden hour | etc.",
    "direction": "front | side | back | overhead | etc.",
    "quality": "hard | soft | diffused | etc.",
    "color_temperature": "warm | cool | neutral | specific Kelvin if applicable"
  },
  "camera": {
    "angle": "eye level | low angle | high angle | dutch angle | etc.",
    "focal_length": "24mm | 50mm | 85mm | 135mm | etc.",
    "depth_of_field": "shallow | deep | bokeh description",
    "aperture": "f/1.4 | f/2.8 | f/8 | etc.",
    "composition": "rule of thirds | centered | golden ratio | etc."
  },
  "subject": {
    "description": "detailed subject description",
    "position": "placement in frame",
    "expression_or_state": "if person/animal — expression, pose, action",
    "clothing_or_texture": "if applicable"
  },
  "environment": {
    "setting": "location/background description",
    "time_of_day": "dawn | morning | midday | golden hour | dusk | night",
    "season": "spring | summer | autumn | winter | tropical | etc.",
    "atmosphere": "fog | haze | clear | rain | dust | etc."
  },
  "colors": {
    "palette": ["primary color", "secondary color", "accent color"],
    "saturation": "muted | natural | vibrant | desaturated",
    "contrast": "low | medium | high | cinematic"
  },
  "materials_and_textures": {
    "surfaces": "description of key surface textures",
    "details": "specific material properties visible"
  },
  "quality_keywords": ["hyperrealistic", "photographic quality", "natural lighting", "authentic textures"],
  "avoid": ["digital artifacts", "unrealistic proportions", "oversaturated colors"],
  "reference_style": "National Geographic | Annie Leibovitz | etc. — closest photographic reference"
}

Respond ONLY with the JSON object, no markdown, no extra text. Make it as detailed and specific as possible based on what you observe in the image.`

  try {
    const message = await client.messages.create({
      model: 'claude-opus-4-6',
      max_tokens: 2048,
      system: systemPrompt,
      messages: [{
        role: 'user',
        content: [{
          type: 'image',
          source: {
            type: 'base64',
            media_type: mediaType,
            data: imageBase64,
          }
        }, {
          type: 'text',
          text: 'Analyze this reference image and generate the JSON prompt for Nano Banana Pro.'
        }]
      }]
    })

    const raw = message.content[0].text.trim()
    const jsonMatch = raw.match(/\{[\s\S]*\}/)
    if (!jsonMatch) throw new Error('No se pudo extraer JSON de la respuesta')
    const jsonPrompt = JSON.parse(jsonMatch[0])

    res.json({ ok: true, prompt: jsonPrompt })
  } catch (err) {
    console.error(err)
    res.status(500).json({ error: err.message || 'Error generando el prompt' })
  }
})

app.get('/api/health', (req, res) => res.json({ status: 'ok' }))

app.listen(PORT, () => console.log(`API corriendo en http://localhost:${PORT}`))
