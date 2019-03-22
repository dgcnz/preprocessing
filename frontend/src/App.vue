<template>
  <div id="app" class="center">
    <router-view/>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
    @import url('https://fonts.googleapis.com/css?family=Inconsolata');

    .code {
        font-family: 'Inconsolata', monospace;
    }
    .disabledContent
    {
        cursor: not-allowed;
        background-color: rgb(229, 229, 229) !important;
    }

    .disabledContent > *
    {
        pointer-events:none;
    }
    .box {
      padding: 5px 10px;
      border-radius: 5px;
      border: 1px solid #2c3e50;
      max-width: 640px;
    }
    .center {
      margin: auto;
      width: 50%;
      padding: 10px;
    }

    #app {
      font-family: 'Avenir', Helvetica, Arial, sans-serif;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      text-align: center;
      color: #2c3e50;
      margin-top: 30px;
      max-width: 640px;
    }
</style>
