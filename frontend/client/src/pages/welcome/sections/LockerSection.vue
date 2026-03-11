<template>
  <section class="bg-[#f7f7f7]">
    <div class="container mx-auto px-4 py-12 md:py-28">
      <!-- Header -->
      <div class="mb-12">
        <h2 class="text-[#181818] text-4xl md:text-5xl lg:text-6xl font-black mb-6">
          Protect Your Studio Equipment 24/7
        </h2>
        <p class="text-black text-xl md:text-2xl opacity-60 lg:w-2/3">
          Automatically lock and unlock studio Macs based on your booking schedule.
          When artists need extra time, they pay - and you get compensated instantly.
        </p>
      </div>

      <!-- Two Column Layout -->
      <div class="grid md:grid-cols-2 gap-8 lg:gap-12">
        <!-- Left Column: Features -->
        <div class="space-y-6">
          <!-- Feature 1 -->
          <div class="bg-white rounded-2xl p-6 shadow-sm">
            <div class="flex items-start gap-4">
              <div class="flex-shrink-0 w-12 h-12 bg-black rounded-full flex items-center justify-center">
                <img src="../../../shared/assets/image/lockin.svg" alt="Lock" class="w-6 h-6" />
              </div>
              <div>
                <h3 class="text-xl font-bold text-[#181818] mb-2">Automatic Locking</h3>
                <p class="text-black opacity-60">
                  Your studio Macs lock automatically when there's no active booking.
                  No manual intervention needed.
                </p>
              </div>
            </div>
          </div>

          <!-- Feature 2 -->
          <div class="bg-white rounded-2xl p-6 shadow-sm">
            <div class="flex items-start gap-4">
              <div class="flex-shrink-0 w-12 h-12 bg-black rounded-full flex items-center justify-center">
                <img src="../../../shared/assets/image/lockin.svg" alt="Lock" class="w-6 h-6" />
              </div>
              <div>
                <h3 class="text-xl font-bold text-[#181818] mb-2">Token-Based Access</h3>
                <p class="text-black opacity-60">
                  Simple registration with a studio token. No email or password required.
                </p>
              </div>
            </div>
          </div>

          <!-- Feature 3 -->
          <div class="bg-white rounded-2xl p-6 shadow-sm">
            <div class="flex items-start gap-4">
              <div class="flex-shrink-0 w-12 h-12 bg-black rounded-full flex items-center justify-center">
                <img src="../../../shared/assets/image/lockin.svg" alt="Lock" class="w-6 h-6" />
              </div>
              <div>
                <h3 class="text-xl font-bold text-[#181818] mb-2">Real-Time Sync</h3>
                <p class="text-black opacity-60">
                  Locks sync instantly with your booking schedule. Artists get access only during their booked time.
                </p>
              </div>
            </div>
          </div>

          <!-- Feature 4 -->
          <div class="bg-white rounded-2xl p-6 shadow-sm">
            <div class="flex items-start gap-4">
              <div class="flex-shrink-0 w-12 h-12 bg-black rounded-full flex items-center justify-center">
                <img src="../../../shared/assets/image/lockin.svg" alt="Lock" class="w-6 h-6" />
              </div>
              <div>
                <h3 class="text-xl font-bold text-[#181818] mb-2">Menu Bar Control</h3>
                <p class="text-black opacity-60">
                  Clean menu bar app with custom Funny How branding. Check status and manage devices easily.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: CTAs -->
        <div class="space-y-6">
          <!-- Download CTA -->
          <div class="bg-black text-white rounded-2xl p-8">
            <h3 class="text-2xl md:text-3xl font-bold mb-4">
              Download for macOS
            </h3>
            <p class="opacity-80 mb-6">
              Protect your studio equipment with the Funny How Locker app.
              Free for all studio owners.
            </p>
            <a
              href="https://github.com/anthropics/funny-how/releases/latest/download/FunnyHowLocker.dmg"
              class="inline-block bg-white text-black font-bold py-3 px-8 rounded-full hover:bg-gray-100 transition-colors"
            >
              Download Now
            </a>
            <p class="text-sm opacity-60 mt-4">
              Requires macOS 11.0 or later
            </p>
          </div>

          <!-- Manage Devices CTA -->
          <div class="bg-gradient-to-br from-purple-600 to-blue-600 text-white rounded-2xl p-8">
            <h3 class="text-2xl md:text-3xl font-bold mb-4">
              Manage Your Devices
            </h3>
            <p class="opacity-90 mb-6">
              View all registered devices, generate access tokens, and monitor lock status from your dashboard.
            </p>
            <a
              href="/settings/devices"
              class="inline-block bg-white text-purple-600 font-bold py-3 px-8 rounded-full hover:bg-gray-100 transition-colors"
            >
              Go to Dashboard
            </a>
          </div>

          <!-- Info Box -->
          <div class="bg-blue-50 border-2 border-blue-200 rounded-2xl p-6">
            <div class="flex items-start gap-3">
              <div class="flex-shrink-0 text-2xl">ℹ️</div>
              <div>
                <h4 class="font-bold text-[#181818] mb-2">How It Works</h4>
                <p class="text-sm text-black opacity-70">
                  Install the app on your studio Macs, register with your studio token,
                  and the app handles the rest. Devices lock automatically based on your booking schedule.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
// No logic needed for this static section
</script>

<style scoped lang="scss">
// Component-specific styles if needed
</style>
