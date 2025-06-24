<template>
  <div>
    <h1>URL短縮</h1>
    <form @submit.prevent="shorten">
      <input v-model="url" type="text" placeholder="URLを入力" required />
      <input v-model.number="expire" type="number" placeholder="有効期限（分）" />
      <button type="submit">短縮</button>
    </form>
    <p v-if="shortUrl">短縮URL: <a :href="shortUrl" target="_blank">{{ shortUrl }}</a></p>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const url = ref('')
const expire = ref(10080)
const shortUrl = ref('')

const shorten = async () => {
  const res = await fetch('http://localhost:8000/shorten', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      url: url.value,
      expire_minutes: expire.value
    })
  })
  const data = await res.json()
  shortUrl.value = data.short_url
}
</script>
