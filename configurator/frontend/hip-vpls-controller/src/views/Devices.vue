<template>
  <div class="main_content">
    <OkModal
      v-bind:header="header"
      v-bind:message="message"
      v-if="showModal"
      v-on:confirm="closeModal"
    />
    <Spinner v-if="showSpinner" />
    <div class="devices">
      <div style="font-weight: bold; text-align: center; width: 100%">
        <table
          class="table"
          style="font-weight: bold; text-align: center; width: 100%"
        >
          <thead>
            <tr>
              <th scope="col">HIT</th>
              <th scope="col">IP</th>
              <th scope="col">Name</th>
              <th scope="col">Last seen</th>
              <th scope="col">Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="device in devices" v-bind:key="device.id">
              <th scope="row">{{ device.hit }}</th>
              <td>{{ device.ip }}</td>
              <td>{{ device.name }}</td>
              <td>{{ new Date(device.timestamp * 1000) }}</td>
              <td>
                <span
                  v-if="
                    new Date().getTime() - device.timestamp * 1000 < 10 * 1000
                  "
                  style="background-color: #0cff00"
                  >Online</span
                >
                <span
                  v-if="
                    new Date().getTime() - device.timestamp * 1000 >= 10 * 1000
                  "
                  style="background-color: #ff5454"
                  >Offline</span
                >
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import OkModal from "../components/OkModal.vue";
import Spinner from "../components/Spinner.vue";

export default {
  name: "Devices",
  data() {
    return {
      showSpinner: true,
      header: "Authentication error",
      message: "Try again later after authorizing",
      showModal: false,
      loaded: true,
      devices: [],
    };
  },
  methods: {
    closeModal() {
      this.showModal = false;
    },
    getDevices() {
      const token = sessionStorage.getItem("token");
      const headers = {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      };
      const url = this.$BASE_URL + "/api/get_devices/";
      axios.post(url, {}, { headers }).then((response) => {
        this.showSpinner = false;
        if (!response.data[0].auth_fail) {
          this.devices = JSON.parse(JSON.stringify(response.data[0].result));
        } else {
          this.showModal = true;
        }
      });
    },
  },
  components: {
    OkModal,
    Spinner,
  },
  mounted() {
    this.getDevices();
  },
};
</script>

<style scoped>
.devices {
  width: 100%;
  height: 100%;
  float: left;
  display: inline;
  margin-left: 0px;
  margin-right: 0px;
}
</style>
