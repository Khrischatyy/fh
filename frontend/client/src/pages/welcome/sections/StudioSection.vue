<script setup lang="ts">

</script>

<template>
  <section
      class="bg-[#F8F8F8]">
    <div class="container mx-auto px-4 py-12 md:py-28">
      <div class="flex flex-col gap-12">
        <!-- Header Section -->
        <div class="text-center md:text-left">
          <h2 class="text-[#181818] text-4xl md:text-5xl lg:text-6xl font-black mb-6">Find Your Best Studio</h2>
          <p class="text-black text-xl md:text-2xl opacity-60 lg:w-1/2">
            We know how hard it is to fine a studio you will vibe at
            That is why we offer multiple filters yo choose best match
          </p>
        </div>


        <div class="flex flex-col lg:flex-row items-center gap-12">
          <!-- Image Section -->
          <div class="w-full lg:w-1/2 relative">
            <img class="w-full h-auto" src="@/public/landing/studio_1.png"
                 alt="Feature Image 1"/>
          </div>

          <!-- Feature Descriptions -->
          <div class="w-full lg:w-1/2 space-y-6">
            <!-- Feature 1 -->
            <div class="bg-[#f7f7f7] rounded-2xl p-3">
              <h3 class="text-black text-2xl md:text-3xl font-black mb-3">Search by address, name or even rating</h3>
              <p class="text-black text-lg md:text-xl opacity-50">Everything counts, find what suits you</p>
            </div>

            <!-- Feature 2 -->
            <div class="bg-[#f7f7f7] rounded-2xl p-3">
              <h3 class="text-black text-2xl md:text-3xl font-black mb-3">See what studio offers, working hours and
                prices</h3>
              <p class="text-black text-lg md:text-xl opacity-50">Detailed description of working hours and prices</p>
            </div>

            <!-- Feature 3 -->
            <div class="bg-[#f7f7f7] rounded-2xl p-3">
              <h3 class="text-black text-2xl md:text-3xl font-black mb-3">Filter by country and city</h3>
              <p class="text-black text-lg md:text-xl opacity-50">Going abroad? Just choose your destination country and
                even book a session upfront, no more hassle!</p>
            </div>
          </div>
        </div>


        <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
          <!-- Feature Card 1 -->
          <div class="bg-[#181818] lg:col-start-2 p-6 flex flex-col rounded-[20px]">
            <div class="relative bg-[#0f0e0e] rounded-[20px] mb-6 overflow-hidden">
              <img class="w-full h-auto" src="@/public/landing/photoWrapper_1.png"
                   alt="Comprehensive card feature"/>
            </div>
            <div class="flex-grow">
              <h3 class="text-white text-2xl md:text-3xl font-black mb-3">Comprehensive card</h3>
              <p class="text-white text-lg md:text-xl opacity-50">See all useful information right at the studio card
                to
                decide what works for you</p>
            </div>
          </div>

          <!-- Feature Card 2 -->
          <div class="bg-[#181818] p-6 flex flex-col rounded-[20px]">
            <div class="relative bg-[#0f0e0e] rounded-[20px] mb-6 overflow-hidden">
              <img class="w-full h-auto" src="@/public/landing/photoWrapper_2.png"
                   alt="Use filters feature"/>
            </div>
            <div class="flex-grow">
              <h3 class="text-[#f7f7f7] text-2xl md:text-3xl font-black mb-3">Use filters!</h3>
              <p class="text-[#f7f7f7] text-lg md:text-xl opacity-50">We have many filters so you can find your best
                match</p>
            </div>
          </div>
        </div>


        <div class="flex flex-col lg:flex-row items-center gap-12">


          <!-- Feature Descriptions -->
          <div class="w-full lg:w-1/2 space-y-6">
            <!-- Feature 4 -->
            <div class="bg-[#f7f7f7] rounded-2xl p-6">
              <h3 class="text-black text-2xl md:text-3xl font-black mb-3">Map with all available studios</h3>
              <p class="text-black text-lg md:text-xl opacity-50">Such a dream, and it came through with our service!
                Travel and visit studios!</p>
            </div>

            <!-- Feature 5 -->
            <div class="bg-[#f7f7f7] rounded-2xl p-6">
              <h3 class="text-black text-2xl md:text-3xl font-black mb-3">Click to book</h3>
              <p class="text-black text-lg md:text-xl opacity-50">Just find studio near you and book it right away</p>
            </div>

            <!-- Feature 6 -->
            <div class="bg-[#f7f7f7] rounded-2xl p-6">
              <h3 class="text-black text-2xl md:text-3xl font-black mb-3">Don't forget to share with friend</h3>
              <p class="text-black text-lg md:text-xl opacity-50">Find studio in any country and city and send link to
                it to get special offers</p>
            </div>
          </div>


          <!-- Image Section -->
          <div class="w-full lg:w-1/2 relative">
            <img class="w-full h-auto" src="@/public/landing/studio_2.png"
                 alt="Feature Image 1"/>
          </div>
        </div>


        <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
          <!-- Feature Card 3 -->
          <div class="bg-[#181818] lg:col-start-2 p-6 flex flex-col rounded-[20px]">
            <div class="relative bg-[#0f0e0e] rounded-[20px] mb-6 overflow-hidden">
              <img class="w-full h-auto" src="@/public/landing/photoWrapper_3.png"
                   alt="Comprehensive card feature"/>
            </div>
            <div class="flex-grow">
              <h3 class="text-white text-2xl md:text-3xl font-black mb-3">Map card</h3>
              <p class="text-white text-lg md:text-xl opacity-50">See studio price right on the map</p>
            </div>
          </div>

          <!-- Feature Card 4 -->
          <div class="bg-[#181818] p-6 flex flex-col rounded-[20px]">
            <div class="relative bg-[#0f0e0e] rounded-[20px] mb-6 overflow-hidden">
              <img class="w-full h-auto" src="@/public/landing/photoWrapper_3.png"
                   alt="Use filters feature"/>
            </div>
            <div class="flex-grow">
              <h3 class="text-[#f7f7f7] text-2xl md:text-3xl font-black mb-3">Map card</h3>
              <p class="text-[#f7f7f7] text-lg md:text-xl opacity-50">See studio price right on the map</p>
            </div>
          </div>
        </div>

      </div>
    </div>
  </section>
</template>

<style scoped lang="scss">

</style>