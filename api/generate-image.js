module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')

  if (req.method === 'OPTIONS') return res.status(200).end()
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' })

  const apiKey = process.env.GEMINI_API_KEY
  if (!apiKey) {
    return res.status(500).json({ error: 'GEMINI_API_KEY not configured on server' })
  }

  const { prompt } = req.body
  if (!prompt) {
    return res.status(400).json({ error: 'prompt is required' })
  }

  try {
    const textPrompt = buildTextPrompt(prompt)

    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key=${apiKey}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          instances: [{ prompt: textPrompt }],
          parameters: {
            sampleCount: 1,
            aspectRatio: '1:1',
            safetyFilterLevel: 'block_few',
            personGeneration: 'allow_adult'
          }
        }),
        signal: AbortSignal.timeout(60000)
      }
    )

    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      throw new Error(err.error?.message || `Gemini error ${response.status}`)
    }

    const data = await response.json()
    const b64 = data.predictions?.[0]?.bytesBase64Encoded
    if (!b64) throw new Error('No image returned from Gemini')

    res.json({
      ok: true,
      imageBase64: b64,
      mimeType: 'image/png',
      prompt: textPrompt
    })
  } catch (err) {
    console.error(err)
    res.status(500).json({ error: err.message || 'Error generating image' })
  }
}

function buildTextPrompt(json) {
  const parts = []

  if (json.style?.primary) parts.push(json.style.primary)
  if (json.style?.rendering_quality) parts.push(json.style.rendering_quality)

  if (json.subject?.description) parts.push(json.subject.description)
  if (json.subject?.expression_or_state) parts.push(json.subject.expression_or_state)
  if (json.subject?.clothing_or_texture) parts.push(json.subject.clothing_or_texture)

  if (json.environment?.setting) parts.push(json.environment.setting)
  if (json.environment?.time_of_day) parts.push(`time of day: ${json.environment.time_of_day}`)
  if (json.environment?.atmosphere) parts.push(`atmosphere: ${json.environment.atmosphere}`)
  if (json.environment?.season) parts.push(json.environment.season)

  if (json.lighting?.type) parts.push(`${json.lighting.type} lighting`)
  if (json.lighting?.direction) parts.push(`light from ${json.lighting.direction}`)
  if (json.lighting?.color_temperature) parts.push(json.lighting.color_temperature)

  if (json.camera?.angle) parts.push(`${json.camera.angle} angle`)
  if (json.camera?.focal_length) parts.push(`${json.camera.focal_length} lens`)
  if (json.camera?.depth_of_field) parts.push(json.camera.depth_of_field)
  if (json.camera?.composition) parts.push(json.camera.composition)

  if (json.colors?.palette?.length) parts.push(`color palette: ${json.colors.palette.join(', ')}`)
  if (json.colors?.saturation) parts.push(`${json.colors.saturation} saturation`)
  if (json.colors?.contrast) parts.push(`${json.colors.contrast} contrast`)

  if (json.materials_and_textures?.surfaces) parts.push(json.materials_and_textures.surfaces)

  if (json.style?.mood) parts.push(`mood: ${json.style.mood}`)

  if (json.quality_keywords?.length) parts.push(json.quality_keywords.join(', '))
  if (json.reference_style) parts.push(`in the style of ${json.reference_style}`)

  if (json.avoid?.length) parts.push(`avoid: ${json.avoid.join(', ')}`)

  return parts.filter(Boolean).join(', ')
}
