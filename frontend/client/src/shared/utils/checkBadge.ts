export function isBadgeTaken(badgeId: number, takenBadges: Array<{ id: number }>): boolean {
    return takenBadges.some(takenBadge => takenBadge.id === badgeId);
}
