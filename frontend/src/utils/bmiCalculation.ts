// Same formula, rounding and WHO categories as the backend
// (backend/app/services/input_preprocessing_service.py). The backend's value is
// the one used by the models; this is only a live preview while typing.

export const MODEL_BMI_RANGE = { min: 12, max: 70 } as const

export function calculateBmi(heightCm: number, weightKg: number): number {
  const heightM = heightCm / 100
  return Math.round((weightKg / (heightM * heightM)) * 10) / 10
}

export function whoBmiCategory(bmi: number): string {
  if (bmi < 18.5) return 'Underweight'
  if (bmi < 25) return 'Healthy weight'
  if (bmi < 30) return 'Overweight'
  return 'Obesity'
}

export function isBmiInModelRange(bmi: number): boolean {
  return bmi >= MODEL_BMI_RANGE.min && bmi <= MODEL_BMI_RANGE.max
}
