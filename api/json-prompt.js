const Anthropic = require('@anthropic-ai/sdk')

const client = new Anthropic.default({ apiKey: process.env.ANTHROPIC_API_KEY })

const SYSTEM_PROMPT = `You are a specialist in analyzing reference images and generating structured JSON prompts for Gemini Nano Banana Pro.

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

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')

  if (req.method === 'OPTIONS') return res.status(200).end()
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' })

  const { imageBase64, mediaType } = req.body
  if (!imageBase64 || !mediaType) {
    return res.status(400).json({ error: 'imageBase64 and mediaType are required' })
  }

  try {
    const message = await client.messages.create({
      model: 'claude-opus-4-6',
      max_tokens: 2048,
      system: SYSTEM_PROMPT,
      messages: [{
        role: 'user',
        content: [
          { type: 'image', source: { type: 'base64', media_type: mediaType, data: imageBase64 } },
          { type: 'text', text: 'Analyze this reference image and generate the JSON prompt for Nano Banana Pro.' }
        ]
      }]
    })

    const raw = message.content[0].text.trim()
    const jsonMatch = raw.match(/\{[\s\S]*\}/)
    if (!jsonMatch) throw new Error('Could not extract JSON from response')
    const prompt = JSON.parse(jsonMatch[0])

    res.json({ ok: true, prompt })
  } catch (err) {
    console.error(err)
    res.status(500).json({ error: err.message || 'Error generating prompt' })
  }
}
