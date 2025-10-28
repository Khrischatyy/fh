<template>
  <div>
    <div class="date">{{ formattedDate }}</div>
    <DatePicker :date="date" @dateChange="dateChanged" />
    <button class="reset" @click="resetDate">Reset Date</button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import {DatePicker} from '~/src/features/DatePicker';

const date = ref(new Date());
const emit = defineEmits(['dateChange']);
const formattedDate = computed(() => {
  const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec'];
  return `${date.value.getDate()} ${MONTHS[date.value.getMonth()]} ${date.value.getFullYear()}`;
});

const resetDate = () => {
  date.value = new Date();
};

const dateChanged = (newDate) => {
  date.value = newDate;
  emit('dateChange', newDate);
};
</script>

<style>
.center {
  text-align: center;
  font: 16px 'Roboto', sans-serif;
}

.date {
  font-size: 30px;
  font-weight: 300;
}

.date-picker {
  display: flex;
  padding: 50px 20px;
  margin: 30px 0;
  overflow: hidden;
  width: 100%;
  background: white;
}

.day,
.month,
.year {
  position: relative;
  height: 50px;
  margin: 0px;
  border-top: 1px solid #e0e0e0;
  border-bottom: 1px solid #e0e0e0;
  border-radius: 0;
}

.day::before,
.day::after,
.month::before,
.month::after,
.year::before,
.year::after {
  content: '';
  position: absolute;
  left: 0;
  width: 80px;
  height: 50px;
  background-color: white;
  opacity: 0.8;
  pointer-events: none;
  z-index: 1;
}

.day::before,
.month::before,
.year::before {
  top: -51px;
}

.day::after,
.month::after,
.year::after {
  bottom: -51px;
}

li {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 80px;
  height: 50px;
  user-select: none;
}

.reset {
  width: 100px;
  height: 30px;
  border-radius: 15px;
  border: none;
  display: none;
  outline: none;
  color: white;
  background-color: #2466fb;
  box-shadow: 0 1px 10px -2px #2466fb;
  font-weight: 300;
}

.reset:active {
  transform: scale(0.95);
}
</style>
