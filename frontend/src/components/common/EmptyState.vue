<script setup>
import BaseButton from './BaseButton.vue'

const props = defineProps({
  icon: {
    type: [Object, String],
    required: true
  },
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  },
  actionText: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['action'])

const handleAction = () => {
  emit('action')
}
</script>

<template>
  <div class="flex flex-col items-center justify-center py-16 px-4 text-center">
    <!-- Icon -->
    <div class="w-20 h-20 rounded-full bg-muted flex items-center justify-center mb-6">
      <component :is="icon" class="w-10 h-10 text-muted-foreground" />
    </div>

    <!-- Title -->
    <h3 class="text-xl font-semibold text-foreground mb-2">{{ title }}</h3>

    <!-- Description -->
    <p v-if="description" class="text-muted-foreground max-w-md mb-6 leading-relaxed">
      {{ description }}
    </p>

    <!-- Action Button -->
    <BaseButton
      v-if="actionText"
      variant="default"
      size="lg"
      class="shadow-md"
      @click="handleAction"
    >
      {{ actionText }}
    </BaseButton>
  </div>
</template>
