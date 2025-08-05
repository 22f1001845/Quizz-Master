<template>
    <div id="app">
        

        <router-view />
    </div>
</template>

<style>
#app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    color: #2c3e50;
}

nav {
    padding: 20px;
    background-color: #f5f5f5;
}

nav a {
    margin: 0 10px;
    font-weight: bold;
    color: #333;
    text-decoration: none;
}

nav a.router-link-exact-active {
    color: #42b983;
}
</style>
