export function filterUnassigned(obj) {
  return Object.fromEntries(
    Object.entries(obj).filter(
      ([_, v]) => v !== "" && v !== null && v !== undefined,
    ),
  )
}

export function isoToHumanReadable(iso) {
  // Function to pad single digit numbers with a leading zero
  const padZero = (number: number) => (number < 10 ? "0" : "") + number

  // Extract date and time components from the provided ISO string
  const [datePart, timePart] = iso.split("T")
  const [year, month, day] = datePart.split("-")
  const [hour, minute] = timePart.split(":")

  // Format date as YYYY-MM-DD
  const formattedDate = `${year}-${padZero(parseInt(month))}-${padZero(
    parseInt(day),
  )}`

  // Format time as H:i
  const formattedTime = `${padZero(parseInt(hour))}:${padZero(
    parseInt(minute),
  )}`

  const formattedResponse = {
    date: formattedDate,
    time: formattedTime,
  }
  return formattedResponse
}
