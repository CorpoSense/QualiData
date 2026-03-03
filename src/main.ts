import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import { createPinia } from "pinia";
import { createBootstrap } from "bootstrap-vue-next";
import Buefy from "buefy";
import "bootstrap/dist/css/bootstrap.css";
import "bootstrap-vue-next/dist/bootstrap-vue-next.css";
import "bootstrap-icons/font/bootstrap-icons.css";
import "@/assets/style.css";
import "buefy/dist/css/buefy.css";

const pinia = createPinia();
const bootstrap = createBootstrap();

const app = createApp(App);
app.use(pinia);
app.use(router);
app.use(bootstrap);
app.use(Buefy, {
  defaultIconPack: "mdi",
  defaultInputHasCounter: false,
});
app.mount("#app");
