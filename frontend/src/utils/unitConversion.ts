const CM_PER_INCH = 2.54
const INCHES_PER_FOOT = 12
const KG_PER_POUND = 0.45359237

export function feetInchesToCm(feet: number, inches: number): number {
  return (feet * INCHES_PER_FOOT + inches) * CM_PER_INCH
}

export function cmToFeetInches(cm: number): { feet: number; inches: number } {
  const totalInches = cm / CM_PER_INCH
  let feet = Math.floor(totalInches / INCHES_PER_FOOT)
  let inches = Math.round(totalInches - feet * INCHES_PER_FOOT)
  if (inches === INCHES_PER_FOOT) {
    feet += 1
    inches = 0
  }
  return { feet, inches }
}

export function poundsToKg(pounds: number): number {
  return pounds * KG_PER_POUND
}

export function kgToPounds(kg: number): number {
  return kg / KG_PER_POUND
}

/** Parse a form value; empty or non-numeric text gives null. */
export function parseNumber(text: string): number | null {
  const trimmed = text.trim().replace(',', '.')
  if (trimmed === '') return null
  const value = Number(trimmed)
  return Number.isFinite(value) ? value : null
}
