import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import { createPinia } from "pinia";
import Buefy from "buefy";
import "@/assets/style.css";
import "buefy/dist/css/buefy.css";

const pinia = createPinia();

createApp(App).use(pinia).use(router).use(Buefy).mount("#app");
