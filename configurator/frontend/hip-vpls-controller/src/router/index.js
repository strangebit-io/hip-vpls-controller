import { createRouter, createWebHistory } from "vue-router";
import Devices from "../views/Devices.vue";
import Firewall from "../views/Firewall.vue";
import ACL from "../views/ACL.vue";
import Mesh from "../views/Mesh.vue";
import Shaper from "../views/Shaper.vue";
import About from "../views/About.vue";

const routes = [
  {
    path: "/devices",
    name: "HIP Switch status",
    component: Devices,
  },
  {
    path: "/firewall",
    name: "HIP firewall",
    component: Firewall,
  },
  {
    path: "/acl",
    name: "MAC based ACL",
    component: ACL,
  },
  {
    path: "/mesh",
    name: "HIP mesh",
    component: Mesh,
  },
  {
    path: "/shaper",
    name: "Traffic shaper",
    component: Shaper,
  },
  {
    path: "/about",
    name: "About",
    component: About,
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

router.replace({ path: "*", redirect: "/" });

export default router;
