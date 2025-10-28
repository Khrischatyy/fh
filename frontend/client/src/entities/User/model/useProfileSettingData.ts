import { getUserProfileSettingData } from "../api"
export function useProfileSettingData() {
  const {
    data: userProfileSettingData,
    pending: isLoading,
    refresh: refreshProfileSettingData,
  } = getUserProfileSettingData()

  const getProfileSettingData = async () => {
    try {
      await refreshProfileSettingData()
    } catch (e) {
      console.error(e)
    }
  }

  return {
    userProfileSettingData,
    isLoading,
    getProfileSettingData,
  }
}
