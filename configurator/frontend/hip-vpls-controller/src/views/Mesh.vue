<template>
  <div class="main_content">
    <OkModal
      v-bind:header="header"
      v-bind:message="message"
      v-if="showModal"
      v-on:confirm="closeModal"
    />
    <Spinner v-if="showSpinner" />
    <div class="mesh">
      <div style="font-weight: bold; text-align: center; width: 100%">
        <table
          class="table"
          style="font-weight: bold; text-align: center; width: 100%"
        >
          <thead>
            <tr>
              <th scope="col">HIT 1</th>
              <th scope="col">HIT 2</th>
              <th scope="col">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="m in mesh" v-bind:key="m.id">
              <th>{{ getDeviceName(m.device_1_id) }}</th>
              <td>{{ getDeviceName(m.device_2_id) }}</td>
              <td>
                <button
                  @click="removeMeshRecord(m.id)"
                  class="btn btn-dark btn-lg btn-block btn-add"
                >
                  <!-- BootstrapIcon icon="crosshair" size="1x" / -->
                  Remove record
                </button>
              </td>
            </tr>
            <tr>
              <td>
                <select
                  class="form-select form-control-lg"
                  v-model="selectedHIT1Id"
                  aria-label="First HIT"
                >
                  <option
                    v-for="device in devices"
                    v-bind:value="device.id"
                    v-bind:key="device.id"
                  >
                    {{ device.name }}
                  </option>
                </select>
              </td>
              <td>
                <select
                  class="form-select form-control-lg"
                  v-model="selectedHIT2Id"
                  aria-label="First HIT"
                >
                  <option
                    v-for="device in devices"
                    v-bind:value="device.id"
                    v-bind:key="device.id"
                  >
                    {{ device.name }}
                  </option>
                </select>
              </td>
              <td>
                <button
                  @click="addMeshRecord"
                  class="btn btn-dark btn-lg btn-block btn-add"
                >
                  <!-- BootstrapIcon icon="building-add" size="1x" / -->
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
      devices: [],
      mesh: [],
    };
  },
  methods: {
    closeModal() {
      this.showModal = false;
    },
    removeMeshRecord(id) {
      const token = sessionStorage.getItem("token");
      const headers = {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      };
      const url = this.$BASE_URL + "/api/delete_mesh/";
      axios.post(url, { id: id }, { headers }).then((response) => {
        this.showSpinner = false;
        if (!response.data[0].auth_fail) {
          this.getMesh();
        } else {
          this.showModal = true;
        }
      });
    },
    addMeshRecord() {
      const token = sessionStorage.getItem("token");
      const headers = {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      };
      const url = this.$BASE_URL + "/api/add_mesh/";
      axios
        .post(
          url,
          {
            device_1_id: this.selectedHIT1Id,
            device_2_id: this.selectedHIT2Id,
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
              this.getMesh();
            }
          } else {
            this.showModal = true;
          }
        });
    },
    getMesh() {
      const token = sessionStorage.getItem("token");
      const headers = {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      };
      const url = this.$BASE_URL + "/api/get_mesh/";
      axios.post(url, {}, { headers }).then((response) => {
        this.showSpinner = false;
        if (!response.data[0].auth_fail) {
          this.mesh = JSON.parse(JSON.stringify(response.data[0].result));
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
          this.getMesh();
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
.mesh {
  width: 100%;
  height: 100%;
  float: left;
  margin-left: 0px;
  margin-right: 0px;
}
</style>
