<template>
  <div class="main_content">
    <OkModal
      v-bind:header="header"
      v-bind:message="message"
      v-if="showModal"
      v-on:confirm="closeModal"
    />
    <Spinner v-if="showSpinner" />
    <div class="acl">
      <div>
        <span style="font-weight: bold; vertical-align: center"
          >Change device</span
        >
        <select
          class="form-select form-control-lg"
          style="width: 90%; float: right"
          v-model="selectedDeviceId"
          @change="changeDevice($event)"
          aria-label="Device"
        >
          <option
            v-for="device in devices"
            v-bind:value="device.id"
            v-bind:key="device.id"
          >
            {{ device.name }}
          </option>
        </select>
      </div>

      <div style="font-weight: bold; text-align: center; width: 100%">
        <table
          class="table"
          style="font-weight: bold; text-align: center; width: 100%"
        >
          <thead>
            <tr>
              <th scope="col">Source MAC</th>
              <th scope="col">Destination MAC</th>
              <th scope="col">Rule</th>
              <th scope="col">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in rules" v-bind:key="r.id">
              <th>{{ prepareMac(r.mac1) }}</th>
              <td>{{ prepareMac(r.mac2) }}</td>
              <td>{{ r.rule }} {{ r.id }} </td>
              <td>
                <button
                  @click="removeRecord(r.id)"
                  class="btn btn-dark btn-lg btn-block btn-add"
                >
                  <!-- BootstrapIcon icon="crosshair" size="1x" / -->
                  Remove record
                </button>
              </td>
            </tr>
            <tr>
              <td>
                <input
                  type="text"
                  class="form-control form-control-lg"
                  style="display: inline; width: calc(100%)"
                  v-model="source_mac"
                />
              </td>
              <td>
                <input
                  type="text"
                  class="form-control form-control-lg"
                  style="display: inline; width: calc(100%)"
                  v-model="destination_mac"
                />
              </td>
              <td>
                <select
                  class="form-select form-control-lg"
                  v-model="selectedRule"
                  aria-label="Rule"
                >
                  <option
                    v-for="rule in rules_"
                    v-bind:value="rule.rule"
                    v-bind:key="rule.rule"
                  >
                    {{ rule.name }}
                  </option>
                </select>
              </td>
              <td>
                <button
                  @click="addRecord"
                  class="btn btn-dark btn-lg btn-block btn-add"
                >
                  Add record
                </button>
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
//import BootstrapIcon from "@dvuckovic/vue3-bootstrap-icons";

export default {
  name: "Devices",
  data() {
    return {
      showSpinner: true,
      header: "Authentication error",
      message: "Try again later after authorizing",
      showModal: false,
      loaded: true,
      selectedHIT1Id: null,
      selectedHIT2Id: null,
      selectedDeviceId: null,
      destination_mac: "",
      source_mac: "",
      devices: [],
      rules: [],
      rules_: [
        { rule: "allow", name: "ALLOW" },
        { rule: "deny", name: "DENY" },
      ],
    };
  },
  methods: {
    prepareMac(mac) {
      var out = ""
      for (var i = 0; i < 12; i+=2) {
        if (i < 10) {
          out += mac[i] + mac[i+1] + ":";
        } else {
          out += mac[i] + mac[i+1]
        }
      }
      return out;
    },
    closeModal() {
      this.showModal = false;
    },
    changeDevice() {
      this.getRecords();
    },
    removeRecord(id) {
      const token = sessionStorage.getItem("token");
      const headers = {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      };
      const url = this.$BASE_URL + "/api/delete_acl_record/";
      axios.post(url, { id: id }, { headers }).then((response) => {
        this.showSpinner = false;
        if (!response.data[0].auth_fail) {
          this.getRecords();
        } else {
          this.showModal = true;
        }
      });
    },
    addRecord() {
      const token = sessionStorage.getItem("token");
      const headers = {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      };
      const url = this.$BASE_URL + "/api/add_acl_record/";
      axios
        .post(
          url,
          {
            device_id: this.selectedDeviceId,
            source_mac: this.source_mac,
            destination_mac: this.destination_mac,
            rule: this.selectedRule,
          },
          { headers }
        )
        .then((response) => {
          this.showSpinner = false;
          if (!response.data[0].auth_fail) {
            if (!response.data[0].result) {
              this.message = response.data[0].reason;
              this.showModal = true;
            } else {
              this.getRecords();
            }
          } else {
            this.showModal = true;
          }
        });
    },
    getRecords() {
      const token = sessionStorage.getItem("token");
      const headers = {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      };
      const url = this.$BASE_URL + "/api/get_acl/";
      axios
        .post(url, { device_id: this.selectedDeviceId }, { headers })
        .then((response) => {
          this.showSpinner = false;
          if (!response.data[0].auth_fail) {
            this.rules = JSON.parse(JSON.stringify(response.data[0].result));
          } else {
            this.showModal = true;
          }
        });
    },
    getDevices() {
      const token = sessionStorage.getItem("token");
      const headers = {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      };
      const url = this.$BASE_URL + "/api/get_devices/";
      axios.post(url, {}, { headers }).then((response) => {
        if (!response.data[0].auth_fail) {
          this.devices = JSON.parse(JSON.stringify(response.data[0].result));
          if (this.devices.length > 0) {
            this.selectedDeviceId = this.devices[0].id;
          }
          this.getRecords();
        } else {
          this.showModal = true;
        }
      });
    },
    getDeviceName(id) {
      for (var i in this.devices) {
        if (this.devices[i].id == id) {
          return this.devices[i].name;
        }
      }
      return "NOT FOUND";
    },
  },
  components: {
    OkModal,
    Spinner,
    //BootstrapIcon
  },
  mounted() {
    this.getDevices();
  },
};
</script>

<style scoped>
.acl {
  width: 100%;
  height: 100%;
  float: left;
  margin-left: 0px;
  margin-right: 0px;
}
span {
  min-height: 40px;
  display: inline-flex;
  align-items: center;
}
</style>
