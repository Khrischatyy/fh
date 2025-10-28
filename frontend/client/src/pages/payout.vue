<template>
  <div>
    <NuxtLayout
        @toggleSideMenu="toggleSideMenu"
        title="Payouts"
        class="text-white flex flex-col min-h-screen"
        name="dashboard"
    >
      <Spinner :is-loading="isLoading" class="mt-4"/>
      <div class="container mx-auto p-4">
        <div v-if="!isLoading && user.payment_gateway" class="mb-4">
          <p class="text-gray-400">Connected account</p>
          <p class="text-white>">{{ user.payment_gateway == 'square' ? 'Square account' : 'Stripe account' }}</p>
        </div>
        <div
            v-if="
            stripeAccountId &&
            stripeAccountData &&
            Object.keys(stripeAccountData).length > 0
          "
            class="flex flex-col mt-4 justify-start items-start border border-white border-opacity-10 rounded-[10px] p-4"
        >
          <div class="text-xl">
            <p class="text-gray-400 mb-1.5">Balance:</p>
            <p class="text-sm mb-1.5">
              Total balance: ${{ balance.instant_available[0]?.amount / 100 }}
            </p>
            <p v-if="balance?.pending?.length > 0" class="text-sm mb-1.5">
              Future payouts: ${{ balance.pending[0]?.amount / 100 }}
            </p>
            <p v-if="balance?.available?.length > 0" class="text-sm mb-1.5">
              In transit to bank: ${{ balance.available[0]?.amount / 100 }}
            </p>
            <p
                v-if="balance?.refund_and_dispute_prefunding?.length > 0"
                class="text-sm mb-1.5"
            >
              Refund and Dispute Prefunding:
              {{ balance.refund_and_dispute_prefunding[0]?.amount / 100 }}
            </p>
            <a
                v-if="stripeAccountId"
                target="_blank"
                :href="`https://connect.stripe.com/app/express#${stripeAccountId}/overview`"
                class="border-white border mt-5 mb-5 block text-white text-sm py-2 px-4 rounded-[10px] hover:opacity-80"
            >
              Go to Stripe Dashboard
            </a>
          </div>
          <div class="text-xl">
            <p class="text-gray-400 mt-2 mb-2">
              Payouts
              {{ stripeAccountData?.payouts_enabled ? "Enabled" : "Disabled" }}
            </p>
            <div
                v-if="stripeAccountData?.external_accounts?.total_count > 0"
                class="text-white text-sm font-bold mb-2 flex justify-center items-center"
            >
              <IconCredit class="w-6 h-6 mr-2"/>
              {{ stripeAccountData?.external_accounts?.data[0]?.bank_name }}
              {{ stripeAccountData?.external_accounts?.data[0]?.last4 }}
            </div>
            <p v-if="stripeAccountData?.payouts_enabled" class="text-sm">
              Payout interval:
              {{ stripeAccountData?.settings?.payouts?.schedule?.interval }}
            </p>
            <button
                v-if="stripeAccountData?.payouts_enabled"
                @click="createAccountLink"
                class="border-white border mt-5 mb-5 text-white text-sm py-2 px-4 rounded-[10px] hover:opacity-80"
            >
              Update Information
            </button>
          </div>
        </div>
        <div
            v-if="
            stripeAccountId &&
            stripeAccountData &&
            Object.keys(stripeAccountData).length > 0 &&
            (!stripeAccountData.details_submitted ||
              !stripeAccountData.payouts_enabled)
          "
            class="flex mt-5 justify-between items-center border border-white border-opacity-10 rounded-[10px] p-4"
        >
          <div class="text-xl">
            <p class="text-red-400 mb-5">Requires attention</p>
            <p class="text-white font-bold">
              Your account is missing some information to make payouts.
            </p>
          </div>
          <button
              @click="createAccountLink"
              class="bg-white text-gray-800 font-bold py-2 px-4 rounded hover:bg-gray-400"
          >
            Update information
          </button>
        </div>
        <div
            v-if="user && !user.stripe_account_id && !user.payment_gateway"
            class="text-center mt-4 flex flex-col items-center justify-center text-gray-400"
        >
          <p class="mb-5">
            Please connect your Stripe or Square account to manage payouts.
          </p>
          <div class="flex flex-wrap gap-5 justify-center items-center">
            <button
                @click="createAccount"
                class="bg-white w-48 justify-center flex gap-2 text-gray-800 font-bold py-2 px-4 rounded hover:bg-gray-400"
            >
              <IconStripe class="h-6"/>
            </button>
            <button
                @click="connectSquareAccount"
                class="bg-white w-48 justify-center text-gray-800 flex gap-2 font-bold py-2 px-4 rounded hover:bg-gray-400"
            >
              <IconSquare class="h-6"/>
            </button>
          </div>
        </div>


        <div v-if="!isLoading && payouts.length > 0" class="mt-4">
          <table class="min-w-full bg-white">
            <thead>
            <tr>
              <th class="py-2 px-4 border-b">Payout ID</th>
              <th class="py-2 px-4 border-b">Amount</th>
              <th class="py-2 px-4 border-b">Status</th>
              <th class="py-2 px-4 border-b">Created At</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="payout in payouts" :key="payout.id">
              <td class="py-2 px-4 border-b">{{ payout.id }}</td>
              <td class="py-2 px-4 border-b">{{ payout.amount / 100 }}</td>
              <td class="py-2 px-4 border-b">{{ payout.status }}</td>
              <td class="py-2 px-4 border-b">
                {{ new Date(payout.created_at).toLocaleString() }}
              </td>
            </tr>
            </tbody>
          </table>
        </div>
      </div>
    </NuxtLayout>
  </div>
</template>

<script setup lang="ts">
import {ref, onMounted, type Ref} from "vue"
import {useFetch, useRuntimeConfig} from "#app"
import {IconCredit, IconSquare, IconStripe, Spinner} from "~/src/shared/ui/common"
import {useApi} from "../lib/api"
import {useSessionStore} from "../entities/Session"
import {storeToRefs} from "pinia"
import {navigateTo} from "nuxt/app";

type StripAccountDataType = {
  id: string
  object: string
  business_profile: {
    annual_revenue: null
    estimated_worker_count: null
    mcc: string
    name: string
    support_address: null
    support_email: null
    support_phone: null
    support_url: null
    url: string
  }
  capabilities: {
    card_payments: string
    transfers: string
  }
  charges_enabled: boolean
  controller: {
    fees: {
      payer: string
    }
    is_controller: boolean
    losses: {
      payments: string
    }
    requirement_collection: string
    stripe_dashboard: {
      type: string
    }
    type: string
  }
  country: string
  created: number
  default_currency: string
  details_submitted: boolean
  email: string
  external_accounts: {
    object: string
    data: [
      {
        id: string
        object: string
        account: string
        account_holder_name: null
        account_holder_type: null
        account_type: null
        available_payout_methods: string[]
        bank_name: string
        country: string
        currency: string
        default_for_currency: boolean
        financial_account: null
        fingerprint: string
        future_requirements: {
          currently_due: string[]
          errors: string[]
          past_due: string[]
          pending_verification: string[]
        }
        last4: string
        metadata: string[]
        requirements: {
          currently_due: string[]
          errors: string[]
          past_due: string[]
          pending_verification: string[]
        }
        routing_number: string
        status: string
      },
    ]
    has_more: boolean
    total_count: number
    url: string
  }
  future_requirements: {
    alternatives: string[]
    current_deadline: null
    currently_due: string[]
    disabled_reason: null
    errors: string[]
    eventually_due: string[]
    past_due: string[]
    pending_verification: string[]
  }
  login_links: {
    object: string
    data: string[]
    has_more: boolean
    total_count: number
    url: string
  }
  metadata: string[]
  payouts_enabled: boolean
}

type SourceTypes = {
  card: number
}

type BalanceDetail = {
  amount: number
  currency: string
  source_types?: SourceTypes
}

type Balance = {
  object: string
  available: BalanceDetail[]
  instant_available: BalanceDetail[]
  livemode: boolean
  pending: BalanceDetail[]
  refund_and_dispute_prefunding: BalanceDetail[]
}

type BalanceResponse = {
  data: Balance
}

const sideMenuRef = ref()
const isLoading = ref(true)
const balance: Ref<Balance> = ref({
  object: "",
  available: [],
  instant_available: [],
  livemode: false,
  pending: [],
  refund_and_dispute_prefunding: [],
} as Balance)
const payouts = ref([])
const stripeAccountId = ref(null)
const stripeAccountData: Ref<StripAccountDataType> = ref(
    {} as StripAccountDataType,
)
const session = useSessionStore()
const {user} = storeToRefs(session)

const fetchBalance = async () => {
  try {
    const {fetch: fetchBalance} = useApi<BalanceResponse>({
      url: "/user/payment/stripe/balance",
      auth: true,
    })

    const response = (await fetchBalance()) || ({data: {}} as BalanceResponse)

    balance.value = response.data
  } catch (error) {
    console.error("Failed to fetch balance:", error)
  }
}

const connectSquareAccount = async () => {
  isLoading.value = true
  try {
    const {fetch: getLink} = useApi({
      url: "/user/payment/square/redirect",
      auth: true,
    })

    await getLink().then((res) => {
      console.log(res)
      if (res?.data?.url) {
        window.location.href = res?.data?.url
      }
    })
  } finally {
    isLoading.value = false
  }
}

const createAccount = async () => {
  isLoading.value = true
  try {
    const {post} = useApi({
      url: "/user/payment/stripe/create-account",
      auth: true,
    })

    const response = await post({})

    stripeAccountId.value = response.data.account_id
    isLoading.value = false
    createAccountLink()
  } catch (error) {
    console.error("Failed to create Stripe account:", error)
  }
}

const createAccountLink = async () => {
  try {
    isLoading.value = true
    const {fetch: getLink} = useApi({
      url: "/user/payment/stripe/refresh?account_id=" + stripeAccountId.value,
      auth: true,
    })

    await getLink().then((res) => {
      if (res.data.url) {
        window.location.href = res.data.url
      }
    })
  } catch (error) {
    console.error("Failed to create account link:", error)
    isLoading.value = false
  }
}

const fetchPayouts = async () => {
  // Implement fetchPayouts logic if needed
}

const fetchStripeAccountData = async () => {
  try {
    isLoading.value = true
    const {fetch: getAccountData} = useApi({
      url: "/user/payment/account/retrieve",
      auth: true,
    })

    getAccountData().then((res) => {
      stripeAccountData.value = res.data
      isLoading.value = false
    })
  } catch (error) {
    console.error("Failed to fetch Stripe account ID:", error)
    isLoading.value = false
  }
}

const toggleSideMenu = () => {
  if (sideMenuRef.value) {
    sideMenuRef.value.toggleMenu()
  }
}

onMounted(async () => {
  if (!user?.value?.company) {
    await session.fetchUserInfo()
  }
  if (!user.value.company) {
    if (process.client) {
      navigateTo("/create")
    }
  }
  isLoading.value = false
  if (user.value && user.value.stripe_account_id) {
    stripeAccountId.value = user.value.stripe_account_id
    await fetchStripeAccountData()
    await fetchBalance()
  }
})
</script>
