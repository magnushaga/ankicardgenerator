export async function generatePKCEChallenge(): Promise<{ codeVerifier: string; codeChallenge: string }> {
  // Generate code verifier
  const codeVerifier = generateRandomString(128)
  
  // Generate code challenge
  const codeChallenge = await generateCodeChallenge(codeVerifier)
  
  return {
    codeVerifier,
    codeChallenge
  }
}

function generateRandomString(length: number): string {
  const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  const values = crypto.getRandomValues(new Uint8Array(length))
  return values.reduce((acc, x) => acc + possible[x % possible.length], '')
}

async function generateCodeChallenge(verifier: string): Promise<string> {
  const hash = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(verifier))
  return base64URLEncode(hash)
}

function base64URLEncode(buffer: ArrayBuffer): string {
  const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer)))
  return base64
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '')
} 