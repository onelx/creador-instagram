const Anthropic = require('@anthropic-ai/sdk')

const client = new Anthropic.default({ apiKey: process.env.ANTHROPIC_API_KEY })

async function scrapeUrl(url) {
  const res = await fetch(url, {
    headers: { 'User-Agent': 'Mozilla/5.0 (compatible; BrandingBot/1.0)' },
    signal: AbortSignal.timeout(15000),
  })
  const html = await res.text()
  const clean = html
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s{2,}/g, ' ')
    .trim()
    .slice(0, 8000)
  return { text: clean, url: res.url }
}

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')

  if (req.method === 'OPTIONS') return res.status(200).end()
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' })

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
  "propuesta_valor": "qué hace única a esta marca",
  "publico_objetivo": "descripción del cliente ideal",
  "personalidad": ["adjetivo1", "adjetivo2", "adjetivo3", "adjetivo4"],
  "tono_de_voz": "cómo habla la marca",
  "paleta_colores": [
    { "nombre": "Color Primario", "hex": "#XXXXXX", "uso": "uso principal" },
    { "nombre": "Color Secundario", "hex": "#XXXXXX", "uso": "uso secundario" },
    { "nombre": "Acento", "hex": "#XXXXXX", "uso": "llamadas a la acción" },
    { "nombre": "Neutro", "hex": "#XXXXXX", "uso": "fondos y texto" }
  ],
  "tipografia": {
    "principal": "nombre de fuente para títulos",
    "secundaria": "nombre de fuente para cuerpo",
    "estilo": "descripción del estilo tipográfico"
  },
  "estilo_visual": "descripción del estilo visual",
  "palabras_clave": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
  "diferenciadores": ["diferenciador1", "diferenciador2", "diferenciador3"],
  "recomendaciones": ["recomendación 1", "recomendación 2", "recomendación 3"]
}`

    const message = await client.messages.create({
      model: 'claude-opus-4-6',
      max_tokens: 2048,
      messages: [{ role: 'user', content: prompt }],
    })

    const raw = message.content[0].text.trim()
    const jsonMatch = raw.match(/\{[\s\S]*\}/)
    if (!jsonMatch) throw new Error('Respuesta sin JSON válido')
    const brief = JSON.parse(jsonMatch[0])

    res.json({ ok: true, brief, url: finalUrl })
  } catch (err) {
    console.error(err)
    res.status(500).json({ error: err.message || 'Error generando el brief' })
  }
}
