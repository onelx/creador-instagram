const Anthropic = require('@anthropic-ai/sdk')

const client = new Anthropic.default({ apiKey: process.env.ANTHROPIC_API_KEY })

const JSON_STRUCTURE = `{
  "style": {
    "primary": "photorealistic | cinematic | illustration | etc.",
    "rendering_quality": "hyperrealistic | detailed | high-resolution",
    "mood": "overall mood/atmosphere"
  },
  "lighting": {
    "type": "natural | studio | dramatic | soft ambient | golden hour | etc.",
    "direction": "front | side | back | overhead | etc.",
    "quality": "hard | soft | diffused",
    "color_temperature": "warm | cool | neutral"
  },
  "camera": {
    "angle": "eye level | low angle | high angle | etc.",
    "focal_length": "24mm | 50mm | 85mm | 135mm | etc.",
    "depth_of_field": "shallow | deep | bokeh description",
    "aperture": "f/1.4 | f/2.8 | f/8 | etc.",
    "composition": "rule of thirds | centered | golden ratio | etc."
  },
  "subject": {
    "description": "detailed subject description",
    "position": "placement in frame",
    "expression_or_state": "expression, pose, action",
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
  "quality_keywords": ["hyperrealistic", "photographic quality", "natural lighting"],
  "avoid": ["digital artifacts", "unrealistic proportions"],
  "reference_style": "closest photographic reference style"
}`

const SINGLE_PROMPT = `You are a specialist in analyzing reference images and generating structured JSON prompts for Gemini Nano Banana Pro.

Analyze the image in detail and output a ready-to-use JSON prompt that reproduces its visual essence as closely as possible.

Use this JSON structure exactly:
${JSON_STRUCTURE}

Respond ONLY with the JSON object, no markdown, no extra text.`

const MIX_PROMPT = `You are a specialist in combining visual references into JSON prompts for Gemini Nano Banana Pro.

You will receive TWO images:
- IMAGE 1 (SUBJECT): Extract from this image — subject description, composition, camera angle, environment, setting, depth of field. This is what the final image will depict.
- IMAGE 2 (COLOR PALETTE): Extract from this image ONLY — color palette, color tones, saturation level, contrast style, color temperature, lighting mood. These colors will be applied to the subject from Image 1.

Create a single combined JSON where:
- subject, composition, camera, environment → come from IMAGE 1
- colors.palette, colors.saturation, colors.contrast, lighting.color_temperature, style.mood → come from IMAGE 2

Use this JSON structure exactly:
${JSON_STRUCTURE}

Respond ONLY with the JSON object, no markdown, no extra text.`

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')

  if (req.method === 'OPTIONS') return res.status(200).end()
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' })

  const { imageBase64, mediaType, mode, paletteBase64 } = req.body
  if (!imageBase64 || !mediaType) {
    return res.status(400).json({ error: 'imageBase64 and mediaType are required' })
  }

  const isMix = mode === 'mix' && paletteBase64

  try {
    let content

    if (isMix) {
      // Two images: subject first, palette second
      content = [
        { type: 'text', text: 'IMAGE 1 — SUBJECT (extract subject, composition, camera, environment from this):' },
        { type: 'image', source: { type: 'base64', media_type: mediaType, data: imageBase64 } },
        { type: 'text', text: 'IMAGE 2 — COLOR PALETTE (extract ONLY colors, saturation, tones, contrast from this):' },
        { type: 'image', source: { type: 'base64', media_type: 'image/jpeg', data: paletteBase64 } },
        { type: 'text', text: 'Now combine them: subject from Image 1, colors from Image 2. Generate the JSON.' }
      ]
    } else {
      content = [
        { type: 'image', source: { type: 'base64', media_type: mediaType, data: imageBase64 } },
        { type: 'text', text: 'Analyze this reference image and generate the JSON prompt for Nano Banana Pro.' }
      ]
    }

    const message = await client.messages.create({
      model: 'claude-opus-4-5',
      max_tokens: 2048,
      system: isMix ? MIX_PROMPT : SINGLE_PROMPT,
      messages: [{ role: 'user', content }]
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
