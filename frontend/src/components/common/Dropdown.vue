<script setup>
import { ref, provide, onMounted, onUnmounted } from 'vue'
import { cn } from '@/utils/cn'

const props = defineProps({
  class: String
})

const isOpen = ref(false)
const dropdownRef = ref(null)

const toggle = () => isOpen.value = !isOpen.value
const close = () => isOpen.value = false

provide('closeDropdown', close)

const handleClickOutside = (event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    close()
  }
}

onMounted(() => document.addEventListener('click', handleClickOutside))
onUnmounted(() => document.removeEventListener('click', handleClickOutside))
</script>

<template>
  <div ref="dropdownRef" class="relative inline-block text-left">
    <div @click="toggle">
      <slot name="trigger" />
    </div>

    <Transition enter-active-class="transition ease-out duration-100" enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100" leave-active-class="transition ease-in duration-75"
      leave-from-class="transform opacity-100 scale-100" leave-to-class="transform opacity-0 scale-95">
      <div v-if="isOpen"
        :class="cn('absolute right-0 z-[9999] mt-2 w-56 origin-top-right rounded-md border bg-popover p-1 text-popover-foreground shadow-md outline-none', props.class)">
        <slot />
      </div>
    </Transition>
  </div>
</template>

<script>
import DropdownItem from './DropdownItem.vue'
import DropdownSeparator from './DropdownSeparator.vue'
import DropdownLabel from './DropdownLabel.vue'

export { DropdownItem, DropdownSeparator, DropdownLabel }
</script>
