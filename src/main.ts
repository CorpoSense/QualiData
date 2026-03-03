import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import { createPinia } from "pinia";
import { createBootstrap } from "bootstrap-vue-next";
import "bootstrap/dist/css/bootstrap.css";
import "bootstrap-vue-next/dist/bootstrap-vue-next.css";
import "bootstrap-icons/font/bootstrap-icons.css";
import "bootstrap/dist/js/bootstrap.bundle.min.js";
import "@/assets/style.css";

const pinia = createPinia();
const bootstrap = createBootstrap();

createApp(App).use(pinia).use(router).use(bootstrap).mount("#app");
