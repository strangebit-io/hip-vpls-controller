import { createApp } from "vue";
import App from "./App.vue";
import "bootstrap/dist/css/bootstrap.min.css";
import "@/assets/css/main.css";
import router from "./router";

const app = createApp(App);
app.config.globalProperties["$BASE_URL"] = "http://localhost:5003";
app.use(router);
app.mount("#app");
