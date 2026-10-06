function parseSseBlock(block, onEvent) {
  let eventName = 'message'
  const dataLines = []

  for (const line of block.split(/\r?\n/)) {
    if (line.startsWith(':')) continue
    const separator = line.indexOf(':')
    const field = separator === -1 ? line : line.slice(0, separator)
    const value = separator === -1 ? '' : line.slice(separator + 1).replace(/^ /, '')

    if (field === 'event') eventName = value
    if (field === 'data') dataLines.push(value)
  }

  if (dataLines.length === 0) return

  const rawData = dataLines.join('\n')
  let payload
  try {
    payload = JSON.parse(rawData)
  } catch {
    payload = { data: rawData }
  }

  onEvent({ name: eventName, payload })
}

export async function streamAgentReply(prompt, { signal, onEvent }) {
  const baseUrl = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')
  const response = await fetch(`${baseUrl}/agent/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream' },
    body: JSON.stringify(prompt),
    signal,
  })

  if (!response.ok) {
    const responseText = await response.text()
    throw new Error(responseText || `请求失败（HTTP ${response.status}）`)
  }
  if (!response.body) throw new Error('浏览器无法读取服务器发送事件流。')

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    buffer += decoder.decode(value || new Uint8Array(), { stream: !done }).replace(/\r\n/g, '\n')

    let boundary = buffer.indexOf('\n\n')
    while (boundary !== -1) {
      parseSseBlock(buffer.slice(0, boundary), onEvent)
      buffer = buffer.slice(boundary + 2)
      boundary = buffer.indexOf('\n\n')
    }

    if (done) break
  }

  if (buffer.trim()) parseSseBlock(buffer, onEvent)
}
