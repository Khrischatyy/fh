export enum BookingStatus {
  Pending = 1,
  Paid = 2,
  Cancelled = 3,
  Expired = 4,
}

export const STATUSES = {
  1: "Pending",
  2: "Paid",
  3: "Cancelled",
  4: "Expired",
}

export const STATUS_COLOR = {
  1: "yellow",
  2: "green",
  3: "red",
  4: "gray",
}

export const getStatus = (status: number) =>
  STATUSES[status as keyof typeof STATUSES]
export const getColor = (status: number) =>
  STATUS_COLOR[status as keyof typeof STATUS_COLOR]

export const getColorHex = (color: string) => {
  switch (color) {
    case "yellow":
      return "#FD9302"
    case "green":
      return "#66AA3B"
    case "red":
      return "#E75032"
    case "gray":
      return "#F3F5FD"
    default:
      return "#F3F5FD"
  }
}

export const getRatingColor = (rating: number) => {
  if (rating >= 4) {
    return "green"
  } else if (rating >= 3) {
    return "yellow"
  } else {
    return "red"
  }
}

export const phoneNormalizer = (phone: string) => {
  return phone.replace(/(\d{3})(\d{3})(\d{4})/, "($1) $2-$3")
}
