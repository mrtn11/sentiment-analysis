<script setup>
import { RouterLink, RouterView } from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'

</script>

<script>
import AudioUploader from './components/AudioUploader.vue';




export default {
  name: 'App',
  components: {
    AudioUploader
  }
}
</script>

<template>
  <div id="app">
    <audio-uploader></audio-uploader>
  </div>
</template>

